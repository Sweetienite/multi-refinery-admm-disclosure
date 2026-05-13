"""
admm_capacity_sharing.py — ADMM capacity-sharing distributed approximation.

Implements the ADMM decomposition for two-refinery coordination via a shared
system capacity constraint.  Each refinery solves its own sub-problem given
a capacity allocation z_i; a coordinator updates the consensus split.

The shared resource is the total system production capacity (sum of all
fv_max values, = 8.15 kt in the paper case).

Each plant subproblem:
    maximize  sum(price_s * f_s)   for s in plant_streams
    subject to:
        fv_min_s <= f_s <= coord_ub_s          (stream bounds)
        sum(f_s) <= z_i                         (capacity allocation)
    augmented by: + lambda_i * y_i + (rho/2) * (y_i - z_consensus)^2
    where y_i = sum(f_s) is the plant's local capacity usage.

Revenue is scaled by ``profit_scale`` to improve ADMM numerical conditioning.

Main entry point: ``run_admm``
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import pyomo.environ as pyo

from src.centralized_lp import RefineryParams, CoordinationSpec


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ADMMParams:
    """ADMM hyper-parameters."""
    rho: float = 0.10          # Augmented Lagrangian penalty
    max_iter: int = 500
    primal_tol: float = 1e-3   # Primal residual convergence threshold
    dual_tol: float = 1e-3     # Dual residual convergence threshold
    profit_scale: float = 1e6  # Profit normalisation factor (divide revenue by this)


@dataclass
class ADMMHistory:
    """Convergence history collected during ADMM iterations."""
    primal_residuals: list[float] = field(default_factory=list)
    dual_residuals: list[float] = field(default_factory=list)
    total_profits: list[float] = field(default_factory=list)
    # Per-iteration capacity allocations (y_A, y_B)
    allocations_a: list[float] = field(default_factory=list)
    allocations_b: list[float] = field(default_factory=list)
    iterations: int = 0


@dataclass
class ADMMResult:
    """Output of ADMM solve."""
    status: str             # "converged" | "max_iter"
    total_profit: float     # System-level approximate profit (CNY)
    profit_a: float         # Plant A profit (CNY)
    profit_b: float         # Plant B profit (CNY)
    allocation_a: float     # Plant A final consensus capacity allocation (kt)
    allocation_b: float     # Plant B final consensus capacity allocation (kt)
    iterations: int
    final_primal_residual: float
    final_dual_residual: float
    history: ADMMHistory = field(default_factory=ADMMHistory)


# ---------------------------------------------------------------------------
# Sub-problem: single-refinery LP with augmented Lagrangian penalty
# ---------------------------------------------------------------------------

def _get_solver() -> pyo.SolverFactory:
    s = pyo.SolverFactory("appsi_highs")
    if s.available(exception_flag=False):
        return s
    return pyo.SolverFactory("highs")


def _solve_subproblem(
    params: RefineryParams,
    coord_ub_multiplier: float,
    z_consensus: float,   # current global consensus capacity allocation
    lambda_k: float,      # dual multiplier for this plant
    rho: float,
    profit_scale: float,
) -> tuple[float, float]:
    """
    Solve single-refinery sub-problem with ADMM augmented Lagrangian term.

    Returns (local_capacity_usage_kt, local_profit_CNY).
    """
    streams = sorted(params.price)
    m = pyo.ConcreteModel()
    m.S = pyo.Set(initialize=streams)
    m.f = pyo.Var(m.S, within=pyo.NonNegativeReals)

    for s in streams:
        m.f[s].setlb(params.flow_min.get(s, 0.0))
        m.f[s].setub(coord_ub_multiplier * params.flow_max[s])

    # Local capacity usage
    local_cap = sum(m.f[s] for s in streams)

    # Objective: (scaled revenue) - dual penalty - proximal term
    revenue_scaled = sum(params.price[s] / profit_scale * m.f[s] for s in streams)
    penalty = lambda_k * local_cap + (rho / 2.0) * (local_cap - z_consensus) ** 2

    m.obj = pyo.Objective(expr=revenue_scaled - penalty, sense=pyo.maximize)

    solver = _get_solver()
    solver.solve(m)

    profit = sum(
        params.price[s] * float(pyo.value(m.f[s])) for s in streams
    )
    alloc = float(pyo.value(sum(m.f[s] for s in streams)))
    return alloc, profit


# ---------------------------------------------------------------------------
# ADMM coordinator
# ---------------------------------------------------------------------------

def run_admm(
    params_a: RefineryParams,
    params_b: RefineryParams,
    coord: Optional[CoordinationSpec] = None,
    admm_params: Optional[ADMMParams] = None,
) -> ADMMResult:
    """
    Run ADMM capacity-sharing for two refineries.

    The shared constraint is: y_A + y_B <= total_system_capacity
    where y_i is each refinery's local total flow (capacity usage).

    The z-update projects the average onto [0, total_system_capacity].

    Returns an ADMMResult with convergence statistics.
    """
    if coord is None:
        coord = CoordinationSpec()
    if admm_params is None:
        admm_params = ADMMParams()

    rho = admm_params.rho
    scale = admm_params.profit_scale
    mult = coord.coord_ub_multiplier

    total_cap = coord.total_system_capacity
    if total_cap is None:
        total_cap = (sum(params_a.flow_max[s] for s in params_a.flow_max)
                     + sum(params_b.flow_max[s] for s in params_b.flow_max))

    # Initialise
    lambda_a, lambda_b = 0.0, 0.0
    z = total_cap / 2.0
    history = ADMMHistory()
    profit_a = profit_b = 0.0
    y_a = y_b = 0.0

    for k in range(admm_params.max_iter):
        # x-updates
        y_a, profit_a = _solve_subproblem(params_a, mult, z, lambda_a, rho, scale)
        y_b, profit_b = _solve_subproblem(params_b, mult, z, lambda_b, rho, scale)

        z_prev = z
        # z-update: soft projection ensuring y_A + y_B <= total_cap
        # z_i = (y_i - lambda_i / rho)  subject to z_A + z_B = total_cap,  z_i >= 0
        z_a_unconstrained = y_a - lambda_a / rho
        z_b_unconstrained = y_b - lambda_b / rho
        # Projection: split capacity optimally (water-filling)
        slack = total_cap - (z_a_unconstrained + z_b_unconstrained)
        if slack >= 0:
            z_a_new = z_a_unconstrained
            z_b_new = z_b_unconstrained
        else:
            z_a_new = z_a_unconstrained + slack / 2.0
            z_b_new = z_b_unconstrained + slack / 2.0
        z_a_new = max(0.0, z_a_new)
        z_b_new = max(0.0, z_b_new)
        # Use average as scalar consensus for symmetric update
        z = (z_a_new + z_b_new) / 2.0

        # Dual updates
        lambda_a = lambda_a + rho * (y_a - z)
        lambda_b = lambda_b + rho * (y_b - z)

        # Residuals
        primal_res = math.sqrt((y_a - z) ** 2 + (y_b - z) ** 2)
        dual_res = math.sqrt(2.0) * rho * abs(z - z_prev)

        history.primal_residuals.append(primal_res)
        history.dual_residuals.append(dual_res)
        history.total_profits.append(profit_a + profit_b)
        history.allocations_a.append(y_a)
        history.allocations_b.append(y_b)

        if primal_res <= admm_params.primal_tol and dual_res <= admm_params.dual_tol:
            history.iterations = k + 1
            return ADMMResult(
                status="converged",
                total_profit=profit_a + profit_b,
                profit_a=profit_a,
                profit_b=profit_b,
                allocation_a=y_a,
                allocation_b=y_b,
                iterations=k + 1,
                final_primal_residual=primal_res,
                final_dual_residual=dual_res,
                history=history,
            )

    history.iterations = admm_params.max_iter
    return ADMMResult(
        status="max_iter",
        total_profit=profit_a + profit_b,
        profit_a=profit_a,
        profit_b=profit_b,
        allocation_a=y_a,
        allocation_b=y_b,
        iterations=admm_params.max_iter,
        final_primal_residual=history.primal_residuals[-1] if history.primal_residuals else float("inf"),
        final_dual_residual=history.dual_residuals[-1] if history.dual_residuals else float("inf"),
        history=history,
    )

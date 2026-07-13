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
Each sub-problem is a convex QP solved via scipy SLSQP.

Main entry point: ``run_admm``
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from scipy.optimize import minimize as _scipy_minimize

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
# Sub-problem: single-refinery QP with augmented Lagrangian penalty
# ---------------------------------------------------------------------------

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

    The augmented Lagrangian penalty contains a quadratic proximal term
    ``(rho/2) * (y - z)^2`` which makes each sub-problem a convex QP.
    We solve it with scipy SLSQP, which is bundled with scipy (already a
    project dependency) and does not require an external QP solver.

    Returns (local_capacity_usage_kt, local_profit_CNY).
    """
    streams = sorted(params.price)
    prices = np.array([params.price[s] for s in streams], dtype=float)
    lb = np.array([params.flow_min.get(s, 0.0) for s in streams], dtype=float)
    ub = np.array([coord_ub_multiplier * params.flow_max[s] for s in streams], dtype=float)

    def neg_lagrangian(f: np.ndarray) -> float:
        y = float(f.sum())
        revenue_scaled = float((prices / profit_scale).dot(f))
        penalty = lambda_k * y + (rho / 2.0) * (y - z_consensus) ** 2
        return -(revenue_scaled - penalty)

    bounds = list(zip(lb.tolist(), ub.tolist()))
    # Initialise at lower bounds (feasible starting point)
    f0 = lb.copy()
    result = _scipy_minimize(
        neg_lagrangian, f0, method="SLSQP",
        bounds=bounds,
        options={"ftol": 1e-10, "maxiter": 1000},
    )
    f_opt = np.clip(result.x, lb, ub)
    profit = float(prices.dot(f_opt))
    alloc = float(f_opt.sum())
    return alloc, profit


def _profit_at_capacity(
    params: RefineryParams,
    coord_ub_multiplier: float,
    capacity: float,
) -> float:
    """Evaluate the feasible local revenue at a consensus capacity allocation."""
    streams = sorted(params.price, key=params.price.get, reverse=True)
    flow = {stream: params.flow_min.get(stream, 0.0) for stream in streams}
    remaining = max(0.0, capacity - sum(flow.values()))
    for stream in streams:
        upper = coord_ub_multiplier * params.flow_max[stream]
        add = min(max(0.0, upper - flow[stream]), remaining)
        flow[stream] += add
        remaining -= add
        if remaining <= 1e-12:
            break
    return float(sum(params.price[stream] * flow[stream] for stream in streams))


def _project_capacity_split(values: np.ndarray, total_capacity: float) -> np.ndarray:
    """Project a two-refinery allocation onto ``z >= 0, sum(z) <= capacity``.

    The ADMM consensus variable has one component per refinery.  Keeping these
    components separate is essential: reducing them to a single average can
    make both local subproblems converge to zero production even when the
    joint capacity is feasible.
    """
    clipped = np.maximum(values, 0.0)
    if float(clipped.sum()) <= total_capacity:
        return clipped

    # Euclidean projection onto the two-dimensional simplex.  The generic
    # threshold construction also makes the intended constraint explicit.
    ordered = np.sort(values)[::-1]
    cumulative = np.cumsum(ordered)
    rho = np.nonzero(ordered - (cumulative - total_capacity) /
                     np.arange(1, len(values) + 1) > 0)[0][-1]
    threshold = (cumulative[rho] - total_capacity) / (rho + 1)
    return np.maximum(values - threshold, 0.0)


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

    The z-update projects the two-refinery consensus allocation onto the
    non-negative shared-capacity simplex.

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

    # Initialise one consensus allocation and multiplier per refinery.
    lambda_a, lambda_b = 0.0, 0.0
    z_a = z_b = total_cap / 2.0
    history = ADMMHistory()
    profit_a = profit_b = 0.0
    y_a = y_b = 0.0

    for k in range(admm_params.max_iter):
        # x-updates
        y_a, profit_a = _solve_subproblem(params_a, mult, z_a, lambda_a, rho, scale)
        y_b, profit_b = _solve_subproblem(params_b, mult, z_b, lambda_b, rho, scale)

        z_prev = np.array([z_a, z_b], dtype=float)
        # z-update: minimise the augmented Lagrangian over the shared-capacity
        # set.  For L = f(y) + lambda*(y-z) + rho/2*(y-z)^2, the unconstrained
        # minimiser is y + lambda/rho; project it onto the feasible split.
        z_a, z_b = _project_capacity_split(
            np.array([y_a + lambda_a / rho, y_b + lambda_b / rho]), total_cap
        )

        # Dual updates
        lambda_a = lambda_a + rho * (y_a - z_a)
        lambda_b = lambda_b + rho * (y_b - z_b)

        # Residuals
        primal_res = math.sqrt((y_a - z_a) ** 2 + (y_b - z_b) ** 2)
        dual_res = rho * float(np.linalg.norm(np.array([z_a, z_b]) - z_prev))

        history.primal_residuals.append(primal_res)
        history.dual_residuals.append(dual_res)
        history.total_profits.append(profit_a + profit_b)
        history.allocations_a.append(y_a)
        history.allocations_b.append(y_b)

        if primal_res <= admm_params.primal_tol and dual_res <= admm_params.dual_tol:
            history.iterations = k + 1
            # The x-updates can be marginally outside the shared-capacity set
            # before the primal residual reaches zero. Report the objective at
            # the feasible consensus allocation, not at that transient point.
            feasible_profit_a = _profit_at_capacity(params_a, mult, float(z_a))
            feasible_profit_b = _profit_at_capacity(params_b, mult, float(z_b))
            return ADMMResult(
                status="converged",
                total_profit=feasible_profit_a + feasible_profit_b,
                profit_a=feasible_profit_a,
                profit_b=feasible_profit_b,
                allocation_a=float(z_a),
                allocation_b=float(z_b),
                iterations=k + 1,
                final_primal_residual=primal_res,
                final_dual_residual=dual_res,
                history=history,
            )

    history.iterations = admm_params.max_iter
    feasible_profit_a = _profit_at_capacity(params_a, mult, float(z_a))
    feasible_profit_b = _profit_at_capacity(params_b, mult, float(z_b))
    return ADMMResult(
        status="max_iter",
        total_profit=feasible_profit_a + feasible_profit_b,
        profit_a=feasible_profit_a,
        profit_b=feasible_profit_b,
        allocation_a=float(z_a),
        allocation_b=float(z_b),
        iterations=admm_params.max_iter,
        final_primal_residual=history.primal_residuals[-1] if history.primal_residuals else float("inf"),
        final_dual_residual=history.dual_residuals[-1] if history.dual_residuals else float("inf"),
        history=history,
    )

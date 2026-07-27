"""
centralized_lp.py — Centralized reference LP model for multi-refinery coordination.

Model description (matching the paper):
  Two refineries A and B each operate a set of production streams.
  Each stream s has a product price p_s (CNY/kt) and flow bounds [fv_min_s, fv_max_s].

  Standalone solve:
    Each plant maximises revenue = sum(p_s * f_s) subject to:
      fv_min_s <= f_s <= fv_max_s  for each stream
      sum(f_s) <= plant_capacity   (plant capacity = sum(fv_max) for its streams)

  Coordinated solve (centralized reference):
    Both plants are solved jointly. Each stream's upper bound is relaxed to
    coord_ub_s = coord_ub_multiplier * fv_max_s (default: 2.0).
    A joint system capacity constraint is imposed:
      sum(f_s, all streams) <= total_system_capacity

    This allows capacity to be reallocated across plants to maximize total revenue.

Requires: pyomo, highspy (or any HiGHS-compatible solver).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import pyomo.environ as pyo


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class RefineryParams:
    """Single-refinery production parameters."""
    name: str
    # Net revenue per stream (product price, CNY/kt). Positive = income.
    price: dict[str, float]
    # Minimum flow constraint (fv_min), kt/period
    flow_min: dict[str, float]
    # Maximum flow constraint (fv_max), kt/period
    flow_max: dict[str, float]


@dataclass
class CoordinationSpec:
    """Specification of the coordinated planning structure."""
    # Upper-bound multiplier for coordinated model (default 2.0 = double fv_max)
    coord_ub_multiplier: float = 2.0
    # Total system capacity (kt/period) shared across all streams
    # Defaults to sum(fv_max) across both plants if not set
    total_system_capacity: Optional[float] = None


@dataclass
class CentralizedResult:
    """Output of the centralized LP solve."""
    status: str                      # "optimal" | "infeasible" | "unknown"
    total_profit: float              # System-level joint profit (CNY)
    profit_a: float                  # Refinery A revenue under coordinated plan
    profit_b: float                  # Refinery B revenue under coordinated plan
    flows_a: dict[str, float]        # Optimal flows for A streams (stream -> kt)
    flows_b: dict[str, float]        # Optimal flows for B streams (stream -> kt)
    standalone_profit_a: float = 0.0
    standalone_profit_b: float = 0.0


# ---------------------------------------------------------------------------
# Helper: get solver
# ---------------------------------------------------------------------------

def _get_solver() -> pyo.SolverFactory:
    s = pyo.SolverFactory("appsi_highs")
    if s.available(exception_flag=False):
        return s
    return pyo.SolverFactory("highs")


# ---------------------------------------------------------------------------
# Standalone solve (single refinery, no exchange)
# ---------------------------------------------------------------------------

def solve_standalone(params: RefineryParams) -> tuple[float, dict[str, float]]:
    """
    Solve single-refinery LP.

    Returns (optimal_profit_CNY, optimal_flows).
    """
    streams = sorted(params.price)
    plant_capacity = sum(params.flow_max[s] for s in streams)

    m = pyo.ConcreteModel()
    m.S = pyo.Set(initialize=streams)
    m.f = pyo.Var(m.S, within=pyo.NonNegativeReals)

    for s in streams:
        m.f[s].setlb(params.flow_min.get(s, 0.0))
        m.f[s].setub(params.flow_max[s])

    # System capacity constraint
    m.cap = pyo.Constraint(expr=sum(m.f[s] for s in streams) <= plant_capacity)

    m.obj = pyo.Objective(
        expr=sum(params.price[s] * m.f[s] for s in streams),
        sense=pyo.maximize,
    )

    solver = _get_solver()
    result = solver.solve(m)

    if result.solver.termination_condition == pyo.TerminationCondition.optimal:
        profit = float(pyo.value(m.obj))
        flows = {s: float(pyo.value(m.f[s])) for s in streams}
        return profit, flows
    return 0.0, {s: 0.0 for s in streams}


# ---------------------------------------------------------------------------
# Joint centralized solve
# ---------------------------------------------------------------------------

def solve_centralized(
    params_a: RefineryParams,
    params_b: RefineryParams,
    coord: Optional[CoordinationSpec] = None,
) -> CentralizedResult:
    """
    Solve the joint centralized LP for refineries A and B.

    In the coordinated model:
    - Each stream s can be produced up to coord_ub_multiplier * fv_max_s
    - Total production across both plants must not exceed total_system_capacity
      (= sum of all fv_max values if not specified)

    Returns a CentralizedResult with total_profit, per-plant profits, and flows.
    """
    if coord is None:
        coord = CoordinationSpec()

    standalone_a, _ = solve_standalone(params_a)
    standalone_b, _ = solve_standalone(params_b)

    streams_a = sorted(params_a.price)
    streams_b = sorted(params_b.price)

    cap_total = coord.total_system_capacity
    if cap_total is None:
        cap_total = (sum(params_a.flow_max[s] for s in streams_a)
                     + sum(params_b.flow_max[s] for s in streams_b))

    m = pyo.ConcreteModel(name="centralized")
    m.SA = pyo.Set(initialize=streams_a)
    m.SB = pyo.Set(initialize=streams_b)
    m.fa = pyo.Var(m.SA, within=pyo.NonNegativeReals)
    m.fb = pyo.Var(m.SB, within=pyo.NonNegativeReals)

    # Bounds: coordinated upper bound = coord_ub_multiplier * fv_max
    for s in streams_a:
        m.fa[s].setlb(params_a.flow_min.get(s, 0.0))
        m.fa[s].setub(coord.coord_ub_multiplier * params_a.flow_max[s])
    for s in streams_b:
        m.fb[s].setlb(params_b.flow_min.get(s, 0.0))
        m.fb[s].setub(coord.coord_ub_multiplier * params_b.flow_max[s])

    # Joint system capacity constraint
    m.sys_cap = pyo.Constraint(
        expr=(sum(m.fa[s] for s in streams_a)
              + sum(m.fb[s] for s in streams_b))
             <= cap_total
    )

    rev_a = sum(params_a.price[s] * m.fa[s] for s in streams_a)
    rev_b = sum(params_b.price[s] * m.fb[s] for s in streams_b)
    m.obj = pyo.Objective(expr=rev_a + rev_b, sense=pyo.maximize)

    solver = _get_solver()
    result = solver.solve(m)

    if result.solver.termination_condition != pyo.TerminationCondition.optimal:
        return CentralizedResult(
            status="infeasible",
            total_profit=0.0,
            profit_a=0.0,
            profit_b=0.0,
            flows_a={s: 0.0 for s in streams_a},
            flows_b={s: 0.0 for s in streams_b},
            standalone_profit_a=standalone_a,
            standalone_profit_b=standalone_b,
        )

    profit_a = float(pyo.value(rev_a))
    profit_b = float(pyo.value(rev_b))

    return CentralizedResult(
        status="optimal",
        total_profit=profit_a + profit_b,
        profit_a=profit_a,
        profit_b=profit_b,
        flows_a={s: float(pyo.value(m.fa[s])) for s in streams_a},
        flows_b={s: float(pyo.value(m.fb[s])) for s in streams_b},
        standalone_profit_a=standalone_a,
        standalone_profit_b=standalone_b,
    )

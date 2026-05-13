"""
transfer_payment_ir.py — Individual-rationality transfer-payment interval.

Computes the range of lump-sum transfers T from Refinery A to Refinery B
such that both refineries weakly prefer participation in the coordinated
plan over operating independently.

Convention: T > 0 means A pays B; T < 0 means B pays A.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IRInterval:
    """Individual-rationality transfer-payment interval [T_lo, T_hi]."""
    # Pre-transfer incremental profits
    delta_a: float   # A's local profit gain under coordination (before transfer)
    delta_b: float   # B's local profit gain under coordination (before transfer)

    # Transfer range
    t_lo: float      # Minimum transfer A must pay B (most favourable to A)
    t_hi: float      # Maximum transfer A must pay B (most favourable to B)

    # Feasibility flag
    feasible: bool   # True if [t_lo, t_hi] is non-empty

    @property
    def width(self) -> float:
        return self.t_hi - self.t_lo


def compute_ir_interval(
    standalone_a: float,
    standalone_b: float,
    coordinated_profit_a: float,  # A's profit under coordination, BEFORE transfer
    coordinated_profit_b: float,  # B's profit under coordination, BEFORE transfer
) -> IRInterval:
    """
    Compute the IR transfer-payment interval.

    The interval [T_lo, T_hi] is defined by:

        T_lo = -(delta_a)        -- A keeps all its gain; pays B just enough
        T_hi = -(delta_b)        -- B keeps all its gain; A pays most

    Equivalently, the IR constraints are:
        coordinated_profit_a - T >= standalone_a   →   T <= delta_a
        coordinated_profit_b + T >= standalone_b   →   T >= -delta_b

    Convention: positive T means A transfers to B.

    Parameters
    ----------
    standalone_a : float
        Refinery A standalone profit (no exchange).
    standalone_b : float
        Refinery B standalone profit (no exchange).
    coordinated_profit_a : float
        Refinery A pre-transfer profit under the coordinated plan.
    coordinated_profit_b : float
        Refinery B pre-transfer profit under the coordinated plan.

    Returns
    -------
    IRInterval
    """
    delta_a = coordinated_profit_a - standalone_a
    delta_b = coordinated_profit_b - standalone_b

    # IR constraints: T <= delta_a and T >= -delta_b
    t_lo = -delta_a   # A must pay at least -delta_a (could be negative = B pays A)
    t_hi = delta_b    # A pays at most delta_b

    # Note: the text uses "A pays B" as positive, matching the IR formulation
    # in the paper where T in [T_lo, T_hi] with T_lo = -delta_A, T_hi = -delta_B
    # (see manuscript Section 3.3).
    feasible = t_lo <= t_hi + 1e-9  # allow small numerical tolerance

    return IRInterval(
        delta_a=delta_a,
        delta_b=delta_b,
        t_lo=t_lo,
        t_hi=t_hi,
        feasible=feasible,
    )

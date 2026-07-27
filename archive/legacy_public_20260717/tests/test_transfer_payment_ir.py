"""
tests/test_transfer_payment_ir.py — Unit tests for IR transfer-payment interval.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.transfer_payment_ir import compute_ir_interval


def test_ir_interval_feasible():
    ir = compute_ir_interval(
        standalone_a=100.0,
        standalone_b=80.0,
        coordinated_profit_a=130.0,
        coordinated_profit_b=95.0,
    )
    assert ir.feasible
    assert ir.t_lo <= ir.t_hi


def test_ir_interval_bounds():
    ir = compute_ir_interval(
        standalone_a=100.0,
        standalone_b=80.0,
        coordinated_profit_a=130.0,  # delta_a = 30
        coordinated_profit_b=95.0,   # delta_b = 15
    )
    # t_lo = -delta_a = -30, t_hi = delta_b = 15
    assert abs(ir.t_lo - (-30.0)) < 1e-9
    assert abs(ir.t_hi - 15.0) < 1e-9


def test_ir_interval_infeasible_when_no_surplus():
    """If coordination creates no surplus, IR interval may be infeasible."""
    ir = compute_ir_interval(
        standalone_a=100.0,
        standalone_b=80.0,
        coordinated_profit_a=90.0,   # A is worse off
        coordinated_profit_b=70.0,   # B is worse off
    )
    # delta_a = -10, delta_b = -10 → t_lo = 10, t_hi = -10 → infeasible
    assert not ir.feasible


def test_paper_case_ir_interval():
    """Paper-reported IR interval: [−5,007,750, −887,820] CNY (Table 2)."""
    ir = compute_ir_interval(
        standalone_a=22_729_950.0,
        standalone_b=33_551_820.0,
        coordinated_profit_a=27_737_700.0,
        coordinated_profit_b=32_664_000.0,
    )
    assert ir.feasible
    assert abs(ir.t_lo - (-5_007_750.0)) < 1.0, f"t_lo {ir.t_lo:.2f} != -5007750"
    assert abs(ir.t_hi - (-887_820.0)) < 1.0, f"t_hi {ir.t_hi:.2f} != -887820"

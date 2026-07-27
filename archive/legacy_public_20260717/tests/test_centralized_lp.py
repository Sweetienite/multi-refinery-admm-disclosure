"""
tests/test_centralized_lp.py — Unit tests for centralized LP model.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.centralized_lp import RefineryParams, CoordinationSpec, solve_centralized, solve_standalone


# Minimal two-stream case for fast unit testing
PARAMS_A = RefineryParams(
    name="A",
    price={"s1": 1000.0, "s2": 500.0},
    flow_min={"s1": 0.0, "s2": 0.0},
    flow_max={"s1": 1.0, "s2": 1.0},
)

PARAMS_B = RefineryParams(
    name="B",
    price={"s3": 800.0, "s4": 300.0},
    flow_min={"s3": 0.0, "s4": 0.0},
    flow_max={"s3": 1.0, "s4": 1.0},
)


def test_standalone_solve_feasible():
    profit, flows = solve_standalone(PARAMS_A)
    assert profit > 0, "Standalone profit should be positive"
    assert set(flows.keys()) == {"s1", "s2"}


def test_standalone_maximises_high_price():
    """Plant should prefer high-price stream when capacity is binding."""
    profit, flows = solve_standalone(PARAMS_A)
    # Plant capacity = sum(fv_max) = 2.0, both streams fit, so both at max
    assert abs(flows["s1"] - 1.0) < 1e-4
    assert abs(flows["s2"] - 1.0) < 1e-4


def test_centralized_profit_geq_standalone():
    """Centralized joint profit must be >= sum of standalone profits."""
    cent = solve_centralized(PARAMS_A, PARAMS_B)
    standalone_total = cent.standalone_profit_a + cent.standalone_profit_b
    assert cent.total_profit >= standalone_total - 1.0, (
        f"Centralized {cent.total_profit:.2f} should be >= standalone {standalone_total:.2f}"
    )


def test_centralized_status_optimal():
    cent = solve_centralized(PARAMS_A, PARAMS_B)
    assert cent.status == "optimal"


def test_paper_case_standalone_profit():
    """Smoke-test: paper case standalone profits must be close to reported values."""
    import yaml

    config_path = ROOT / "configs" / "main_case.yaml"
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    from scripts.run_main_case import build_refinery_params, build_coord_spec

    params_a = build_refinery_params(cfg, "A")
    params_b = build_refinery_params(cfg, "B")
    coord = build_coord_spec(cfg)

    cent = solve_centralized(params_a, params_b, coord)
    total_standalone = cent.standalone_profit_a + cent.standalone_profit_b

    # Paper-reported standalone total: 56,281,770 CNY (Table 2)
    assert abs(total_standalone - 56_281_770.0) < 1.0, (
        f"Standalone total {total_standalone:.2f} != 56281770.00"
    )
    # Paper-reported coordinated total: 60,401,700 CNY (Table 2)
    assert abs(cent.total_profit - 60_401_700.0) < 1.0, (
        f"Coordinated total {cent.total_profit:.2f} != 60401700.00"
    )

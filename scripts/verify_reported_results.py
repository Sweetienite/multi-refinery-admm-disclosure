"""
verify_reported_results.py — Verify pre-computed results against paper values.

Loads pre-computed tables from ``results/tables/`` and compares them to the
expected metrics stored in ``results/expected_metrics.json``.

Usage:
    python scripts/verify_reported_results.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.validation import verify_results, print_verification_report


def load_tables_as_metrics(tables_dir: Path) -> dict[str, float]:
    """Load result tables and assemble a flat metrics dict for comparison."""
    metrics: dict[str, float] = {}

    # Table 2 — system profit breakdown
    # CSV metric column names differ from expected_metrics.json keys; map them.
    T2_KEY_MAP = {
        "standalone_a": "standalone_profit_a",
        "standalone_b": "standalone_profit_b",
        "standalone_total": "standalone_total_profit",
        "coordinated_total": "coordinated_total_profit",
        "coordination_value": "coordination_value",
        "admm_rel_total_error_pct": "admm_rel_total_error_pct",
        "ir_t_lo": "ir_t_lo",
        "ir_t_hi": "ir_t_hi",
    }
    t2 = tables_dir / "table2_system_profit.csv"
    raw_t2: dict[str, float] = {}
    if t2.exists():
        with open(t2, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                key = row["metric"]
                try:
                    raw_t2[key] = float(row["value_cny"])
                except (ValueError, KeyError):
                    pass
        for csv_key, exp_key in T2_KEY_MAP.items():
            if csv_key in raw_t2:
                metrics[exp_key] = raw_t2[csv_key]
        # coordinated per-plant profits = standalone + pre-transfer gain (delta)
        if "standalone_a" in raw_t2 and "delta_a" in raw_t2:
            metrics["coordinated_profit_a"] = raw_t2["standalone_a"] + raw_t2["delta_a"]
        if "standalone_b" in raw_t2 and "delta_b" in raw_t2:
            metrics["coordinated_profit_b"] = raw_t2["standalone_b"] + raw_t2["delta_b"]

    # Table 3 — ADMM convergence
    # CSV item column names differ from expected_metrics.json keys; map them.
    T3_KEY_MAP = {
        "admm_total_profit_cny": "admm_total_profit",
        "rel_total_profit_error_pct": "admm_rel_total_error_pct",
        "rel_cv_gap_pct": "admm_cv_gap_pct",
    }
    t3 = tables_dir / "table3_admm_convergence.csv"
    if t3.exists():
        with open(t3, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                key = row["item"]
                mapped_key = T3_KEY_MAP.get(key, key)
                try:
                    metrics[mapped_key] = float(row["value"])
                except (ValueError, KeyError):
                    pass

    # Table 4 — disclosure tradeoff (exposure scores by mechanism)
    # CSV: mechanism, role, admm_profit_cny, utility_retention, exposure_score,
    #      exposure_reduction_pct, note
    t4 = tables_dir / "table4_disclosure_tradeoff.csv"
    if t4.exists():
        with open(t4, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                mech = row.get("mechanism", "")
                try:
                    score = float(row["exposure_score"])
                    reduction = float(row["exposure_reduction_pct"])
                except (ValueError, KeyError):
                    continue
                if mech == "none":
                    metrics["exposure_score_no_control"] = score
                elif mech == "ts_ladder":
                    metrics["exposure_score_ts_ladder"] = score
                    metrics["exposure_reduction_ts_ladder_pct"] = reduction
                elif mech == "bucketing":
                    metrics["exposure_score_bucketing"] = score
                    metrics["exposure_reduction_bucketing_pct"] = reduction

    return metrics


def main() -> None:
    tables_dir = ROOT / "results" / "tables"
    computed = load_tables_as_metrics(tables_dir)

    checks, all_passed = verify_results(computed, results_dir=ROOT / "results")
    print_verification_report(checks)

    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()

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

    # Table 2
    t2 = tables_dir / "table2_system_profit.csv"
    if t2.exists():
        with open(t2, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                key = row["metric"]
                try:
                    metrics[key] = float(row["value_cny"])
                except (ValueError, KeyError):
                    pass

    # Table 3
    t3 = tables_dir / "table3_admm_convergence.csv"
    if t3.exists():
        with open(t3, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                key = row["item"]
                try:
                    metrics[key] = float(row["value"])
                except (ValueError, KeyError):
                    pass

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

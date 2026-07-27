#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DIMS = {
    "fig1a_system_value_gain.png": (3413, 909),
    "fig1b_allocation_changes.png": (3413, 1582),
    "fig2a_residual_convergence.png": (1641, 1216),
    "fig2b_capacity_allocation.png": (1641, 1216),
    "fig3a_indirect_exposure_components.png": (1641, 1228),
    "fig3b_exposure_reduction_and_synergy_retention.png": (1641, 1228),
    "fig4a_cap_multiplier_sensitivity.png": (1641, 1216),
    "fig4b_value_difference_sensitivity.png": (1641, 1216),
}


def close(actual: float, expected: float, tol: float = 1e-8) -> bool:
    return math.isclose(actual, expected, rel_tol=tol, abs_tol=tol)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    errors: list[str] = []
    for name, dims in EXPECTED_DIMS.items():
        path = ROOT / "figures" / "named" / name
        if not path.exists():
            errors.append(f"missing figure: {path}")
        elif Image.open(path).size != dims:
            errors.append(f"wrong dimensions: {name}={Image.open(path).size}, expected={dims}")

    fig1 = read(ROOT / "data" / "final_fig1a_system_value_gain.csv")
    values = {row["scenario"]: float(row["system_objective_million_CNY"]) for row in fig1}
    if not close(values.get("中心化协同", 0), 60.4017):
        errors.append("centralized objective mismatch")
    if not close((values.get("中心化协同", 0) - values.get("独立运营", 0)) * 1e6, 4119930.0):
        errors.append("synergy value mismatch")

    trace = read(ROOT / "data" / "fig2_admm_trace.csv")
    if len(trace) != 60:
        errors.append(f"ADMM trace has {len(trace)} rows, expected 60")
    if trace:
        if not close(float(trace[-1]["primal_residual"]), 8.344650970215639e-08):
            errors.append("final primal residual mismatch")
        if not close(float(trace[-1]["dual_residual"]), 3.147125156033326e-08):
            errors.append("final dual residual mismatch")

    scoring = read(ROOT / "data" / "scoring_closure_final_results.csv")
    required = {"E_exact", "E_stream", "E_temporal", "E_capacity", "E_aggregate", "S_main"}
    if not scoring or not required.issubset(scoring[0]):
        errors.append("five-component scoring columns missing")
    if errors:
        print("FAILED")
        print("\n".join(f" - {error}" for error in errors))
        return 1
    print("PASS: final public release values, eight figures, and trace contract verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

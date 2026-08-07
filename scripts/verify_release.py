#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
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
    "fig3a_indirect_exposure_components.png": (2126, 1535),
    "fig3b_exposure_reduction_and_synergy_retention.png": (1641, 1228),
    "fig4a_cap_multiplier_sensitivity.png": (1641, 1216),
    "fig4b_value_difference_sensitivity.png": (1641, 1216),
}


def close(actual: float, expected: float, tol: float = 1e-8) -> bool:
    return math.isclose(actual, expected, rel_tol=tol, abs_tol=tol)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_checksums(manifest: Path, base: Path, errors: list[str]) -> None:
    for line in manifest.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        expected, relative = line.split(maxsplit=1)
        path = base / relative
        if not path.exists():
            errors.append(f"checksum target missing: {path}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected:
            errors.append(f"checksum mismatch: {relative}")


def main() -> int:
    errors: list[str] = []
    if (ROOT / "archive").exists():
        errors.append("legacy archive must not be present in the public current branch")

    verify_checksums(ROOT / "data" / "SHA256SUMS.txt", ROOT / "data", errors)
    verify_checksums(ROOT / "figures" / "SHA256SUMS.txt", ROOT / "figures" / "named", errors)

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

    allocation = read(ROOT / "data" / "final_fig1b_allocation_changes.csv")
    positive_delta = sum(max(float(row["delta_kt"]), 0.0) for row in allocation)
    if not close(positive_delta, 3.78):
        errors.append("positive configuration increment mismatch")

    mechanism = {row["metric"]: row for row in read(ROOT / "data" / "final_fig3b_mechanism_summary.csv")}
    if not close(float(mechanism["暴露降低率/%"]["分阶段量化"]), 61.85, tol=1e-6):
        errors.append("stagewise exposure reduction mismatch")
    if not close(float(mechanism["暴露降低率/%"]["配置量分桶_均值"]), 49.95, tol=1e-6):
        errors.append("bucket exposure reduction mismatch")
    if not close(float(mechanism["协同收益保留率/%"]["分阶段量化"]), 99.987, tol=1e-6):
        errors.append("stagewise utility retention mismatch")
    if not close(float(mechanism["协同收益保留率/%"]["配置量分桶_均值"]), 99.964, tol=1e-6):
        errors.append("bucket utility retention mismatch")

    components = read(ROOT / "data" / "figure_inputs" / "final_fig3a_indirect_exposure_components.csv")
    expected_components = [
        (0.4666666666666667, 0.778525641025641),
        (0.696984126984127, 0.9742812582407958),
        (0.9917168200828639, 0.9996651443661757),
    ]
    if len(components) != 3:
        errors.append("final Figure 3 component row count mismatch")
    else:
        for row, (stage, bucket) in zip(components, expected_components):
            if not close(float(row["分阶段量化"]), stage, tol=1e-12) or not close(float(row["配置量分桶"]), bucket, tol=1e-12):
                errors.append("final Figure 3 component values mismatch")

    scoring = read(ROOT / "data" / "scoring_closure_final_results.csv")
    required = {"E_exact", "E_stream", "E_temporal", "E_capacity", "E_aggregate", "S_main"}
    if not scoring or not required.issubset(scoring[0]):
        errors.append("five-component scoring columns missing")
    for label, expected_iterations, expected_mean in (
        ("stagewise_quantization", [376, 376, 376], 0.38148768174258835),
        ("allocation_bucket_0p01", [27, 130, 199], 0.5005111515082138),
    ):
        rows = [row for row in scoring if row["label"] == label]
        if len(rows) != 3:
            errors.append(f"{label} scoring row count mismatch")
            continue
        actual_iterations = [int(row["n_iterations"]) for row in rows]
        if actual_iterations != expected_iterations:
            errors.append(f"{label} iteration counts mismatch: {actual_iterations}")
        actual_mean = sum(float(row["S_main"]) for row in rows) / len(rows)
        if not close(actual_mean, expected_mean, tol=1e-12):
            errors.append(f"{label} S_main mean mismatch")
    if errors:
        print("FAILED")
        print("\n".join(f" - {error}" for error in errors))
        return 1
    print("PASS: final public release values, eight figures, and trace contract verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

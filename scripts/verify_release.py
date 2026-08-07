#!/usr/bin/env python3
"""Verify the six panels actually used by the final manuscript.

The approved PNG files live in ``manuscript_figures_20260731``.  Their
hashes, dimensions, inputs, and supplied generator are deliberately verified
as one immutable bundle.  Rendering is not part of this check: exact pixels
depend on a compatible Chinese serif font (see the bundle README).
"""
from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "manuscript_figures_20260731"
EXPECTED_DIMS = {
    "fig1_allocation_changes.png": (3413, 1582),
    "fig2a_residuals.png": (1641, 1216),
    "fig2b_capacity_allocation.png": (1641, 1216),
    "fig3_indirect_exposure.png": (1641, 1228),
    "fig4a_cap_multiplier.png": (1641, 1216),
    "fig4b_value_difference.png": (1641, 1216),
}


def close(actual: float, expected: float, tol: float = 1e-8) -> bool:
    return math.isclose(actual, expected, rel_tol=tol, abs_tol=tol)


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_manifest(errors: list[str]) -> None:
    manifest = BUNDLE / "MANIFEST.sha256"
    if not manifest.exists():
        errors.append("missing manuscript figure manifest")
        return
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        path = BUNDLE / relative.removeprefix("./")
        if not path.exists():
            errors.append(f"manifest target missing: {relative}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append(f"manifest checksum mismatch: {relative}")


def main() -> int:
    errors: list[str] = []
    if (ROOT / "archive").exists():
        errors.append("legacy archive must not be present in the public current branch")
    verify_manifest(errors)

    for name, dims in EXPECTED_DIMS.items():
        path = BUNDLE / "figures" / name
        if not path.exists():
            errors.append(f"missing final-manuscript figure: {name}")
        elif Image.open(path).size != dims:
            errors.append(f"wrong dimensions: {name}={Image.open(path).size}, expected={dims}")

    allocation = read(BUNDLE / "data/final_fig1b_allocation_changes.csv")
    positive_delta = sum(max(float(row["delta_kt"]), 0.0) for row in allocation)
    if len(allocation) != 10 or not close(positive_delta, 3.78):
        errors.append("Figure 1 allocation contract mismatch")

    trace = read(BUNDLE / "data/fig2_admm_trace.csv")
    if len(trace) != 60:
        errors.append(f"ADMM trace has {len(trace)} rows, expected 60")
    elif not (
        close(float(trace[-1]["primal_residual"]), 8.344650970215639e-08)
        and close(float(trace[-1]["dual_residual"]), 3.147125156033326e-08)
    ):
        errors.append("final ADMM residual contract mismatch")

    components = read(BUNDLE / "data/final_fig3a_indirect_exposure_components.csv")
    expected_components = [
        (0.4666666666666667, 0.778525641025641),
        (0.696984126984127, 0.9742812582407958),
        (0.9917168200828639, 0.9996651443661757),
    ]
    if len(components) != 3:
        errors.append("Figure 3 component row count mismatch")
    else:
        for row, (stage, bucket) in zip(components, expected_components):
            if not close(float(row["分阶段量化"]), stage, 1e-12) or not close(float(row["配置量分桶"]), bucket, 1e-12):
                errors.append("Figure 3 component values mismatch")

    if errors:
        print("FAILED")
        print("\n".join(f" - {error}" for error in errors))
        return 1
    print("PASS: final manuscript's six panels, inputs, and supplied release bundle verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate the reader-facing final-paper contract without private inputs."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FINAL_FIGURE = ROOT / "manuscript_figures_20260731/figures/fig3_indirect_exposure.png"
FINAL_HASH = "72ac52f565b61fc128f810e294429cca1b750451d03faa86965d26277013b8df"


def close(actual: float, expected: float) -> bool:
    return math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-9)


def main() -> int:
    errors: list[str] = []
    required = [
        ROOT / "configs/paper_public_parameters_20260806.yaml",
        ROOT / "results/paper_key_results.json",
        ROOT / "results/table4_authoritative.csv",
        ROOT / "results/table5_weight_sensitivity_authoritative.csv",
        ROOT / "docs/MANUSCRIPT_ASSET_CONTRACT_20260807.md",
        ROOT / "manuscript_figures_20260731/MANIFEST.sha256",
        ROOT / "manuscript_figures_20260731/code/generate_paper_figures_final.py",
        FINAL_FIGURE,
    ]
    errors.extend(f"missing {path.relative_to(ROOT)}" for path in required if not path.exists())
    if FINAL_FIGURE.exists():
        if hashlib.sha256(FINAL_FIGURE.read_bytes()).hexdigest() != FINAL_HASH:
            errors.append("final Figure 3 checksum mismatch")
        if Image.open(FINAL_FIGURE).size != (1641, 1228):
            errors.append("final Figure 3 dimensions mismatch")
    result_path = ROOT / "results/paper_key_results.json"
    if result_path.exists():
        values = json.loads(result_path.read_text(encoding="utf-8"))
        expected = {
            "standalone_total_CNY": 56281770.0,
            "centralized_total_CNY": 60401700.0,
            "coordination_value_CNY": 4119930.0,
            "admm_total_CNY": 60401701.13487248,
            "admm_iterations": 60,
            "objective_difference_CNY": 1.13487248,
            "positive_allocation_increment_kt": 3.78,
            "s391_increment_share_percent": 48.7,
        }
        for key, expected_value in expected.items():
            actual = values.get(key)
            if actual is None or not close(float(actual), float(expected_value)):
                errors.append(f"key result mismatch: {key}")
        if values.get("validation", {}).get("reproducibility") != "PARTIAL_PASS":
            errors.append("reproducibility status must remain PARTIAL_PASS")
    if errors:
        print("FAILED")
        print("\n".join(f" - {error}" for error in errors))
        return 1
    print("PASS: public final-paper contract and final manuscript Figure 3 verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

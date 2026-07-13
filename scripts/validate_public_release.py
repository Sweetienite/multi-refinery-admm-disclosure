#!/usr/bin/env python3
"""Validate the published manuscript tables and final Figure 2-6 package."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
PACKAGE = ROOT / "figures_final_release"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (TABLES / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    table2 = {row["metric"]: float(row["value_cny"]) for row in rows("table2_system_profit.csv")}
    assert table2["standalone_total"] == 56_281_770.00
    assert table2["coordinated_total"] == 60_401_700.00
    assert table2["admm_profit_no_disclosure"] == 60_288_563.64

    table3 = {row["item"]: row["value"] for row in rows("table3_admm_convergence.csv")}
    assert table3["actual_iterations"] == "32"
    assert table3["final_primal_residual"] == "7.1097e-05"
    assert table3["final_dual_residual"] == "4.1687e-07"

    table4 = {row["mechanism"]: row for row in rows("table4_disclosure_tradeoff.csv")}
    assert table4["none"]["exposure_score"] == "0.930"
    assert table4["ts_ladder"]["utility_retention"] == "0.9997"
    assert table4["bucketing"]["exposure_score"] == "0.273"

    table5 = {row["weight_scheme"]: row for row in rows("table5_weight_sensitivity.csv")}
    assert table5["main"]["exposure_none"] == "0.930"
    assert table5["main"]["exposure_ts_ladder"] == "0.285"
    assert table5["main"]["exposure_bucketing"] == "0.273"

    sensitivity = rows("table6_economic_sensitivity.csv")
    assert len(sensitivity) == 5
    assert sensitivity[1]["coordination_value_cny"] == "4123130.00"
    assert sensitivity[-1]["coordination_value_cny"] == "4116730.00"

    manifest = json.loads((PACKAGE / "release_manifest.json").read_text(encoding="utf-8"))
    assert manifest["release_version"] == "v1.0.1-paper-submission"
    assert len(manifest["exports"]) == 9
    for entry in manifest["exports"]:
        path = PACKAGE / entry["file"]
        assert sha256(path) == entry["sha256"], path
        with Image.open(path) as image:
            assert image.mode == "RGB", path
            assert tuple(round(value) for value in image.info["dpi"]) == (600, 600), path

    source_index = (PACKAGE / "source" / "source_index.md").read_text(encoding="utf-8")
    for token in (
        "https://github.com/EMRPS/refinery-planning-benchmark",
        "case3/case3.gms",
        "无需访问其他仓库即可验证输入并重绘图件",
    ):
        assert token in source_index, token
    print("Published tables, final figures, checksums, and source index verified.")


if __name__ == "__main__":
    main()

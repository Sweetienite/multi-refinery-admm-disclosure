"""Export the frozen, publicly derived exchange-cost sensitivity results.

The exact manuscript sensitivity programs are identified by immutable commit
and path in ``figures_final_release/source/source_index.md``.  This compact
repository intentionally exports their checked public result summary instead
of pretending to recompute it from a different simplified objective.
"""
from __future__ import annotations

import csv
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main(output_dir: Path | None = None) -> None:
    source = ROOT / "data" / "derived" / "economic_sensitivity_settings.csv"
    with source.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    for row in rows[1:]:
        print(f"  {row[0]}={row[1]} → CV = {float(row[2]):,.2f} CNY ({row[3]}%)")

    out_dir = output_dir or ROOT / "results" / "generated" / "sensitivity"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "table6_economic_sensitivity.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

    print(f"  → Frozen public sensitivity summary exported to {out_dir}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export the frozen, publicly derived Table 6 sensitivity summary."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "results" / "generated" / "sensitivity",
        help="Directory for exported sensitivity summary; frozen manuscript tables are never overwritten by default.",
    )
    args = parser.parse_args()
    main(args.output_dir)

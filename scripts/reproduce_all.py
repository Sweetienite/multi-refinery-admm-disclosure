"""
reproduce_all.py — Master reproduction script.

Runs the compact diagnostic pipeline and regenerates the final Figure 2-6
panels from frozen public CSV inputs.  All outputs are written below
``results/generated/``; archived manuscript tables and final PNGs are never
overwritten.

Usage:
    python scripts/reproduce_all.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import scripts.run_main_case as run_main_case
import scripts.run_disclosure_assessment as run_disclosure
import scripts.run_sensitivity_checks as run_sensitivity
import scripts.make_figures as make_figures


def main() -> None:
    print("=" * 60)
    print("Multi-refinery ADMM Disclosure — Public Diagnostics and Figure Rendering")
    print("=" * 60)

    print("\n[1/4] Running compact main-case diagnostic (centralized LP + ADMM)...")
    run_main_case.main()

    print("\n[2/4] Running compact disclosure diagnostic...")
    run_disclosure.main()

    print("\n[3/4] Exporting frozen sensitivity summary...")
    run_sensitivity.main()

    print("\n[4/4] Regenerating final Figures 2-6 from frozen inputs...")
    make_figures.main()

    print("\nReproduction complete. Diagnostic outputs are in results/generated/.")


if __name__ == "__main__":
    main()

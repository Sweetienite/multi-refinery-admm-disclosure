"""
reproduce_all.py — Master reproduction script.

Runs the full pipeline to reproduce Tables 2–6 and Figures 2–5 from the
manuscript.  Results are written to ``results/tables/`` and figures to
``results/figures/``.

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
    print("Multi-refinery ADMM Disclosure — Full Reproduction")
    print("=" * 60)

    print("\n[1/4] Running main case (centralized LP + ADMM)...")
    run_main_case.main()

    print("\n[2/4] Running disclosure assessment...")
    run_disclosure.main()

    print("\n[3/4] Running sensitivity checks...")
    run_sensitivity.main()

    print("\n[4/4] Generating figures...")
    make_figures.main()

    print("\nReproduction complete.  Results in results/tables/ and results/figures/")


if __name__ == "__main__":
    main()

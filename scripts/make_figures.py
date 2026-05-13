"""
make_figures.py — Generate Figures 2–5 from pre-computed result files.

Usage:
    python scripts/make_figures.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.plotting import make_all_figures


def main() -> None:
    make_all_figures(
        results_dir=str(ROOT / "results"),
        output_dir=str(ROOT / "results" / "figures"),
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run the supplied generator for the six final-manuscript figure panels.

This compatibility entry point intentionally accepts no legacy ``--data-dir``
or ``--output-dir`` arguments. The final manuscript has a frozen bundle with
its own data and output contract; it requires an explicit overwrite flag so a
machine without the compatible CJK font cannot replace approved PNGs by
accident.
"""
from __future__ import annotations

import argparse
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument(
    "--overwrite-approved-outputs",
    action="store_true",
    help="render into the bundle's reproduced/ directory after checking its font requirements",
)
args = parser.parse_args()
if not args.overwrite_approved_outputs:
    raise SystemExit(
        "Refusing to overwrite frozen figure outputs. Read manuscript_figures_20260731/README.md "
        "and re-run with --overwrite-approved-outputs only on a compatible font stack."
    )
runpy.run_path(
    ROOT / "manuscript_figures_20260731/code/generate_paper_figures_final.py",
    run_name="__main__",
)

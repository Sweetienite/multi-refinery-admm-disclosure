"""Regenerate the nine final Figure 2-6 panels from frozen public CSV inputs."""
from __future__ import annotations

import sys
import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

def main(output_dir: Path | None = None) -> None:
    renderer = ROOT / "figures_final_release" / "source" / "plot_revised_figures_v2.py"
    destination = output_dir or ROOT / "results" / "generated" / "final_figures"
    subprocess.run([sys.executable, str(renderer), "--output-dir", str(destination)], check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "results" / "generated" / "final_figures",
        help="Directory for regenerated figures; archived final PNGs are never overwritten by default.",
    )
    args = parser.parse_args()
    main(args.output_dir)

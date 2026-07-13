#!/usr/bin/env python3
"""Create checksums and basic metadata for the frozen final figure exports."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
RESULTS = PACKAGE_ROOT / "results"
OUTPUT = PACKAGE_ROOT / "release_manifest.json"
FIGURES = [
    "fig2a_total_profit.png", "fig2b_coordination_value.png",
    "fig3a_residuals.png", "fig3b_capacity_allocation.png",
    "fig4_compensation_interval.png", "fig5_utility_exposure.png",
    "fig6a_exchange_cost.png", "fig6b_exchange_capacity.png",
    "fig6c_price_spread.png",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    exports = []
    for name in FIGURES:
        path = RESULTS / name
        with Image.open(path) as image:
            dpi = image.info.get("dpi", (None, None))
            exports.append({
                "file": f"results/{name}",
                "sha256": sha256(path),
                "mode": image.mode,
                "width_px": image.width,
                "height_px": image.height,
                "dpi": [round(float(value), 2) for value in dpi],
            })
    manifest = {
        "release_version": "v1.0.1-paper-submission",
        "release_note": "Same-name revision containing final submitted Figure 2-6 panels and reproducibility assets.",
        "upstream_source": {
            "repository": "https://github.com/Sweetienite/-benchmark-derived-.git",
            "branch": "e1-research-design-rebuild",
            "commit": "3b912c6f759533cb658fdae0cb9e53727a5fe3a2",
        },
        "exports": exports,
    }
    OUTPUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()

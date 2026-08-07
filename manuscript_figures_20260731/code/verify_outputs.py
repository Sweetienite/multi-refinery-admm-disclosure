from __future__ import annotations

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "fig1_allocation_changes.png": (3413, 1582),
    "fig2a_residuals.png": (1641, 1216),
    "fig2b_capacity_allocation.png": (1641, 1216),
    "fig3_indirect_exposure.png": (1641, 1228),
    "fig4a_cap_multiplier.png": (1641, 1216),
    "fig4b_value_difference.png": (1641, 1216),
}

for folder in [ROOT / "figures", ROOT / "reproduced"]:
    for name, expected_size in EXPECTED.items():
        path = folder / name
        if not path.exists():
            raise SystemExit(f"Missing: {path}")
        with Image.open(path) as image:
            if image.size != expected_size:
                raise SystemExit(f"Wrong size: {path}: {image.size} != {expected_size}")
print("All figure files and dimensions passed.")

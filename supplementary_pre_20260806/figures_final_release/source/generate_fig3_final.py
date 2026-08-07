from __future__ import annotations
from pathlib import Path
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "figure_inputs" / "final_fig3a_indirect_exposure_components.csv"
OUTPUT_IMAGE = ROOT / "figures_final_release" / "figures" / "fig3_indirect_exposure_final.png"
DPI = 600
WIDTH_CM, HEIGHT_CM = 9.0, 6.5
WIDTH_PX = round(WIDTH_CM / 2.54 * DPI)
HEIGHT_PX = round(HEIGHT_CM / 2.54 * DPI)
BLUE, ORANGE, DARK = "#2F6FB3", "#E67E22", "#202020"
FS_TICK, FS_LABEL, FS_LEGEND = 6.4, 7.2, 5.8

def resolve_chinese_font() -> tuple[str, str]:
    candidates = [
        os.environ.get("ADMM_FIGURE_FONT"),
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\simsun.ttf",
        "/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            font_manager.fontManager.addfont(candidate)
            return font_manager.FontProperties(fname=candidate).get_name(), candidate
    raise FileNotFoundError("未找到可用的中文宋体风格字体。可通过 ADMM_FIGURE_FONT 指定字体路径。")

font_name, font_file = resolve_chinese_font()
plt.rcParams.update({
    "font.family": font_name,
    "axes.unicode_minus": False,
    "mathtext.fontset": "dejavusans",
    "font.size": FS_TICK,
    "axes.linewidth": 0.60,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.major.size": 2.8,
    "ytick.major.size": 2.8,
    "xtick.major.width": 0.60,
    "ytick.major.width": 0.60,
})

df = pd.read_csv(DATA_FILE, encoding="utf-8-sig")
stage = df["分阶段量化"].to_numpy(dtype=float)
bucket = df["配置量分桶"].to_numpy(dtype=float)
fig = plt.figure(figsize=(WIDTH_CM / 2.54, HEIGHT_CM / 2.54), dpi=DPI, facecolor="white")
ax = fig.add_axes([0.15, 0.18, 0.80, 0.70])
x = np.arange(3)
bar_width = 0.24
ax.bar(x - bar_width / 2, stage, width=bar_width, color=BLUE, edgecolor="none", label="分阶段量化")
ax.bar(x + bar_width / 2, bucket, width=bar_width, color=ORANGE, edgecolor="none", label="配置量分桶")
ax.set_xticks(x, [r"$E_{\mathrm{temporal}}$", r"$E_{\mathrm{capacity}}$", r"$E_{\mathrm{aggregate}}$"])
ax.set_ylim(0.0, 1.0)
ax.set_yticks(np.arange(0.0, 1.01, 0.2))
ax.set_xlabel("加权指标", fontsize=FS_LABEL, labelpad=3.0)
ax.set_ylabel("指标得分", fontsize=FS_LABEL, labelpad=4.0)
ax.tick_params(top=False, right=False, labelsize=FS_TICK, pad=1.2)
ax.tick_params(axis="x", which="both", length=0)
for spine in ax.spines.values():
    spine.set_linewidth(0.60)
    spine.set_color(DARK)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.105), ncol=2, frameon=False,
          fontsize=FS_LEGEND, handlelength=1.0, columnspacing=0.9, borderaxespad=0.0)
fig.savefig(OUTPUT_IMAGE, dpi=DPI, facecolor="white", edgecolor="none")
plt.close(fig)
image = Image.open(OUTPUT_IMAGE).convert("RGB")
if image.size != (WIDTH_PX, HEIGHT_PX):
    image = image.resize((WIDTH_PX, HEIGHT_PX), Image.Resampling.LANCZOS)
image.save(OUTPUT_IMAGE, dpi=(DPI, DPI))
print(f"generated={OUTPUT_IMAGE}")
print(f"font={font_name} ({font_file})")

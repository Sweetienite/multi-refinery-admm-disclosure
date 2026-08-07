from __future__ import annotations

import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "reproduced"
OUT.mkdir(parents=True, exist_ok=True)

DPI = 600
BLUE = "#2F6FB3"
ORANGE = "#E67E22"
DARK = "#202020"
GRAY = "#888888"
LIGHT = "#C7C7C7"

FS_TICK = 6.4
FS_LABEL = 7.2
FS_ANNOT = 5.9
FS_LEGEND = 5.8


def resolve_chinese_font() -> tuple[str, str | None]:
    env = os.environ.get("ADMM_FIGURE_FONT")
    candidates = [
        env,
        r"C:\Windows\Fonts\simsun.ttc",
        r"C:\Windows\Fonts\simsun.ttf",
        "/usr/share/fonts/truetype/arphic-gbsn00lp/gbsn00lp.ttf",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            font_manager.fontManager.addfont(candidate)
            name = font_manager.FontProperties(fname=candidate).get_name()
            return name, candidate
    return "DejaVu Sans", None


FONT_NAME, FONT_FILE = resolve_chinese_font()
plt.rcParams.update(
    {
        "font.family": FONT_NAME,
        "axes.unicode_minus": False,
        "mathtext.fontset": "dejavusans",
        "font.size": FS_TICK,
        "axes.linewidth": 0.60,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 2.8,
        "ytick.major.size": 2.8,
        "xtick.major.width": 0.60,
        "ytick.major.width": 0.60,
    }
)


def new_fig(px_w: int, px_h: int) -> plt.Figure:
    return plt.figure(figsize=(px_w / DPI, px_h / DPI), dpi=DPI, facecolor="white")


def style_axes(
    ax: plt.Axes,
    *,
    xlabel: str | None = None,
    ylabel: str | None = None,
    ticksize: float = FS_TICK,
    xlabelsize: float = FS_LABEL,
    ylabelsize: float = FS_LABEL,
) -> None:
    ax.tick_params(top=False, right=False, labelsize=ticksize, pad=1.2)
    for spine in ax.spines.values():
        spine.set_linewidth(0.60)
        spine.set_color(DARK)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=xlabelsize, labelpad=2.8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=ylabelsize, labelpad=4.0)


def save_exact(fig: plt.Figure, filename: str, px_w: int, px_h: int) -> Path:
    path = OUT / filename
    fig.savefig(path, dpi=DPI, facecolor="white", edgecolor="none")
    plt.close(fig)
    image = Image.open(path).convert("RGB")
    if image.size != (px_w, px_h):
        image = image.resize((px_w, px_h), Image.Resampling.LANCZOS)
        image.save(path, dpi=(DPI, DPI))
    return path


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / name, encoding="utf-8-sig")


def figure1() -> Path:
    df = read_csv("final_fig1b_allocation_changes.csv")
    streams = df["stream"].tolist()
    values = df["delta_kt"].to_numpy(dtype=float)
    groups = df["group"].tolist()

    width_px, height_px = 3413, 1582
    fig = new_fig(width_px, height_px)
    ax = fig.add_axes([0.20, 0.14, 0.74, 0.80])
    y = np.arange(len(streams))[::-1]
    for yi, value in zip(y, values):
        ax.barh(
            yi,
            value,
            height=0.62,
            color=BLUE if value >= 0 else ORANGE,
            edgecolor="none",
        )
    ax.axvline(0, color=DARK, lw=0.70)
    ax.axhline(4.5, color=LIGHT, lw=0.60, ls=(0, (3, 3)))
    ax.set_yticks(y, streams)
    ax.set_xlim(-2.5, 2.5)
    ax.set_xticks([-2, -1, 0, 1, 2])

    for yi, value in zip(y, values):
        text = f"{value:+.2f}" if value >= 0 else f"{value:.2f}"
        if value >= 0:
            ax.text(value + 0.06, yi, text, ha="left", va="center", fontsize=6.0)
        elif abs(value) < 0.04:
            ax.text(-0.07, yi, text, ha="right", va="center", fontsize=6.0)
        else:
            ax.text(value - 0.06, yi, text, ha="right", va="center", fontsize=6.0)

    # The data are ordered as five streams from plant A and five from plant B.
    group_a = groups[0].replace("炼厂", "炼厂 ")
    group_b = groups[5].replace("炼厂", "炼厂 ")
    ax.text(-2.36, 8.55, group_a, ha="left", va="center", fontsize=6.6, fontweight="bold")
    ax.text(-2.36, 3.05, group_b, ha="left", va="center", fontsize=6.6, fontweight="bold")
    style_axes(ax, xlabel="流股变化量/kt", ylabel="候选流股编号")
    return save_exact(fig, "fig1_allocation_changes.png", width_px, height_px)


def figure2a() -> Path:
    df = read_csv("fig2_admm_trace.csv")
    iteration = df["iteration"].to_numpy()
    primal = df["primal_residual"].to_numpy(dtype=float)
    dual = df["dual_residual"].to_numpy(dtype=float)
    zero = df["dual_residual_is_zero"].astype(bool).to_numpy()
    dual_gap = dual.copy()
    dual_gap[zero] = np.nan

    width_px, height_px = 1641, 1216
    fig = new_fig(width_px, height_px)
    ax = fig.add_axes([0.22, 0.18, 0.74, 0.76])
    ax.plot(iteration, primal, color=BLUE, lw=0.95)
    ax.plot(iteration, dual_gap, color=ORANGE, lw=0.92, ls=(0, (5, 2.4)))
    ax.scatter(iteration[~zero], dual[~zero], s=2.0, color=ORANGE, zorder=3, linewidths=0)
    ax.axhline(1e-7, color=GRAY, lw=0.70, ls=(0, (3, 2.5)))
    ax.set_yscale("log")
    ax.set_xlim(0, 60)
    ax.set_ylim(1e-9, 1e1)
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60])
    ticks = [1e1, 1e-1, 1e-3, 1e-5, 1e-7, 1e-9]
    ax.set_yticks(ticks)
    ax.set_yticklabels([r"$10^{1}$", r"$10^{-1}$", r"$10^{-3}$", r"$10^{-5}$", r"$10^{-7}$", r"$10^{-9}$"])
    number_font = font_manager.FontProperties(family="DejaVu Sans")
    for label in ax.get_yticklabels():
        label.set_fontproperties(number_font)
        label.set_fontsize(FS_TICK)
    style_axes(ax, xlabel="迭代次数", ylabel="残差指标")
    ax.text(40.5, 1.5e-4, "原始残差", color=BLUE, fontsize=FS_ANNOT, ha="left", va="bottom")
    ax.text(14, 2.2e-4, "对偶残差", color=ORANGE, fontsize=FS_ANNOT, ha="left", va="bottom")
    ax.text(3, 1.8e-7, "停止阈值", color=GRAY, fontsize=5.8, ha="left", va="bottom")
    return save_exact(fig, "fig2a_residuals.png", width_px, height_px)


def figure2b() -> Path:
    df = read_csv("fig2_admm_trace.csv")
    iteration = df["iteration"].to_numpy()
    z_a = df["z_A"].to_numpy(dtype=float)
    z_b = df["z_B"].to_numpy(dtype=float)

    width_px, height_px = 1641, 1216
    fig = new_fig(width_px, height_px)
    ax = fig.add_axes([0.22, 0.18, 0.74, 0.76])
    ax.plot(iteration, z_a, color=BLUE, lw=0.95)
    ax.plot(iteration, z_b, color=ORANGE, lw=0.92, ls=(0, (5, 2.4)))
    ax.set_xlim(0, 60)
    ax.set_ylim(2.0, 6.15)
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60])
    ax.text(57.8, 3.66, r"$z_A=3.61$", color=BLUE, fontsize=FS_ANNOT, ha="right", va="bottom")
    ax.text(57.8, 4.59, r"$z_B=4.54$", color=ORANGE, fontsize=FS_ANNOT, ha="right", va="bottom")
    style_axes(ax, xlabel="迭代次数", ylabel="共享容量分配/kt")
    return save_exact(fig, "fig2b_capacity_allocation.png", width_px, height_px)


def figure3() -> Path:
    df = read_csv("final_fig3a_indirect_exposure_components.csv")
    components = df["component"].tolist()
    stage = df["分阶段量化"].to_numpy(dtype=float)
    bucket = df["配置量分桶"].to_numpy(dtype=float)

    width_px, height_px = 1641, 1228
    fig = new_fig(width_px, height_px)
    ax = fig.add_axes([0.20, 0.18, 0.75, 0.52])
    labels = [component.replace("可恢复度", "\n可恢复度").replace("可重构度", "\n可重构度") for component in components]
    x = np.arange(len(labels))
    bar_width = 0.24
    bars1 = ax.bar(x - bar_width / 2, stage, width=bar_width, color=BLUE, label="分阶段量化", edgecolor="none")
    bars2 = ax.bar(x + bar_width / 2, bucket, width=bar_width, color=ORANGE, label="配置量分桶", edgecolor="none")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.36)
    ax.set_yticks(np.arange(0, 1.21, 0.2))
    stage_offsets = [(-0.03, 0.055), (-0.03, 0.055), (-0.03, 0.085)]
    bucket_offsets = [(0.00, 0.055), (0.00, 0.055), (0.04, 0.115)]
    for i, (rect, value) in enumerate(zip(bars1, stage)):
        x_text = rect.get_x() + rect.get_width() / 2 + stage_offsets[i][0]
        y_text = value + stage_offsets[i][1]
        ax.text(x_text, y_text, f"{value:.3f}", ha="center", va="bottom", fontsize=FS_ANNOT)
    for i, (rect, value) in enumerate(zip(bars2, bucket)):
        x_text = rect.get_x() + rect.get_width() / 2 + bucket_offsets[i][0]
        y_text = value + bucket_offsets[i][1]
        ax.text(x_text, y_text, f"{value:.3f}", ha="center", va="bottom", fontsize=FS_ANNOT)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.14),
        ncol=2,
        frameon=False,
        fontsize=FS_LEGEND,
        handlelength=1.0,
        columnspacing=0.8,
        borderaxespad=0.0,
    )
    style_axes(ax, ylabel="间接可恢复暴露分量得分", ylabelsize=6.8)
    return save_exact(fig, "fig3_indirect_exposure.png", width_px, height_px)


def figure4a() -> Path:
    df = read_csv("final_fig4a_cap_multiplier_sensitivity.csv")
    x = df["协同上限倍数"].to_numpy(dtype=float)
    y = df["system_synergy_value_million_CNY"].to_numpy(dtype=float)

    width_px, height_px = 1641, 1216
    fig = new_fig(width_px, height_px)
    ax = fig.add_axes([0.22, 0.18, 0.74, 0.76])
    ax.plot(x, y, color=BLUE, lw=0.95, marker="o", ms=2.8, mfc=BLUE, mec=BLUE)
    ax.plot(2.0, 4.120, "o", ms=4.0, color=ORANGE, zorder=4)
    ax.axhline(4.120, color=GRAY, lw=0.70, ls=(0, (3, 2.5)))
    ax.set_xlim(1.6, 2.4)
    ax.set_ylim(2.90, 5.18)
    ax.set_xticks(x)
    ax.text(1.665, 3.06, "3.015", ha="left", va="bottom", fontsize=FS_ANNOT)
    ax.text(2.000, 4.255, "4.120", ha="center", va="bottom", fontsize=FS_ANNOT)
    ax.text(2.365, 4.945, "4.857", ha="right", va="bottom", fontsize=FS_ANNOT)
    style_axes(ax, xlabel="协同上限倍数", ylabel="系统协同价值/百万元")
    return save_exact(fig, "fig4a_cap_multiplier.png", width_px, height_px)


def figure4b() -> Path:
    df = read_csv("final_fig4b_value_difference_sensitivity.csv")
    x = df["价值差异系数"].to_numpy(dtype=float)
    y = df["system_synergy_value_million_CNY"].to_numpy(dtype=float)

    width_px, height_px = 1641, 1216
    fig = new_fig(width_px, height_px)
    ax = fig.add_axes([0.22, 0.18, 0.74, 0.76])
    ax.plot(x, y, color=BLUE, lw=0.95, marker="o", ms=2.8, mfc=BLUE, mec=BLUE)
    ax.plot(1.0, 4.120, "o", ms=4.0, color=ORANGE, zorder=4)
    ax.axhline(4.120, color=GRAY, lw=0.70, ls=(0, (3, 2.5)))
    ax.set_xlim(0.8, 1.2)
    ax.set_ylim(2.90, 5.18)
    ax.set_xticks(x)
    ax.text(0.812, 3.18, "3.296", ha="left", va="top", fontsize=FS_ANNOT)
    ax.text(1.000, 4.255, "4.120", ha="center", va="bottom", fontsize=FS_ANNOT)
    ax.text(1.183, 4.99, "4.944", ha="right", va="top", fontsize=FS_ANNOT)
    style_axes(ax, xlabel="价值差异系数", ylabel="系统协同价值/百万元")
    return save_exact(fig, "fig4b_value_difference.png", width_px, height_px)


def main() -> None:
    outputs = [figure1(), figure2a(), figure2b(), figure3(), figure4a(), figure4b()]
    print(f"Chinese font: {FONT_NAME} ({FONT_FILE or 'fallback'})")
    for output in outputs:
        print(output.relative_to(ROOT))


if __name__ == "__main__":
    main()

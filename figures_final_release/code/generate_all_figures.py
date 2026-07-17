#!/usr/bin/env python3
"""Regenerate all figures used by the final corrected manuscript.

Outputs PNG (300 dpi), SVG, and PDF to figures/generated.
The authoritative PNGs extracted from the delivered DOCX are under
figures/final_docx_png.
"""
from __future__ import annotations

import csv
import math
import subprocess
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "figures" / "generated"
OUT.mkdir(parents=True, exist_ok=True)

BLUE = "#5D7F99"
ORANGE = "#C88A5B"
DARK = "#3F3F3F"
LIGHT_GRAY = "#B7B7B7"
MID_GRAY = "#A8A8A8"
WHITE = "#FFFFFF"


def configure_matplotlib() -> None:
    mpl.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Noto Sans CJK JP", "Noto Sans CJK SC", "Microsoft YaHei", "SimHei", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "axes.linewidth": 1.2,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.major.width": 1.0,
        "ytick.major.width": 1.0,
        "mathtext.fontset": "stix",
        "savefig.facecolor": WHITE,
        "figure.facecolor": WHITE,
        "axes.facecolor": WHITE,
    })


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def save_all(fig: plt.Figure, stem: str, pixel_size: tuple[int, int]) -> None:
    width, height = pixel_size
    fig.set_size_inches(width / 300, height / 300, forward=True)
    for ext in ("png", "svg", "pdf"):
        kwargs = {"bbox_inches": None, "pad_inches": 0}
        if ext == "png":
            kwargs["dpi"] = 300
        fig.savefig(OUT / f"{stem}.{ext}", **kwargs)
    plt.close(fig)


def fig1a() -> None:
    rows = read_csv("fig1a_system_total_benefit.csv")
    labels = [r["case"] for r in rows]
    vals = np.array([float(r["objective_million_CNY"]) for r in rows])
    fig, ax = plt.subplots()
    bars = ax.bar(range(3), vals, width=0.62,
                  color=[LIGHT_GRAY, BLUE, BLUE], edgecolor=DARK, linewidth=1.2,
                  hatch=["/", None, "\\"])
    ax.set_ylabel("系统总收益/百万元", fontsize=24)
    ax.set_xticks(range(3), labels, fontsize=22)
    ax.set_ylim(0, 66)
    ax.set_yticks([0, 20, 40, 60])
    ax.tick_params(axis="y", labelsize=22, pad=8)
    ax.tick_params(axis="x", pad=8)
    for b, v in zip(bars, vals):
        ax.text(b.get_x()+b.get_width()/2, v+1.2, f"{v:.3f}", ha="center", va="bottom", fontsize=21)
    fig.subplots_adjust(left=0.14, right=0.98, bottom=0.17, top=0.96)
    save_all(fig, "fig1a_system_total_benefit", (1951, 1363))


def fig1b() -> None:
    row = read_csv("fig1b_objective_gap.csv")[0]
    val = float(row["difference_CNY"])
    fig, ax = plt.subplots()
    b = ax.bar([0], [val], width=0.7, color=ORANGE, edgecolor=DARK, linewidth=1.2, hatch="xx")[0]
    ax.set_ylabel("目标函数值差异/元", fontsize=24)
    ax.set_xticks([0], ["ADMM−中心化参考"], fontsize=22)
    ax.set_ylim(0, 1.5)
    ax.set_yticks([0, 0.5, 1.0, 1.5])
    ax.tick_params(axis="y", labelsize=22, pad=8)
    ax.text(0, val+0.06, f"{val:.3f}", ha="center", va="bottom", fontsize=21)
    fig.subplots_adjust(left=0.15, right=0.98, bottom=0.17, top=0.96)
    save_all(fig, "fig1b_objective_gap", (1963, 1363))


def fig2a() -> None:
    rows = read_csv("fig2_admm_trace.csv")
    it = np.array([int(r["iteration"]) for r in rows])
    primal = np.array([float(r["primal_residual"]) for r in rows])
    dual = np.array([float(r["dual_residual_plot"]) for r in rows])
    zero = np.array([int(r["dual_residual_is_zero"]) == 1 for r in rows])
    fig, ax = plt.subplots()
    ax.semilogy(it, primal, color=BLUE, marker="o", markerfacecolor=WHITE,
                markeredgecolor=BLUE, markersize=4.2, linewidth=1.6, label="原始残差指标")
    ax.semilogy(it, dual, color=ORANGE, marker="s", markerfacecolor=WHITE,
                markeredgecolor=ORANGE, markersize=3.9, linewidth=1.6, label="对偶残差指标")
    ax.scatter(it[zero], np.full(zero.sum(), 1e-9), marker="v", facecolors=WHITE,
               edgecolors=ORANGE, linewidths=1.2, s=30, label="对偶残差为0", zorder=4)
    ax.axhline(1e-7, color=MID_GRAY, linestyle="--", linewidth=1.5, label="停止阈值")
    ax.set_xlim(1, 60)
    ax.set_ylim(5e-10, 2e1)
    ax.set_xlabel("迭代次数", fontsize=21)
    ax.set_ylabel("残差指标", fontsize=21)
    ax.tick_params(labelsize=18)
    ax.legend(ncol=2, loc="upper right", frameon=False, fontsize=17,
              handlelength=2.4, columnspacing=1.8)
    fig.subplots_adjust(left=0.105, right=0.995, bottom=0.19, top=0.96)
    save_all(fig, "fig2a_admm_residuals", (3566, 1496))


def fig2b() -> None:
    rows = read_csv("fig2_admm_trace.csv")
    it = np.array([int(r["iteration"]) for r in rows])
    z_a = np.array([float(r["z_A"]) for r in rows])
    z_b = np.array([float(r["z_B"]) for r in rows])
    fig, ax = plt.subplots()
    ax.plot(it, z_a, color=BLUE, marker="o", markerfacecolor=WHITE,
            markeredgecolor=BLUE, markersize=4.2, linewidth=1.6, label=r"$z_A$")
    ax.plot(it, z_b, color=ORANGE, marker="s", markerfacecolor=WHITE,
            markeredgecolor=ORANGE, markersize=3.9, linewidth=1.6, label=r"$z_B$")
    ax.set_xlim(1, 60)
    ax.set_ylim(2.0, 6.15)
    ax.set_xlabel("迭代次数", fontsize=21)
    ax.set_ylabel("共享容量分配量/kt", fontsize=21)
    ax.tick_params(labelsize=18)
    ax.legend(loc="center right", frameon=False, fontsize=19, handlelength=2.4)
    fig.subplots_adjust(left=0.115, right=0.995, bottom=0.20, top=0.96)
    save_all(fig, "fig2b_capacity_allocation", (3566, 1436))


def fig3() -> None:
    r = read_csv("fig3_compensation_interval.csv")[0]
    lo = float(r["lower_million_CNY"])
    hi = float(r["upper_million_CNY"])
    width = float(r["width_million_CNY"])
    fig, ax = plt.subplots()
    ax.set_xlim(0, 5.5)
    ax.set_ylim(-0.8, 1.4)
    ax.axhline(0.5, color=MID_GRAY, linewidth=1.3)
    ax.plot([lo, hi], [0.5, 0.5], color=BLUE, linewidth=5.0, solid_capstyle="butt")
    ax.scatter([lo, hi], [0.5, 0.5], marker="D", s=90, color=BLUE, zorder=3)
    ax.text((lo+hi)/2, 0.93, f"可行补偿区间（宽度{width:.3f}百万元）", ha="center", fontsize=18)
    ax.text(lo, 0.05, f"{lo:.3f}", ha="center", fontsize=17)
    ax.text(hi, 0.05, f"{hi:.3f}", ha="center", fontsize=17)
    ax.text(5.45, 1.22, "单位：百万元", ha="right", fontsize=17)
    ax.text(2.75, -0.63, r"$T_{AB}>0$：炼厂A向炼厂B支付", ha="center", fontsize=18)
    ax.set_xticks([0, 1, 2, 3, 4, 5])
    ax.tick_params(axis="x", labelsize=17)
    ax.set_yticks([])
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_position(("data", -0.2))
    fig.subplots_adjust(left=0.02, right=0.995, bottom=0.23, top=0.98)
    save_all(fig, "fig3_compensation_interval", (3626, 1016))


def fig4() -> None:
    rows = read_csv("fig4_utility_exposure.csv")
    stage = next(r for r in rows if r["mechanism"] == "分阶段量化")
    bucket = next(r for r in rows if r["mechanism"] == "配置量分桶")
    fig, ax = plt.subplots()
    ax.scatter(float(stage["observable_exposure_score"]), float(stage["coordination_utility_retention"]),
               marker="s", s=135, color=BLUE, edgecolor=DARK, linewidth=1.0, zorder=3)
    ax.scatter(float(bucket["observable_exposure_score"]), float(bucket["coordination_utility_retention"]),
               marker="^", s=145, color=ORANGE, edgecolor=DARK, linewidth=1.0, zorder=3)
    ax.axhline(1.0, color=MID_GRAY, linestyle="--", linewidth=1.4)
    ax.axvline(1.0, color=MID_GRAY, linestyle="--", linewidth=1.4)
    ax.text(0.39, float(stage["coordination_utility_retention"])+1.0e-5, "分阶段量化", fontsize=17)
    ax.text(0.515, float(bucket["coordination_utility_retention"])-3.0e-5, "配置量分桶", fontsize=17)
    ax.text(0.03, 1.00001, "中心化协同增量基准", fontsize=16)
    ax.text(0.06, 0.999993, "低暴露\n高保留率", fontsize=15, va="top")
    ax.text(0.98, 0.999515, "未控制消息暴露基准", fontsize=15, ha="right", va="bottom")
    ax.set_xlim(0, 1.05)
    ax.set_ylim(0.9995, 1.00004)
    ax.set_xlabel("可观察暴露分数", fontsize=20)
    ax.set_ylabel("协同收益保留率", fontsize=20)
    ax.tick_params(labelsize=17)
    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.18, top=0.965)
    save_all(fig, "fig4_utility_exposure", (3373, 1903))


def main() -> None:
    configure_matplotlib()
    # Regenerate data first so the script is self-contained.
    subprocess.run([sys.executable, str(ROOT / "code" / "build_figure_data.py")], check=True)
    fig1a(); fig1b(); fig2a(); fig2b(); fig3(); fig4()
    print(f"Generated figures in: {OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Portable generator for the eight final paper subfigures.

The script reads the authoritative CSV files instead of duplicating paper values
in code. It does not bundle or require font files. A suitable local CJK serif
font is selected when available.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DPI = 600
BLUE = "#2F6FB3"
ORANGE = "#E67E22"
DARK = "#202020"
GRAY = "#888888"
LIGHT = "#C7C7C7"

EXPECTED_DIMS = {
    "image47.png": (3413, 909),
    "image48.png": (3413, 1582),
    "image49.png": (1641, 1216),
    "image50.png": (1641, 1216),
    "image51.png": (2126, 1535),
    "image52.png": (1641, 1228),
    "image53.png": (1641, 1216),
    "image54.png": (1641, 1216),
}

OUTPUT_NAMES = {
    "image47.png": "fig1a_system_value_gain.png",
    "image48.png": "fig1b_allocation_changes.png",
    "image49.png": "fig2a_residual_convergence.png",
    "image50.png": "fig2b_capacity_allocation.png",
    "image51.png": "fig3a_indirect_exposure_components.png",
    "image52.png": "fig3b_exposure_reduction_and_synergy_retention.png",
    "image53.png": "fig4a_cap_multiplier_sensitivity.png",
    "image54.png": "fig4b_value_difference_sensitivity.png",
}


def choose_cjk_serif_font() -> str:
    preferred = [
        "Songti SC", "SimSun", "STSong", "Noto Serif CJK SC",
        "Noto Serif CJK JP", "Source Han Serif SC", "AR PL UMing CN",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in preferred:
        if name in available:
            return name
    return "DejaVu Serif"


def configure_matplotlib() -> None:
    plt.rcParams.update({
        "font.family": choose_cjk_serif_font(),
        "axes.unicode_minus": False,
        "font.size": 7.5,
        "axes.linewidth": 0.65,
        "xtick.direction": "in",
        "ytick.direction": "in",
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "xtick.major.width": 0.65,
        "ytick.major.width": 0.65,
        "xtick.minor.width": 0.5,
        "ytick.minor.width": 0.5,
    })


def new_fig(px_w: int, px_h: int):
    return plt.figure(figsize=(px_w / DPI, px_h / DPI), dpi=DPI, facecolor="white")


def style(ax, xlabel=None, ylabel=None, ticksize=7.0):
    ax.tick_params(top=True, right=True, labelsize=ticksize, pad=1.5)
    for spine in ax.spines.values():
        spine.set_linewidth(0.65)
        spine.set_color(DARK)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=7.8, labelpad=3.0)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=7.8, labelpad=3.0)


def save(fig, output_dir: Path, name: str):
    px_w, px_h = EXPECTED_DIMS[name]
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / OUTPUT_NAMES.get(name, name)
    fig.savefig(path, dpi=DPI, facecolor="white", edgecolor="none")
    plt.close(fig)
    image = Image.open(path).convert("RGB")
    if image.size != (px_w, px_h):
        image = image.resize((px_w, px_h), Image.Resampling.LANCZOS)
        image.save(path, dpi=(DPI, DPI))
    actual = Image.open(path).size
    if actual != (px_w, px_h):
        raise RuntimeError(f"Unexpected size for {name}: {actual}")


def require_columns(df: pd.DataFrame, required: set[str], source: Path) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{source} missing columns: {sorted(missing)}")


def build_all(data_dir: Path, output_dir: Path, verification_path: Path | None = None) -> dict:
    configure_matplotlib()

    fig1a = pd.read_csv(data_dir / "final_fig1a_system_value_gain.csv")
    require_columns(fig1a, {"scenario", "system_objective_million_CNY"}, data_dir / "final_fig1a_system_value_gain.csv")
    by_scenario = dict(zip(fig1a["scenario"], fig1a["system_objective_million_CNY"]))
    x0 = float(by_scenario["独立运营"])
    x1 = float(by_scenario["中心化协同"])
    W, H = EXPECTED_DIMS["image47.png"]
    fig = new_fig(W, H)
    ax = fig.add_axes([0.055, 0.24, 0.91, 0.66])
    ax.plot([x0, x1], [0, 0], color=BLUE, lw=1.5)
    ax.plot(x0, 0, "o", ms=6.3, mfc="white", mec=BLUE, mew=1.0)
    ax.plot(x1, 0, "o", ms=6.3, mfc=ORANGE, mec=ORANGE, mew=1.0)
    ax.annotate("", xy=(x1, 0.28), xytext=(x0, 0.28), arrowprops=dict(arrowstyle="<->", lw=0.75, color=DARK))
    ax.text((x0+x1)/2, 0.37, f"系统协同价值 {x1-x0:.3f} 百万元", ha="center", va="bottom", fontsize=8.2)
    ax.text(x0, -0.18, f"独立运营\n{x0:.3f}", ha="center", va="top", fontsize=7.4)
    ax.text(x1, -0.18, f"中心化协同\n{x1:.3f}", ha="center", va="top", fontsize=7.4)
    ax.set_xlim(55.8, 61.0); ax.set_ylim(-0.52, 0.62); ax.set_yticks([]); ax.set_xticks([56,57,58,59,60,61])
    style(ax, xlabel="系统目标函数值/百万元")
    save(fig, output_dir, "image47.png")

    fig1b = pd.read_csv(data_dir / "final_fig1b_allocation_changes.csv")
    require_columns(fig1b, {"group", "stream", "delta_kt"}, data_dir / "final_fig1b_allocation_changes.csv")
    streams = fig1b["stream"].tolist(); vals = fig1b["delta_kt"].to_numpy(float); groups = fig1b["group"].tolist()
    W, H = EXPECTED_DIMS["image48.png"]
    fig = new_fig(W, H); ax = fig.add_axes([0.15, 0.13, 0.80, 0.82]); y = np.arange(len(streams))[::-1]
    for yi, value in zip(y, vals):
        ax.barh(yi, value, height=0.62, color=BLUE if value >= 0 else ORANGE, edgecolor="none")
    ax.axvline(0, color=DARK, lw=0.75); ax.axhline(4.5, color=LIGHT, lw=0.65, ls=(0,(3,3)))
    ax.set_yticks(y, streams); ax.set_xlim(-2.5, 2.5); ax.set_xticks([-2,-1,0,1,2])
    for yi, value in zip(y, vals):
        if value >= 0:
            ax.text(value+0.07, yi, f"{value:+.2f}", ha="left", va="center", fontsize=7.0)
        elif abs(value) < 0.04:
            ax.text(-0.08, yi, f"{value:.2f}", ha="right", va="center", fontsize=7.0)
        else:
            ax.text(value-0.07, yi, f"{value:.2f}", ha="right", va="center", fontsize=7.0)
    # Labels are based on the authoritative row grouping.
    first_b = groups.index("炼厂B") if "炼厂B" in groups else 5
    ax.text(-2.38, len(streams)-1.45, "炼厂 A", ha="left", va="center", fontsize=7.6, fontweight="bold")
    ax.text(-2.38, len(streams)-first_b-1.95, "炼厂 B", ha="left", va="center", fontsize=7.6, fontweight="bold")
    style(ax, xlabel="协同相对独立配置量变化/kt")
    save(fig, output_dir, "image48.png")

    trace = pd.read_csv(data_dir / "fig2_admm_trace.csv")
    require_columns(trace, {"iteration","primal_residual","dual_residual","z_A","z_B","dual_residual_is_zero"}, data_dir / "fig2_admm_trace.csv")
    if len(trace) != 60:
        raise ValueError(f"Expected 60 trace rows, got {len(trace)}")
    iteration = trace["iteration"].to_numpy(); primal = trace["primal_residual"].to_numpy(float)
    dual = trace["dual_residual"].to_numpy(float); z_a = trace["z_A"].to_numpy(float); z_b = trace["z_B"].to_numpy(float)
    zero = trace["dual_residual_is_zero"].astype(bool).to_numpy(); dual_plot = dual.copy(); dual_plot[zero] = np.nan

    W, H = EXPECTED_DIMS["image49.png"]
    fig = new_fig(W, H); ax = fig.add_axes([0.18,0.17,0.78,0.78])
    ax.plot(iteration, primal, color=BLUE, lw=1.05); ax.plot(iteration, dual_plot, color=ORANGE, lw=1.0, ls=(0,(5,2.4)))
    ax.scatter(iteration[~zero], dual[~zero], s=2.2, color=ORANGE, zorder=3, linewidths=0)
    ax.axhline(1e-7, color=GRAY, lw=0.75, ls=(0,(3,2.5)))
    ax.set_yscale("log"); ax.set_xlim(1,60); ax.set_ylim(1e-9,1e1); ax.set_xticks([1,10,20,30,40,50,60])
    ax.text(42,1.3e-4,"原始残差",color=BLUE,fontsize=7.0,ha="left",va="bottom")
    ax.text(14,2.0e-4,"对偶残差",color=ORANGE,fontsize=7.0,ha="left",va="bottom")
    ax.text(3,1.6e-7,"停止阈值",color=GRAY,fontsize=6.8,ha="left",va="bottom")
    style(ax, xlabel="迭代次数", ylabel="残差指标")
    save(fig, output_dir, "image49.png")

    W, H = EXPECTED_DIMS["image50.png"]
    fig = new_fig(W,H); ax = fig.add_axes([0.18,0.17,0.78,0.78])
    ax.plot(iteration,z_a,color=BLUE,lw=1.05); ax.plot(iteration,z_b,color=ORANGE,lw=1.0,ls=(0,(5,2.4)))
    ax.set_xlim(1,60); ax.set_ylim(2.0,6.15); ax.set_xticks([1,10,20,30,40,50,60])
    ax.text(58.5,3.68,"$z_A=3.61$",color=BLUE,fontsize=7.2,ha="right",va="bottom")
    ax.text(58.5,4.61,"$z_B=4.54$",color=ORANGE,fontsize=7.2,ha="right",va="bottom")
    style(ax, xlabel="迭代次数", ylabel="共享容量分配/kt")
    save(fig, output_dir, "image50.png")

    fig3a = pd.read_csv(data_dir / "final_fig3a_indirect_exposure_components.csv")
    require_columns(fig3a, {"component","分阶段量化","配置量分桶"}, data_dir / "final_fig3a_indirect_exposure_components.csv")
    stage = fig3a["分阶段量化"].to_numpy(float)
    bucket = fig3a["配置量分桶"].to_numpy(float)
    W,H = EXPECTED_DIMS["image51.png"]
    fig = new_fig(W,H); ax=fig.add_axes([0.15,0.18,0.80,0.70])
    labels = [r"$E_{\mathrm{temporal}}$", r"$E_{\mathrm{capacity}}$", r"$E_{\mathrm{aggregate}}$"]
    x=np.arange(len(labels)); bar_width=0.24
    ax.bar(x-bar_width/2,stage,width=bar_width,color=BLUE,label="分阶段量化",edgecolor="none")
    ax.bar(x+bar_width/2,bucket,width=bar_width,color=ORANGE,label="配置量分桶",edgecolor="none")
    ax.set_xticks(x,labels); ax.set_ylim(0.0,1.0); ax.set_yticks(np.arange(0.0,1.01,0.2))
    ax.legend(loc="upper center",bbox_to_anchor=(0.5,1.105),ncol=2,frameon=False,fontsize=5.8,handlelength=1.0,columnspacing=0.9)
    style(ax,xlabel="加权指标",ylabel="指标得分",ticksize=6.4)
    ax.tick_params(top=False,right=False)
    ax.tick_params(axis="x",which="both",length=0)
    save(fig, output_dir, "image51.png")

    fig3b = pd.read_csv(data_dir / "final_fig3b_mechanism_summary.csv").set_index("metric")
    exposure = fig3b.loc["暴露降低率/%"]
    retention = fig3b.loc["协同收益保留率/%"]
    W,H = EXPECTED_DIMS["image52.png"]
    fig = new_fig(W,H); ax1=fig.add_axes([0.32,0.60,0.64,0.32]); ax2=fig.add_axes([0.32,0.11,0.64,0.32])
    ax1.set_xlim(40,70); ax1.set_ylim(-0.55,1.55); ax1.set_yticks([1,0],["分阶段量化","配置量分桶"])
    ax1.plot(float(exposure["分阶段量化"]),1,"o",ms=4.8,color=BLUE)
    ax1.text(float(exposure["分阶段量化"])+0.75,1.08,f"{float(exposure['分阶段量化']):.2f}",ha="left",va="bottom",fontsize=6.8)
    mean=float(exposure["配置量分桶_均值"]); mn=float(exposure["配置量分桶_最小值"]); mx=float(exposure["配置量分桶_最大值"])
    ax1.errorbar(mean,0,xerr=np.array([[mean-mn],[mx-mean]]),fmt="o",ms=4.6,color=ORANGE,ecolor=ORANGE,capsize=3,lw=0.9)
    ax1.text(mean,0.22,f"{mean:.2f}",ha="center",va="bottom",fontsize=6.8); ax1.text(0.04,0.90,"暴露降低率/%",transform=ax1.transAxes,ha="left",va="top",fontsize=6.6)
    style(ax1,ticksize=6.5)
    ax2.set_xlim(99.88,100.02); ax2.set_ylim(-0.55,1.55); ax2.set_yticks([1,0],["分阶段量化","配置量分桶"]); ax2.set_xticks([99.90,99.95,100.00])
    ax2.plot(float(retention["分阶段量化"]),1,"o",ms=4.8,color=BLUE)
    ax2.text(float(retention["分阶段量化"])+0.003,1.08,f"{float(retention['分阶段量化']):.3f}",ha="left",va="bottom",fontsize=6.8)
    mean=float(retention["配置量分桶_均值"]); mn=float(retention["配置量分桶_最小值"]); mx=float(retention["配置量分桶_最大值"])
    ax2.errorbar(mean,0,xerr=np.array([[mean-mn],[mx-mean]]),fmt="o",ms=4.6,color=ORANGE,ecolor=ORANGE,capsize=3,lw=0.9)
    ax2.text(mean,0.22,f"{mean:.3f}",ha="center",va="bottom",fontsize=6.8); ax2.text(0.04,0.90,"协同收益保留率/%",transform=ax2.transAxes,ha="left",va="top",fontsize=6.6)
    style(ax2,ticksize=6.5)
    save(fig, output_dir, "image52.png")

    def sensitivity(source_name: str, x_col: str, y_col: str, output_name: str, xlabel: str, start_label_pos, end_label_pos):
        source = pd.read_csv(data_dir / source_name)
        require_columns(source, {x_col,y_col}, data_dir / source_name)
        x = source[x_col].to_numpy(float); yv = source[y_col].to_numpy(float)
        W,H = EXPECTED_DIMS[output_name]
        fig = new_fig(W,H); ax=fig.add_axes([0.18,0.17,0.78,0.78])
        ax.plot(x,yv,color=BLUE,lw=1.05,marker="o",ms=4.0,mfc=BLUE,mec=BLUE)
        baseline_index = int(np.argmin(np.abs(x-1.0 if x.min()<1.0 else x-2.0)))
        baseline_x=float(x[baseline_index]); baseline_y=float(yv[baseline_index])
        ax.plot(baseline_x,baseline_y,"o",ms=5.0,color=ORANGE,zorder=4); ax.axhline(baseline_y,color=GRAY,lw=0.75,ls=(0,(3,2.5)))
        ax.set_xlim(float(x.min())-0.04,float(x.max())+0.04); ax.set_ylim(2.90,5.15); ax.set_xticks(x)
        ax.text(*start_label_pos, f"{float(yv[0]):.3f}", fontsize=6.8, zorder=5)
        ax.text(baseline_x,baseline_y+0.08,f"{baseline_y:.3f}",ha="center",va="bottom",fontsize=6.8)
        ax.text(*end_label_pos, f"{float(yv[-1]):.3f}", fontsize=6.8)
        style(ax,xlabel=xlabel,ylabel="系统协同价值/百万元")
        save(fig, output_dir, output_name)

    sensitivity("final_fig4a_cap_multiplier_sensitivity.csv","协同上限倍数","system_synergy_value_million_CNY","image53.png","协同上限倍数",(1.62,3.34),(2.36,4.93))
    sensitivity("final_fig4b_value_difference_sensitivity.csv","价值差异系数","system_synergy_value_million_CNY","image54.png","价值差异系数",(0.842,3.145),(1.18,4.99))

    verification = {
        "iterations": int(len(trace)),
        "zero_dual_iterations": trace.loc[zero,"iteration"].astype(int).tolist(),
        "final_primal_residual": float(primal[-1]),
        "final_dual_residual": float(dual[-1]),
        "final_z_A": float(z_a[-1]),
        "final_z_B": float(z_b[-1]),
        "zero_handling": "Source zeros retained; zero dual residuals are converted to NaN only in the plotting array to create line breaks."
    }
    verification_path = verification_path or ROOT / "docs" / "figure_verification.json"
    verification_path.parent.mkdir(parents=True, exist_ok=True)
    verification_path.write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding="utf-8")
    return verification


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--data-dir",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    parser.add_argument(
        "--verification-path",
        type=Path,
        default=ROOT / "docs" / "figure_verification.json",
        help="写入图件数据验证摘要的路径；默认为当前仓库 docs/figure_verification.json",
    )
    args=parser.parse_args()
    verification=build_all(args.data_dir.resolve(),args.output_dir.resolve(),args.verification_path.resolve())
    print(json.dumps(verification,ensure_ascii=False,indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

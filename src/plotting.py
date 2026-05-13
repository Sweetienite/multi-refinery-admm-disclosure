"""
plotting.py — Figure generation for the multi-refinery ADMM disclosure paper.

Generates Figures 2–5 matching the paper layout.

Usage:
    from src.plotting import make_all_figures
    make_all_figures(results_dir="results", output_dir="results/figures")
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np


FIGURE_DPI = 300
FIGURE_SIZE = (8, 5)


# ---------------------------------------------------------------------------
# Figure 2 — Profit comparison bar chart
# ---------------------------------------------------------------------------

def fig2_profit_comparison(
    data: dict[str, float],
    output_path: Optional[str | Path] = None,
) -> None:
    """
    Bar chart comparing standalone vs coordinated profits for A, B, and system.

    Expected keys in ``data``:
        standalone_a, standalone_b, standalone_total,
        coordinated_a, coordinated_b, coordinated_total
    """
    labels = ["Refinery A", "Refinery B", "System Total"]
    standalone = [
        data["standalone_a"] / 1e6,
        data["standalone_b"] / 1e6,
        data["standalone_total"] / 1e6,
    ]
    coordinated = [
        data["coordinated_a"] / 1e6,
        data["coordinated_b"] / 1e6,
        data["coordinated_total"] / 1e6,
    ]

    x = np.arange(len(labels))
    width = 0.35
    fig, ax = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
    bars1 = ax.bar(x - width / 2, standalone, width, label="Standalone", color="#4C72B0")
    bars2 = ax.bar(x + width / 2, coordinated, width, label="Coordinated", color="#DD8452")

    ax.set_ylabel("Profit (million CNY)")
    ax.set_title("Figure 2 — System Profit Comparison")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3 — Individual-rationality interval
# ---------------------------------------------------------------------------

def fig3_ir_interval(
    t_lo: float,
    t_hi: float,
    output_path: Optional[str | Path] = None,
) -> None:
    """
    Horizontal bar showing the IR transfer-payment interval [T_lo, T_hi].
    """
    fig, ax = plt.subplots(figsize=(8, 3), dpi=FIGURE_DPI)
    ax.barh(0, t_hi - t_lo, left=t_lo / 1e4, height=0.4,
            color="#4C72B0", alpha=0.8)
    ax.axvline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xlabel("Transfer payment T (10,000 CNY)  [+ = A pays B]")
    ax.set_title("Figure 3 — Individual-Rationality Transfer-Payment Interval")
    ax.set_yticks([])
    ax.annotate(f"T_lo = {t_lo/1e4:.1f}", xy=(t_lo / 1e4, 0.25),
                fontsize=9, ha="left")
    ax.annotate(f"T_hi = {t_hi/1e4:.1f}", xy=(t_hi / 1e4, 0.25),
                fontsize=9, ha="right")
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 4 — Disclosure utility–exposure tradeoff
# ---------------------------------------------------------------------------

def fig4_disclosure_tradeoff(
    mechanisms: list[str],
    utility_retention: list[float],
    exposure_reduction: list[float],
    output_path: Optional[str | Path] = None,
) -> None:
    """
    Scatter plot of utility-retention vs exposure-reduction for each mechanism.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]
    for i, (mech, ur, er) in enumerate(zip(mechanisms, utility_retention, exposure_reduction)):
        ax.scatter(ur * 100, er * 100,
                   s=120, color=colors[i % len(colors)], zorder=5,
                   label=mech)
        ax.annotate(mech, (ur * 100, er * 100),
                    textcoords="offset points", xytext=(6, 4), fontsize=8)

    ax.set_xlabel("Utility retention (%)")
    ax.set_ylabel("Exposure reduction (%)")
    ax.set_title("Figure 4 — Disclosure Utility–Exposure Tradeoff")
    ax.legend(loc="lower left", fontsize=8)
    ax.set_xlim(99.5, 100.05)
    ax.set_ylim(-5, 80)
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 5 — Economic sensitivity
# ---------------------------------------------------------------------------

def fig5_economic_sensitivity(
    perturbations: list[float],
    coordination_values: list[float],
    output_path: Optional[str | Path] = None,
) -> None:
    """
    Line chart showing system coordination value under exchange-cost perturbations.
    """
    fig, ax = plt.subplots(figsize=FIGURE_SIZE, dpi=FIGURE_DPI)
    ax.plot(
        [p * 100 for p in perturbations],
        [v / 1e4 for v in coordination_values],
        marker="o", color="#4C72B0", linewidth=1.5,
    )
    ax.axvline(100, color="gray", linewidth=0.8, linestyle="--", label="Baseline")
    ax.set_xlabel("Exchange cost multiplier (%)")
    ax.set_ylabel("Coordination value (10,000 CNY)")
    ax.set_title("Figure 5 — Economic Parameter Sensitivity")
    ax.legend()
    fig.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=FIGURE_DPI)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------

def make_all_figures(results_dir: str = "results", output_dir: str = "results/figures") -> None:
    """Regenerate Figures 2–5 from pre-computed result files."""
    import json
    import csv

    rdir = Path(results_dir)
    odir = Path(output_dir)
    odir.mkdir(parents=True, exist_ok=True)

    with open(rdir / "expected_metrics.json", encoding="utf-8") as f:
        metrics = json.load(f)

    # Figure 2
    fig2_profit_comparison(
        {
            "standalone_a": metrics["standalone_profit_a"],
            "standalone_b": metrics["standalone_profit_b"],
            "standalone_total": metrics["standalone_total_profit"],
            "coordinated_a": metrics["coordinated_profit_a"],
            "coordinated_b": metrics["coordinated_profit_b"],
            "coordinated_total": metrics["coordinated_total_profit"],
        },
        output_path=odir / "fig2_profit_comparison.png",
    )

    # Figure 3
    fig3_ir_interval(
        t_lo=metrics["ir_t_lo"],
        t_hi=metrics["ir_t_hi"],
        output_path=odir / "fig3_ir_interval.png",
    )

    # Figure 4
    mechanisms = ["No control (baseline)", "Adaptive TS ladder", "Stream bucketing"]
    utility_retention = [1.0000, 0.9997, 0.9976]
    exposure_reduction = [0.0, 0.6935, 0.7065]
    fig4_disclosure_tradeoff(
        mechanisms, utility_retention, exposure_reduction,
        output_path=odir / "fig4_disclosure_tradeoff.png",
    )

    # Figure 5
    table6_path = rdir / "tables" / "table6_economic_sensitivity.csv"
    perturbations, cvals = [], []
    with open(table6_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["perturbation_type"] == "exchange_cost_multiplier" or row["perturbation_type"] == "baseline":
                perturbations.append(float(row["setting"]))
                cvals.append(float(row["coordination_value_cny"]))
    fig5_economic_sensitivity(perturbations, cvals,
                              output_path=odir / "fig5_economic_sensitivity.png")

    print(f"Figures written to {odir}")

#!/usr/bin/env python3
"""Build the compact CSV inputs used by the paper figures.

All values are derived from the frozen corrected Euclidean-projection ADMM
reference and the final scoring-closure files bundled under data/source.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "source"
OUT = ROOT / "data"

P_STANDALONE = 56_281_770.0
P_CENTRALIZED = 60_401_700.0
P_ADMM = 60_401_701.13487248
ADMM_GAP = P_ADMM - P_CENTRALIZED
P_STAGEWISE = 60_401_181.443218812
P_BUCKET = 60_400_230.30631116


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    # Figure 1(a)
    rows = [
        {"case": "独立运营", "objective_CNY": P_STANDALONE, "objective_million_CNY": P_STANDALONE / 1e6},
        {"case": "中心化协同", "objective_CNY": P_CENTRALIZED, "objective_million_CNY": P_CENTRALIZED / 1e6},
        {"case": "ADMM分布式", "objective_CNY": P_ADMM, "objective_million_CNY": P_ADMM / 1e6},
    ]
    write_csv(OUT / "fig1a_system_total_benefit.csv", list(rows[0]), rows)

    # Figure 1(b)
    rows = [{
        "comparison": "ADMM−中心化参考",
        "difference_CNY": ADMM_GAP,
        "absolute_difference_CNY": abs(ADMM_GAP),
    }]
    write_csv(OUT / "fig1b_objective_gap.csv", list(rows[0]), rows)

    # Figure 2
    ref = json.loads((SRC / "h3b_corrected_tight_reference.json").read_text(encoding="utf-8"))
    trace_rows = []
    for row in ref["trace"]:
        r = dict(row)
        dual = float(r["dual_residual"])
        zero = abs(dual) <= 1e-15
        r["dual_residual_is_zero"] = int(zero)
        r["dual_residual_plot"] = 1e-9 if zero else dual
        trace_rows.append(r)
    fields = list(trace_rows[0].keys())
    write_csv(OUT / "fig2_admm_trace.csv", fields, trace_rows)

    # Figure 3
    lower = 887_820.0
    upper = 5_007_750.0
    rows = [{
        "payer": "炼厂A",
        "payee": "炼厂B",
        "lower_CNY": lower,
        "upper_CNY": upper,
        "lower_million_CNY": lower / 1e6,
        "upper_million_CNY": upper / 1e6,
        "width_CNY": upper - lower,
        "width_million_CNY": (upper - lower) / 1e6,
    }]
    write_csv(OUT / "fig3_compensation_interval.csv", list(rows[0]), rows)

    # Figure 4
    scoring = json.loads((SRC / "scoring_closure_final_summary.json").read_text(encoding="utf-8"))
    score_map = {r["label"]: r for r in scoring}
    rows = [
        {
            "mechanism": "未控制消息暴露基准",
            "rho": "1/10",
            "objective_CNY": "",
            "coordination_utility_retention": 1.0,
            "observable_exposure_score": 1.0,
            "exposure_reduction_pct": 0.0,
            "marker": "baseline",
        },
        {
            "mechanism": "分阶段量化",
            "rho": 1.0,
            "objective_CNY": P_STAGEWISE,
            "coordination_utility_retention": (P_STAGEWISE - P_STANDALONE) / (P_CENTRALIZED - P_STANDALONE),
            "observable_exposure_score": score_map["stagewise_quantization"]["S_main_mean"],
            "exposure_reduction_pct": 100 * (1 - score_map["stagewise_quantization"]["S_main_mean"]),
            "marker": "square",
        },
        {
            "mechanism": "配置量分桶",
            "rho": 10.0,
            "objective_CNY": P_BUCKET,
            "coordination_utility_retention": (P_BUCKET - P_STANDALONE) / (P_CENTRALIZED - P_STANDALONE),
            "observable_exposure_score": score_map["allocation_bucket_0p01"]["S_main_mean"],
            "exposure_reduction_pct": 100 * (1 - score_map["allocation_bucket_0p01"]["S_main_mean"]),
            "marker": "triangle",
        },
    ]
    write_csv(OUT / "fig4_utility_exposure.csv", list(rows[0]), rows)

    # Figure 4 component data and weight sensitivity.
    comp_rows = []
    for label, zh in [
        ("baseline_rho1", "未控制消息基准"),
        ("stagewise_quantization", "分阶段量化"),
        ("allocation_bucket_0p01", "配置量分桶"),
    ]:
        r = score_map[label]
        comp_rows.append({
            "mechanism": zh,
            "E_exact": r["E_exact_mean"],
            "E_stream": r["E_stream_mean"],
            "E_temporal": r["E_temporal_mean"],
            "E_capacity": r["E_capacity_mean"],
            "E_aggregate": r["E_aggregate_mean"],
            "S_main": r["S_main_mean"],
        })
    write_csv(OUT / "fig4_exposure_components.csv", list(comp_rows[0]), comp_rows)

    sensitivity_rows = []
    schemes = [
        ("主权重", "S_main_mean"),
        ("均匀权重", "S_uniform_mean"),
        ("精确值直接暴露加权", "S_direct_weighted_mean"),
        ("轨迹信息加权", "S_trajectory_weighted_mean"),
        ("聚合重构加权", "S_aggregate_weighted_mean"),
    ]
    for scheme, key in schemes:
        for label, zh in [
            ("stagewise_quantization", "分阶段量化"),
            ("allocation_bucket_0p01", "配置量分桶"),
        ]:
            score = score_map[label][key]
            sensitivity_rows.append({
                "weight_scheme": scheme,
                "mechanism": zh,
                "score": score,
                "reduction_pct": 100 * (1 - score),
            })
    write_csv(OUT / "fig4_weight_sensitivity.csv", list(sensitivity_rows[0]), sensitivity_rows)


if __name__ == "__main__":
    main()

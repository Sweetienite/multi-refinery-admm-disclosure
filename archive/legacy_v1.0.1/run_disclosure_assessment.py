"""
run_disclosure_assessment.py — Disclosure mechanism evaluation.

Produces compact diagnostic counterparts of Table 4 (utility–exposure
tradeoff) and Table 5 (weight sensitivity). The frozen manuscript tables are
not overwritten.

Runs ADMM under three disclosure settings:
  - none        : no disclosure control (baseline)
  - ts_ladder   : adaptive threshold-ladder (main mechanism)
  - bucketing   : stream-bucketing (alternative mechanism)

Then recomputes exposure scores under all five weight schemes for Table 5.
"""
from __future__ import annotations

import csv
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml

from scripts.run_main_case import build_refinery_params, build_coord_spec, load_case_config
from src.admm_capacity_sharing import ADMMParams, run_admm
from src.disclosure_metrics import (
    WEIGHT_SCHEMES,
    ExposureScoreResult,
    DisclosureMessage,
    compute_exposure_score,
    messages_from_history_none,
    messages_from_history_ts_ladder,
    messages_from_history_bucketing,
)


MECHANISMS = ["none", "ts_ladder", "bucketing"]

# Paper-reported values (used as reference for comparison)
REPORTED = {
    "none":       {"utility_retention": 1.0000, "exposure_score": 0.930, "exposure_reduction": 0.0},
    "ts_ladder":  {"utility_retention": 0.9997, "exposure_score": 0.285, "exposure_reduction": 0.6935},
    "bucketing":  {"utility_retention": 0.9976, "exposure_score": 0.273, "exposure_reduction": 0.7065},
}


def _simulate_run(params_a, params_b, coord, admm_params, mechanism: str):
    """Run ADMM and generate disclosure messages for the given mechanism."""
    result = run_admm(params_a, params_b, coord, admm_params)

    # Build per-iteration exchange flow history from convergence history.
    # The ADMM records allocations_a per iteration.
    cap_bounds = {}
    for s in params_a.price:
        cap_bounds[s] = coord.coord_ub_multiplier * params_a.flow_max.get(s, 1.0)
    for s in params_b.price:
        cap_bounds[s] = coord.coord_ub_multiplier * params_b.flow_max.get(s, 1.0)

    all_streams = list(params_a.price) + list(params_b.price)
    n = result.iterations

    flows_per_iter = []
    for i, (ya, yb) in enumerate(
        zip(result.history.allocations_a, result.history.allocations_b)
    ):
        # Distribute each plant's capacity proportional to individual stream prices
        flows: dict[str, float] = {}
        total_price_a = sum(params_a.price[s] for s in params_a.price)
        for s in params_a.price:
            flows[s] = ya * params_a.price[s] / max(total_price_a, 1.0)
        total_price_b = sum(params_b.price[s] for s in params_b.price)
        for s in params_b.price:
            flows[s] = yb * params_b.price[s] / max(total_price_b, 1.0)
        flows_per_iter.append(flows)

    if mechanism == "none":
        messages = messages_from_history_none(flows_per_iter, cap_bounds)
    elif mechanism == "ts_ladder":
        messages = messages_from_history_ts_ladder(flows_per_iter, cap_bounds)
    elif mechanism == "bucketing":
        messages = messages_from_history_bucketing(flows_per_iter, cap_bounds)
    else:
        raise ValueError(f"Unknown mechanism: {mechanism}")

    return result, messages, all_streams


def main(output_dir: Path | None = None) -> None:
    """Run a compact disclosure diagnostic without overwriting frozen tables."""
    config_path = ROOT / "configs" / "main_case.yaml"
    cfg = load_case_config(config_path)
    admm_cfg = cfg.get("admm", {})

    params_a = build_refinery_params(cfg, "A")
    params_b = build_refinery_params(cfg, "B")
    coord = build_coord_spec(cfg)
    admm_params = ADMMParams(
        rho=admm_cfg.get("rho", 0.10),
        max_iter=admm_cfg.get("max_iter", 500),
        primal_tol=admm_cfg.get("primal_tol", 1e-3),
        dual_tol=admm_cfg.get("dual_tol", 1e-3),
        profit_scale=admm_cfg.get("profit_scale", 1e6),
    )

    results_by_mech: dict[str, dict] = {}
    messages_by_mech: dict[str, list[DisclosureMessage]] = {}
    all_streams_ref: list[str] = []

    baseline_profit = None

    for mech in MECHANISMS:
        print(f"  Running mechanism: {mech}")
        result, messages, all_streams = _simulate_run(
            params_a, params_b, coord, admm_params, mech
        )
        if baseline_profit is None:
            baseline_profit = result.total_profit

        score = compute_exposure_score(messages, all_streams, mechanism=mech, weight_scheme="main")
        results_by_mech[mech] = {
            "total_profit": result.total_profit,
            "exposure_score": score.total_score,
        }
        messages_by_mech[mech] = messages
        all_streams_ref = all_streams

    baseline_exposure = results_by_mech["none"]["exposure_score"]

    out_dir = output_dir or ROOT / "results" / "generated" / "disclosure_assessment"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Table 4
    table4_rows = [
        ["mechanism", "role", "admm_profit_cny", "utility_retention",
         "exposure_score", "exposure_reduction_pct", "note"],
    ]
    for mech in MECHANISMS:
        r = results_by_mech[mech]
        ur = r["total_profit"] / baseline_profit if baseline_profit else 0
        er = (baseline_exposure - r["exposure_score"]) / max(baseline_exposure, 1e-12)
        roles = {
            "none": "distributed baseline",
            "ts_ladder": "main evaluation mechanism",
            "bucketing": "main evaluation mechanism",
        }
        table4_rows.append([
            mech, roles[mech],
            f"{r['total_profit']:.2f}",
            f"{ur:.4f}",
            f"{r['exposure_score']:.3f}",
            f"{er*100:.2f}",
            "",
        ])
    with open(out_dir / "table4_disclosure_tradeoff.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(table4_rows)

    # Table 5 — weight sensitivity
    table5_rows = [["weight_scheme", "weight_direct", "weight_corridor",
                    "weight_temporal", "weight_bottleneck", "weight_side",
                    "exposure_none", "exposure_ts_ladder", "exposure_bucketing",
                    "reduction_ts_ladder_pct", "reduction_bucketing_pct"]]
    for scheme_name, weights in WEIGHT_SCHEMES.items():
        row = [
            scheme_name,
            str(weights["direct"]), str(weights["corridor"]),
            str(weights["temporal"]), str(weights["bottleneck"]), str(weights["side"]),
        ]
        scores = {}
        for mech in MECHANISMS:
            s = compute_exposure_score(
                messages_by_mech[mech], all_streams_ref,
                mechanism=mech, weight_scheme=scheme_name,
            )
            scores[mech] = s.total_score
        base_s = scores["none"]
        row += [
            f"{scores['none']:.3f}",
            f"{scores['ts_ladder']:.3f}",
            f"{scores['bucketing']:.3f}",
            f"{(base_s - scores['ts_ladder']) / max(base_s, 1e-12) * 100:.2f}",
            f"{(base_s - scores['bucketing']) / max(base_s, 1e-12) * 100:.2f}",
        ]
        table5_rows.append(row)

    with open(out_dir / "table5_weight_sensitivity.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(table5_rows)

    print(f"  → Diagnostic Table 4 and Table 5 outputs written to {out_dir}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the compact disclosure diagnostic into a non-authoritative output directory."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "results" / "generated" / "disclosure_assessment",
        help="Directory for diagnostic outputs; frozen manuscript tables are never overwritten by default.",
    )
    args = parser.parse_args()
    main(args.output_dir)

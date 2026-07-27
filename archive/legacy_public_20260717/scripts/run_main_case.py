"""
run_main_case.py — Centralized LP and ADMM main case run.

Produces a compact diagnostic counterpart of the Table 2 and Table 3
calculations. The frozen manuscript tables are not overwritten.

Case parameters are loaded from configs/main_case.yaml.
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

from src.centralized_lp import (
    RefineryParams,
    CoordinationSpec,
    solve_centralized,
)
from src.admm_capacity_sharing import ADMMParams, run_admm
from src.transfer_payment_ir import compute_ir_interval


def load_case_config(config_path: str | Path) -> dict:
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_refinery_params(cfg: dict, name: str) -> RefineryParams:
    p = cfg["refineries"][name]
    return RefineryParams(
        name=name,
        price=p["price"],
        flow_min=p.get("flow_min", {}),
        flow_max=p["flow_max"],
    )


def build_coord_spec(cfg: dict) -> CoordinationSpec:
    c = cfg.get("coordination", {})
    return CoordinationSpec(
        coord_ub_multiplier=c.get("coord_ub_multiplier", 2.0),
        total_system_capacity=c.get("total_system_capacity", None),
    )


def main(output_dir: Path | None = None) -> None:
    """Run the compact public model without altering frozen manuscript outputs."""
    config_path = ROOT / "configs" / "main_case.yaml"
    cfg = load_case_config(config_path)
    admm_cfg = cfg.get("admm", {})

    params_a = build_refinery_params(cfg, "A")
    params_b = build_refinery_params(cfg, "B")
    coord = build_coord_spec(cfg)

    # 1. Centralized solve
    cent = solve_centralized(params_a, params_b, coord)
    total_standalone = cent.standalone_profit_a + cent.standalone_profit_b
    cv_cent = cent.total_profit - total_standalone
    print(f"  Standalone A:       {cent.standalone_profit_a:>15,.2f} CNY")
    print(f"  Standalone B:       {cent.standalone_profit_b:>15,.2f} CNY")
    print(f"  Standalone total:   {total_standalone:>15,.2f} CNY")
    print(f"  Coordinated total:  {cent.total_profit:>15,.2f} CNY")
    print(f"  Coordination value: {cv_cent:>15,.2f} CNY")

    # 2. IR interval
    ir = compute_ir_interval(
        standalone_a=cent.standalone_profit_a,
        standalone_b=cent.standalone_profit_b,
        coordinated_profit_a=cent.profit_a,
        coordinated_profit_b=cent.profit_b,
    )
    print(f"  IR interval:  [{ir.t_lo:,.2f}, {ir.t_hi:,.2f}] CNY")

    # 3. ADMM
    admm_params = ADMMParams(
        rho=admm_cfg.get("rho", 0.10),
        max_iter=admm_cfg.get("max_iter", 500),
        primal_tol=admm_cfg.get("primal_tol", 1e-3),
        dual_tol=admm_cfg.get("dual_tol", 1e-3),
        profit_scale=admm_cfg.get("profit_scale", 1e6),
    )
    admm_result = run_admm(params_a, params_b, coord, admm_params)
    rel_err_total = abs(admm_result.total_profit - cent.total_profit) / max(abs(cent.total_profit), 1)
    cv_admm = admm_result.total_profit - total_standalone
    rel_err_cv = abs(cv_admm - cv_cent) / max(abs(cv_cent), 1)
    print(f"  ADMM status:        {admm_result.status}")
    print(f"  ADMM iterations:    {admm_result.iterations}")
    print(f"  ADMM total profit:  {admm_result.total_profit:>15,.2f} CNY")
    print(f"  Relative total-profit error: {rel_err_total*100:.3f}%")
    print(f"  Coordination-value gap:      {rel_err_cv*100:.2f}%")

    # 4. Write tables
    out_dir = output_dir or ROOT / "results" / "generated" / "main_case"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Table 2
    table2_rows = [
        ["metric", "value_cny", "note"],
        ["standalone_a", f"{cent.standalone_profit_a:.2f}", "Refinery A standalone profit"],
        ["standalone_b", f"{cent.standalone_profit_b:.2f}", "Refinery B standalone profit"],
        ["standalone_total", f"{total_standalone:.2f}", "System baseline"],
        ["coordinated_total", f"{cent.total_profit:.2f}", "Centralized reference"],
        ["coordination_value", f"{cv_cent:.2f}", ""],
        ["admm_profit_no_disclosure", f"{admm_result.total_profit:.2f}", "Distributed baseline"],
        ["admm_abs_error", f"{abs(admm_result.total_profit - cent.total_profit):.2f}", ""],
        ["admm_rel_total_error_pct", f"{rel_err_total*100:.3f}", ""],
        ["delta_a", f"{ir.delta_a:.2f}", "A pre-transfer gain"],
        ["delta_b", f"{ir.delta_b:.2f}", "B pre-transfer gain"],
        ["ir_t_lo", f"{ir.t_lo:.2f}", "IR interval lower bound"],
        ["ir_t_hi", f"{ir.t_hi:.2f}", "IR interval upper bound"],
    ]
    with open(out_dir / "table2_system_profit.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(table2_rows)

    # Table 3
    table3_rows = [
        ["item", "value"],
        ["decomposition", "capacity-sharing ADMM"],
        ["rho", str(admm_params.rho)],
        ["max_iter", str(admm_params.max_iter)],
        ["primal_tol", str(admm_params.primal_tol)],
        ["dual_tol", str(admm_params.dual_tol)],
        ["actual_iterations", str(admm_result.iterations)],
        ["final_primal_residual", f"{admm_result.final_primal_residual:.4e}"],
        ["final_dual_residual", f"{admm_result.final_dual_residual:.4e}"],
        ["admm_total_profit_cny", f"{admm_result.total_profit:.2f}"],
        ["rel_total_profit_error_pct", f"{rel_err_total*100:.3f}"],
        ["rel_cv_gap_pct", f"{rel_err_cv*100:.2f}"],
    ]
    with open(out_dir / "table3_admm_convergence.csv", "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(table3_rows)

    # Write diagnostic metrics next to the diagnostic tables.
    metrics = {
        "standalone_profit_a": cent.standalone_profit_a,
        "standalone_profit_b": cent.standalone_profit_b,
        "standalone_total_profit": total_standalone,
        "coordinated_total_profit": cent.total_profit,
        "coordinated_profit_a": cent.profit_a,
        "coordinated_profit_b": cent.profit_b,
        "coordination_value": cv_cent,
        "admm_total_profit": admm_result.total_profit,
        "admm_rel_total_error_pct": rel_err_total * 100,
        "admm_cv_gap_pct": rel_err_cv * 100,
        "ir_t_lo": ir.t_lo,
        "ir_t_hi": ir.t_hi,
    }
    with open(out_dir / "expected_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print(f"  → Diagnostic Table 2 and Table 3 outputs written to {out_dir}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the compact public ADMM model into a non-authoritative output directory."
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "results" / "generated" / "main_case",
        help="Directory for diagnostic outputs; frozen manuscript tables are never overwritten by default.",
    )
    args = parser.parse_args()
    main(args.output_dir)

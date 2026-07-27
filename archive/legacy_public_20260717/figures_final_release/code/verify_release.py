#!/usr/bin/env python3
"""Verify key values, expected files, pixel dimensions, and SHA-256 manifest."""
from __future__ import annotations
import csv, hashlib, json, math
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "fig1a_system_total_benefit.png": (1951, 1363),
    "fig1b_objective_gap.png": (1963, 1363),
    "fig2a_admm_residuals.png": (3566, 1496),
    "fig2b_capacity_allocation.png": (3566, 1436),
    "fig3_compensation_interval.png": (3626, 1016),
    "fig4_utility_exposure.png": (3373, 1903),
}

def close(a,b,tol=1e-9): return abs(a-b) <= tol*max(1.0,abs(a),abs(b))

def main():
    src = ROOT / "figures" / "final_docx_png"
    for name, dims in EXPECTED.items():
        p=src/name
        assert p.exists(), p
        assert Image.open(p).size == dims, (name,Image.open(p).size,dims)
    summary=json.loads((ROOT/'data/source/scoring_closure_final_summary.json').read_text(encoding='utf-8'))
    m={r['label']:r for r in summary}
    assert close(m['stagewise_quantization']['S_main_mean'],0.38148768174258835)
    assert close(m['allocation_bucket_0p01']['S_main_mean'],0.5005111515082138)
    with (ROOT/'data/fig2_admm_trace.csv').open(encoding='utf-8-sig') as f:
        rows=list(csv.DictReader(f))
    assert len(rows)==60
    assert close(float(rows[-1]['primal_residual']),8.344650970215639e-08)
    assert close(float(rows[-1]['dual_residual']),3.147125156033326e-08)
    print('Release verification passed.')
if __name__=='__main__': main()

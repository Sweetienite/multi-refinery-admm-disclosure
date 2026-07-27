#!/usr/bin/env python3
from __future__ import annotations
import json, math
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def close(a,b,tol=1e-6): return math.isclose(float(a),float(b),rel_tol=tol,abs_tol=tol)
def main():
    errors=[]
    exp=json.loads((ROOT/'results/paper_release_20260717/EXPECTED_FINAL_VALUES.json').read_text(encoding='utf-8'))['paper_values']
    summary=json.loads((ROOT/'results/paper_release_20260717/scoring_closure_final_summary.json').read_text(encoding='utf-8'))
    by={r['label']:r for r in summary}
    if not close(by['stagewise_quantization']['S_main_mean'],exp['stagewise_exposure_score']): errors.append('stagewise score mismatch')
    if not close(by['allocation_bucket_0p01']['S_main_mean'],exp['bucket_exposure_score']): errors.append('bucket score mismatch')
    data=ROOT/'figures_final_release/data'
    f1=pd.read_csv(data/'fig1a_system_total_benefit.csv')
    m=dict(zip(f1['case'],f1['objective_CNY']))
    for name,key in [('独立运营','standalone_total_CNY'),('中心化协同','centralized_objective_CNY'),('ADMM分布式','admm_objective_CNY')]:
        if not close(m[name],exp[key]): errors.append(f'{name} mismatch')
    gap=pd.read_csv(data/'fig1b_objective_gap.csv').iloc[0]['difference_CNY']
    if not close(gap,exp['admm_minus_centralized_CNY']): errors.append('objective gap mismatch')
    if errors:
        print('FAILED'); [print(' -',e) for e in errors]; return 1
    print('PASS: final public paper release values are internally consistent.'); return 0
if __name__=='__main__': raise SystemExit(main())

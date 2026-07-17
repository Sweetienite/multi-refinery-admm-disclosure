# Multi-refinery ADMM Disclosure — Final Paper Release

Reader-facing reproducibility release for the revised manuscript on ADMM-based multi-refinery coordinated production planning and commercial information disclosure control.

## Final numerical chain

| Item | Final value |
|---|---:|
| Standalone model objective | 56,281,770 CNY |
| Centralized coordinated objective | 60,401,700 CNY |
| Coordination value | 4,119,930 CNY |
| Euclidean-projection ADMM objective | 60,401,701.13487248 CNY |
| ADMM iterations | 60 |
| ADMM–centralized difference | 1.13487248 CNY |
| Positive allocation increment | 3.78 kt |
| Feasible A-to-B compensation | 887,820–5,007,750 CNY |

## Disclosure-control results

| Mechanism | Utility retention | Exposure score | Exposure reduction |
|---|---:|---:|---:|
| Stagewise quantization | 99.987% | 0.381488 | 61.85% |
| 0.01 kt allocation bucketing | 99.964% | 0.500511 | 49.95% |

The iteration order remains visible. The mechanisms control the numerical resolution of aggregate allocation messages and the visibility of active-stream identifiers. The exposure score is an empirical trace-based measure under the published fields, recovery rules, and weights; it is not a differential privacy, SMPC, cryptographic-security, or formal privacy guarantee.

## Repository scope

This repository contains the final paper-facing data, figures, plotting code, scoring summaries, and validation scripts. It supports independent redrawing and validation of the released table/figure values. Historical material is retained under `archive/` and must not be combined with the current release.

## Quick validation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r figures_final_release/requirements.txt
python figures_final_release/code/verify_release.py
python scripts/validate_paper_release_20260717.py
python figures_final_release/code/generate_all_figures.py
```

The model objectives are CNY-valued optimization objectives derived from public benchmark coefficients. They are not observed enterprise profits or estimates for a specific refinery. No enterprise production or confidential operating data are included.

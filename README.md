# Multi-refinery ADMM Disclosure

![Reproduce](https://github.com/Sweetienite/multi-refinery-admm-disclosure/actions/workflows/reproduce.yml/badge.svg)

Reproducibility package for the manuscript:

> **ADMM-based coordinated production planning and commercial information disclosure control for multi-refinery systems**

## Scope

This repository reproduces:
- Table 2: system profit, ADMM approximation, and individual-rationality interval
- Table 3: ADMM convergence parameters and results
- Table 4: utility–exposure tradeoff across disclosure mechanisms
- Table 5: observable exposure score weight sensitivity
- Table 6: economic parameter sensitivity
- Figures 2–6

## What is included

- Python implementation of the centralized reference LP model (`src/centralized_lp.py`)
- ADMM capacity-sharing approximation (`src/admm_capacity_sharing.py`)
- Individual-rationality transfer-payment interval calculation (`src/transfer_payment_ir.py`)
- Observable commercial information exposure metrics (`src/disclosure_metrics.py`)
- Figure generation code (`src/plotting.py`)
- Result verification (`src/validation.py`)
- Derived case parameters (`data/derived/`)
- Pre-computed result tables (`results/tables/`)
- Final paper figures (`results/figures/`)
- Final submitted figure release for Figures 2–6 (`figures_final_release/`)

## What is not included

- Confidential industrial production data
- Real refinery operating data
- Journal submission files (Word, LaTeX)
- Original upstream benchmark raw files
- Historical experiments not reported in the manuscript

## Data source

The case parameters are derived from the public refinery-petrochemical production planning benchmark:

> Wenli Du, Chuan Wang, Chen Fan, Zhi Li, Yeke Zhong, Tianao Kang, Ziting Liang,
> Minglei Yang, Feng Qian, Xin Dai.
> A production planning benchmark for real-world refinery-petrochemical complexes.
> arXiv:2503.22057, 2025.

Repository: https://github.com/EMRPS/refinery-planning-benchmark

See `data/README.md` for details on data provenance.

## Installation

```bash
git clone https://github.com/Sweetienite/multi-refinery-admm-disclosure.git
cd multi-refinery-admm-disclosure
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows cmd:
# .venv\Scripts\activate.bat
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
```

A solver is required. HiGHS is recommended and installed automatically via `highspy`.

## Reproduce results

```bash
# Run all experiments and regenerate result tables
python scripts/reproduce_all.py

# Verify computed results match reported paper values
python scripts/verify_reported_results.py

# Generate figures
python scripts/make_figures.py
```

## Verification status

The pre-computed result tables can be verified against the reported paper values without re-running the full model:

```bash
python scripts/verify_reported_results.py
```

Expected output: `17/17 checks passed` with `rel_err = 0.0000%` for all metrics.

A full reproduction run (requires HiGHS solver via `highspy`) can be executed with:

```bash
python scripts/reproduce_all.py
```

The repository reproduces manuscript Tables 2–6 and Figures 2–6 from publicly derived case parameters. It does not contain enterprise production data or confidential industrial information.

## Final submitted figures (Figures 2–6)

`figures_final_release/` is the authoritative final submission package for the
nine independent panels of Figures 2–6. It contains the exported 600 dpi RGB
PNG files, the frozen CSV inputs, the plotting script, data checks, checksums,
and a source-program index. The older files in `results/figures/` are retained
as historical reproduction outputs and must not be substituted for this final
submission package.

To validate the frozen inputs and regenerate the figures into a separate
directory (leaving the archived final PNGs untouched):

```bash
python figures_final_release/source/validate_data.py
python figures_final_release/source/plot_revised_figures_v2.py \
  --output-dir /tmp/final-figure-render
```

The frozen values are derived from public benchmark parameters and scripts.
They do not include enterprise production data or confidential production
information. See `figures_final_release/source/source_index.md` for the exact
upstream repository, commit, programs, and figure-to-data mapping.

## Expected key metrics

| Metric | Value |
|--------|-------|
| Standalone total profit | 56,281,770.00 CNY |
| Centralized coordinated profit | 60,401,700.00 CNY |
| System coordination value | 4,119,930.00 CNY |
| ADMM relative total-profit error | 0.187% |
| ADMM coordination-value gap | 2.75% |
| Adaptive thresholding exposure reduction | 69.35% |
| Flow interval aggregation exposure reduction | 70.65% |

## License

Code: MIT License (see `LICENSE`).

Derived data and result files: see `DATA_LICENSE.md`.

## Citation

If you use this repository, please cite the associated manuscript and the upstream benchmark.
See `CITATION.cff` for the full citation entry.

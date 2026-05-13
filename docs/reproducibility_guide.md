# Reproducibility guide

## Prerequisites

- Python ≥ 3.10
- HiGHS solver (installed automatically via `highspy`)
- Pyomo ≥ 6.7

## Quick start

```bash
git clone https://github.com/Sweetienite/multi-refinery-admm-disclosure.git
cd multi-refinery-admm-disclosure

python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
# source .venv/bin/activate

pip install -r requirements.txt

# Reproduce all tables and figures:
python scripts/reproduce_all.py

# Verify against paper-reported values:
python scripts/verify_reported_results.py
```

## Step-by-step

### 1. Main case (Tables 2 and 3)

```bash
python scripts/run_main_case.py
```

Writes:
- `results/tables/table2_system_profit.csv`
- `results/tables/table3_admm_convergence.csv`
- `results/expected_metrics.json` (updated)

### 2. Disclosure assessment (Tables 4 and 5)

```bash
python scripts/run_disclosure_assessment.py
```

Writes:
- `results/tables/table4_disclosure_tradeoff.csv`
- `results/tables/table5_weight_sensitivity.csv`

### 3. Economic sensitivity (Table 6)

```bash
python scripts/run_sensitivity_checks.py
```

Writes:
- `results/tables/table6_economic_sensitivity.csv`

### 4. Generate figures

```bash
python scripts/make_figures.py
```

Writes figures to `results/figures/`.
Figure 1 (methodology flowchart) is a manually composed figure and is not regenerated
by script; the PNG is stored directly in `results/figures/`.

## Troubleshooting

**Solver not found**: ensure `highspy` is installed (`pip install highspy`).
If HiGHS is not available, install a compatible solver (GLPK, CBC) and update
the solver factory calls in `src/centralized_lp.py`.

**Numerical differences**: the ADMM implementation uses a standard symmetric
z-update. Results may differ slightly from the paper (which uses the project's
internal ADMM) due to subproblem decomposition differences.  
The pre-computed tables in `results/tables/` record the exact paper-reported values.

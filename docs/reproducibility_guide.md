# Reproducibility guide

## Frozen public artifacts

The following files are the public release records for the submitted-artifact
package. They are internally checked and reproducible as presentation
artifacts; the corrected numerical authority is the pinned reconstruction
branch described in `docs/authoritative_case4l_evidence.md`.

- Tables 2–6: `results/tables/` and `results/expected_metrics.json`
- Final Figure 2–6 panels, frozen plotting CSVs, renderer, checksums, and
  source-program index: `figures_final_release/`

Run this before using or rerendering the package:

```bash
python scripts/validate_public_release.py
```

The public benchmark source and local frozen data-to-figure mapping are listed
in `figures_final_release/source/source_index.md`. The compact model in `src/`
is an independently runnable diagnostic implementation; it is not presented
as a byte-for-byte replacement for the frozen 32-iteration trace.

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

# Run compact diagnostics and render final Figures 2-6 to results/generated/:
python scripts/reproduce_all.py

# Verify against paper-reported values:
python scripts/verify_reported_results.py
```

## Step-by-step

### 1. Compact main-case diagnostic

```bash
python scripts/run_main_case.py
```

Writes non-authoritative diagnostic outputs to:

- `results/generated/main_case/table2_system_profit.csv`
- `results/generated/main_case/table3_admm_convergence.csv`
- `results/generated/main_case/expected_metrics.json`

### 2. Compact disclosure diagnostic

```bash
python scripts/run_disclosure_assessment.py
```

Writes non-authoritative diagnostic outputs to
`results/generated/disclosure_assessment/`.

### 3. Frozen economic sensitivity export

```bash
python scripts/run_sensitivity_checks.py
```

Exports the checked public sensitivity summary to
`results/generated/sensitivity/table6_economic_sensitivity.csv`. It does not
claim to recalculate the sensitivity from the compact LP objective.

### 4. Generate final figures

```bash
python scripts/make_figures.py
```

Writes the nine final panels to `results/generated/final_figures/`. The archived
submission PNGs under `figures_final_release/results/` are never overwritten.
Figure 1 is outside this package's regeneration scope.

## Troubleshooting

**Solver not found**: ensure `highspy` is installed (`pip install highspy`).
If HiGHS is not available, install a compatible solver (GLPK, CBC) and update
the solver factory calls in `src/centralized_lp.py`.

**Numerical differences**: the compact ADMM implementation is a reader-facing
diagnostic and is not the authoritative full-trace implementation. The exact
historical 32-iteration trace is supplied as a frozen public result series; the
separately corrected Euclidean-projection reference and corrected 60-run grid
are pinned in the authoritative reconstruction branch. The frozen tables and
final figure inputs record the historical release artifacts and are protected
from being overwritten by compact diagnostics.

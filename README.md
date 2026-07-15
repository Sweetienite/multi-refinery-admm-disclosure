# Multi-refinery ADMM Disclosure

Reader-facing release for the manuscript *ADMM-based coordinated production
planning and commercial information disclosure control for multi-refinery
systems*.

This repository provides the released tables, figures, derived public inputs,
and checks that keep those presentation artifacts internally consistent.  The
full numerical reconstruction is deliberately kept in one authoritative source
repository, rather than duplicated here with a second implementation.

## Start here

- To inspect or regenerate the released figures: use this repository.
- To recompute the manuscript-equivalent numerical evidence: use the
  [authoritative Case4-L reconstruction branch](docs/authoritative_case4l_evidence.md).
- Do not use `src/admm_capacity_sharing.py` to reproduce manuscript Table 3 or
  the disclosure results.  It is a compact diagnostic implementation with
  different algorithmic behavior.

## What is included here

- Released Tables 2–6 and Figures 2–6.
- Derived, non-confidential benchmark parameters.
- Frozen figure inputs, renderer, checksums, and presentation-artifact checks.
- A compact diagnostic model useful for code inspection, but not as the
  manuscript’s numerical source of truth.

The table and figure files retained in this repository are historical release
artifacts.  They are not an alternative numerical authority and must not be
cited when they differ from the pinned reconstruction.  In particular, use the
reconstruction branch for the ADMM payment interval, run counts, and
trace-derived exposure values.

## What is not included here

- Enterprise production or operating data.
- A second copy of the full ADMM/disclosure trace archive.
- A claim that the compact diagnostic model independently regenerates every
  manuscript number.

## Install and use

```bash
git clone https://github.com/Sweetienite/multi-refinery-admm-disclosure.git
cd multi-refinery-admm-disclosure
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt

# Check released tables and figures against their frozen source package.
python scripts/validate_public_release.py

# Regenerate final figures into a separate directory.
python figures_final_release/source/validate_data.py
python figures_final_release/source/plot_revised_figures_v2.py \\
  --output-dir /tmp/final-figure-render
```

`scripts/verify_reported_results.py` checks archived reported values.  It is a
consistency check, not an independent full-model recomputation.

## Paper-facing terminology

The model is a derived benchmark shared-capacity allocation case.  Objective
values are CNY-valued model objectives, not observed enterprise profits.  The
reported disclosure measures are empirical trace-based observable-exposure
measures; they do not claim differential privacy, SMPC, cryptographic security,
or formal privacy guarantees.  See the authoritative reconstruction guide for
the exact numerical scope and all wording limits.

## Data provenance and license

The derived case parameters originate from the public refinery-petrochemical
production-planning benchmark by Du et al. (2025).  See `data/README.md`,
`DATA_LICENSE.md`, and `CITATION.cff` for provenance, licensing, and citation.

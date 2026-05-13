# Limitations

## Case scope

The numerical results are derived from a single **strong-complementarity
counterfactual** case constructed from publicly available benchmark parameters.
They are **not** generalisable to:

- Arbitrary refinery pairs with different stream structures
- Real industrial multi-refinery systems
- Cases where coordination value is small or negative
- Scenarios with complex blending, quality constraints, or multi-period dynamics

The case is designed to study the ADMM coordination and disclosure-control
methodology under clearly positive complementarity, not to estimate real-world
multi-refinery economics.

## Model simplifications

The model implemented in this repository is a single-period, single-commodity
LP.  The full benchmark (Case 3) includes:
- Multi-period planning (multiple time steps)
- Complex blending specifications
- Quality constraints
- Inventory dynamics

The simplified model in `src/centralized_lp.py` captures the capacity-sharing
and exchange structure but omits these complexities.

## ADMM convergence

The ADMM capacity-sharing decomposition used in this repository implements a
standard symmetric z-update.  The internal project implementation uses a
price-normalized, warm-started ADMM with specific residual scaling.  Iteration
counts and residual values from `scripts/run_main_case.py` may differ from the
paper-reported values (Table 3).  The **pre-computed tables** in `results/tables/`
record the exact paper values.

## Disclosure metrics

The observable exposure score is a heuristic metric for quantifying
information leakage in ADMM coordination messages.  It does **not** constitute
a formal privacy proof.  Formal differential privacy analysis requires
additional mathematical machinery beyond the scope of this manuscript.

## Data

No real refinery operating data are used or implied.  All parameters are
derived from the public benchmark.

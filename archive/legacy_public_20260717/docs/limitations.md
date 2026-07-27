# Limitations

## Case scope

The numerical results are derived from a single **public-benchmark-derived
dual-refinery coordination case** constructed from publicly available benchmark
parameters.  They are **not** generalisable to:

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

The reader repository is not the numerical authority.  The historical
internal H3B implementation uses a price-normalized, warm-started ADMM and a
proportional capacity rescaling in its coordinator step; that reproduces the
historical 32-iteration value but is not the Euclidean projection of the
declared quadratic z-subproblem.  The authoritative reconstruction branch
keeps both the historical result and a separately labelled Euclidean-
projection forensic reference.  Do not describe the historical value as
strictly equivalent to the centralized LP.

## Disclosure metrics

The observable exposure score is a heuristic metric for quantifying
information leakage in ADMM coordination messages.  It does **not** constitute
a formal privacy proof.  Formal differential privacy analysis requires
additional mathematical machinery beyond the scope of this manuscript.

## Data

No real refinery operating data are used or implied.  All parameters are
derived from the public benchmark.

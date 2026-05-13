# Parameter provenance

All case parameters are derived from the publicly available refinery-petrochemical
production planning benchmark (Case 3):

> Wenli Du et al. A production planning benchmark for real-world refinery-petrochemical
> complexes. arXiv:2503.22057, 2025.
> https://github.com/EMRPS/refinery-planning-benchmark

## Stream assignment

Two subsets of Case 3 streams are selected to form the two-refinery case:

| Stream | Plant | Price (CNY/kt) | fv_min (kt) | fv_max (kt) | Benchmark source |
|--------|-------|---------------|-------------|-------------|------------------|
| s147 | A | 8,520,000 | 0.00 | 0.94 | c_P(s147), FVMax(s147,1) |
| s158 | A | 7,180,000 | 0.00 | 0.57 | c_P(s158), FVMax(s158,1) |
| s53  | A | 6,800,000 | 0.00 | 0.74 | c_P(s53),  FVMax(s53,1)  |
| s61  | A | 6,080,000 | 0.00 | 0.70 | c_P(s61),  FVMax(s61,1)  |
| s545 | A | 4,965,000 | 0.26 | 0.27 | c_P(s545), FVMax(s545,1) |
| s36  | B | 7,600,000 | 0.00 | 0.43 | c_P(s36),  FVMax(s36,1)  |
| s391 | B | 7,100,000 | 0.00 | 1.84 | c_P(s391), FVMax(s391,1) |
| s455 | B | 6,780,000 | 0.00 | 2.00 | c_P(s455), FVMax(s455,1) |
| s376 | B | 5,828,000 | 0.00 | 0.49 | c_P(s376), FVMax(s376,1) |
| s65  | B | 4,730,000 | 0.00 | 0.17 | c_P(s65),  FVMax(s65,1)  |

## Model construction

The stream selection creates a "strong-complementarity counterfactual" scenario:
- Plant A has high-price but capacity-limited streams (s147 is the highest-value stream).
- Plant B has lower prices but substantially more capacity (s455: 2.0 kt, s391: 1.84 kt).
- Total system capacity: 8.15 kt = sum of all fv_max values.

In the coordinated model each stream's upper bound is doubled (to 2 × fv_max),
and the joint optimiser reallocates capacity to the highest-value streams.

## Design principle

The case is designed to study the methodology (ADMM + disclosure control) under
clearly positive complementarity, not to estimate the profit of any real refinery.
Results are not generalisable to arbitrary refinery pairs.

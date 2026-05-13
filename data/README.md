# Data provenance

This repository does **not** redistribute the original benchmark files.

The original refinery-petrochemical production planning benchmark is available from:

> https://github.com/EMRPS/refinery-planning-benchmark

Please cite the upstream benchmark when using this repository:

> Wenli Du, Chuan Wang, Chen Fan, Zhi Li, Yeke Zhong, Tianao Kang, Ziting Liang,
> Minglei Yang, Feng Qian, Xin Dai.
> A production planning benchmark for real-world refinery-petrochemical complexes.
> arXiv:2503.22057, 2025.

## Derived parameters (`data/derived/`)

The files under `data/derived/` contain reformatted, aggregated, and simplified
parameter subsets derived from the Case3 benchmark. They include:

| File | Description |
|------|-------------|
| `h15_case_summary.csv` | High-level case structure summary |
| `candidate_exchange_flows.csv` | Candidate stream flow bounds used in the case |
| `economic_sensitivity_settings.csv` | Exchange-cost perturbation settings for Table 6 |
| `disclosure_weight_schemes.csv` | Exposure-score weight schemes for Table 5 |

These files do **not** contain confidential industrial data and are provided solely
for non-commercial academic reproducibility of the associated manuscript.
See `DATA_LICENSE.md` for terms.

## Placing raw benchmark files

If you wish to run the scripts against the full benchmark (not required for the
paper's tables):

1. Clone the upstream repository:
   ```
   git clone https://github.com/EMRPS/refinery-planning-benchmark
   ```
2. Place the `case3/` directory under `data/raw/` in this repository.
3. `data/raw/` is listed in `.gitignore` and will not be committed.

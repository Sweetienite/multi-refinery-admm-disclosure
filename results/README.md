# Results

Pre-computed result tables from the manuscript.

## Tables

| File | Paper table | Description |
|------|-------------|-------------|
| `tables/table2_system_profit.csv` | Table 2 | System profit, ADMM approximation, IR interval |
| `tables/table3_admm_convergence.csv` | Table 3 | ADMM parameters and convergence results |
| `tables/table4_disclosure_tradeoff.csv` | Table 4 | Utility–exposure tradeoff |
| `tables/table5_weight_sensitivity.csv` | Table 5 | Exposure score weight sensitivity |
| `tables/table6_economic_sensitivity.csv` | Table 6 | Economic parameter sensitivity |

## Figures

| File | Paper figure | Description |
|------|-------------|-------------|
| `figures/fig1_methodology_flowchart.png` | Figure 1 | Methodology flowchart (manually drawn) |
| `figures/fig2_profit_comparison.png` | Figure 2 | Standalone vs coordinated profit |
| `figures/fig3_ir_interval.png` | Figure 3 | Individual-rationality interval |
| `figures/fig4_disclosure_tradeoff.png` | Figure 4 | Utility–exposure tradeoff scatter |
| `figures/fig5_economic_sensitivity.png` | Figure 5 | Economic sensitivity line chart |

## Verification

Run `python scripts/verify_reported_results.py` to check that
the pre-computed tables match `expected_metrics.json`.

Run `python scripts/reproduce_all.py` to regenerate all tables and figures
from scratch using the case parameters in `configs/main_case.yaml`.

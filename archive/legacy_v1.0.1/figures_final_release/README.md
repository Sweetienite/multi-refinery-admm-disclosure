# figures_final_release

This package contains the final figure-generation assets used for the submitted manuscript revision. It is the authoritative final package for Figures 2–6 under the repository version label `v1.0.1-paper-submission`.

## Contents
- `results/`: final exported PNG figures used in the manuscript, plus a contact sheet for quick review.
- `source/plot_revised_figures_v2.py`: final plotting script used to generate the refined figures.
- `source/validate_data.py`: input-data consistency check script.
- `source/data/`: frozen CSV input data used by the plotting script.
- `source/source_index.md`: upstream public-source commit and program-to-figure mapping.
- `release_manifest.json`: checksums and rendered-file metadata for the final exports.

## Final figures included
- fig2a_total_profit.png
- fig2b_coordination_value.png
- fig3a_residuals.png
- fig3b_capacity_allocation.png
- fig4_compensation_interval.png
- fig5_utility_exposure.png
- fig6a_exchange_cost.png
- fig6b_exchange_capacity.png
- fig6c_price_spread.png

## Notes
- These are the final refined figures prepared for the final manuscript formatting stage. They have a white opaque RGB background and 600 dpi metadata.
- The plotting script reads CSV files from `source/data/`. By default it writes to `results/`; use `--output-dir` to regenerate elsewhere without overwriting the archived final exports.
- The script uses Songti and Times New Roman if those fonts are installed; it falls back to locally available serif fonts only when necessary. The published `results/` files are the frozen final exports.
- Run `python source/validate_data.py` before regeneration. The check verifies the reported numerical anchors, including all 32 ADMM iterations.

# Result lineage and projection audit

This reader-facing note prevents three different evidence chains from being
merged into one number:

| Chain | Exact status |
|---|---|
| Historical H3B | `60,288,563.636` CNY is reproducible from the committed proportional `z` rescaling, with 32 iterations and a `113,136.364` CNY gap to H2F. It is a historical implementation result, not a strict LP-equivalence proof. |
| Corrected reference | The authoritative branch changes only the coordinator projection to the Euclidean simplex projection. At `abs_tol=1e-7` it reaches `60,401,701.135` CNY, about `1.135` CNY from H2F; this is a forensic reference and does not overwrite the historical trace. |
| H4D1R counts | The current row-level audit is `60/26/16`. The manuscript/H5 `60/24/15` appears only in historical documentation/constants; the old row-level CSV is not present in either repository. |
| H5 exposure values | `0.285`, `0.273`, `69.35%`, and `70.65%` are reproducible from fixed center-value constants in the H5 neighborhood script. They are historical approximations, not current per-rho trace recomputations. |

The full source-backed report and executable check are linked from the pinned
authoritative branch:

```bash
python scripts/current/run_h3b_projection_forensic.py
python -m pytest -q tests/test_h3b_supplement_reproducibility.py tests/test_h3b_projection_forensic.py
```

The physical interpretation remains limited to a benchmark-derived
shared-capacity allocation model.  No send/receive variable, direction,
conservation, transport cost, receiving-unit constraint, or real pipeline
capacity is present.

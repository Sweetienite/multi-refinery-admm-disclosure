# Result lineage and projection audit

This reader-facing note prevents three different evidence chains from being
merged into one number:

| Chain | Exact status |
|---|---|
| Historical H3B | `60,288,563.636` CNY is reproducible from the committed proportional `z` rescaling, with 32 iterations and a `113,136.364` CNY gap to H2F. It is a historical implementation result, not a strict LP-equivalence proof. |
| Corrected reference | The authoritative branch changes only the coordinator projection to the Euclidean simplex projection. At `abs_tol=1e-7` it reaches `60,401,701.135` CNY, about `1.135` CNY from H2F; this is a forensic reference and does not overwrite the historical trace. |
| H4D1R counts | The current row-level audit is `60/26/16`. The manuscript/H5 `60/24/15` appears only in historical documentation/constants; the old row-level CSV is not present in either repository. |
| Corrected full H4D1 chain | The same Euclidean projection was carried through the complete `4 modes × 3 seeds × 5 rho = 60` grid. Under the historical `max_iter=500, abs_tol=1e-3` protocol it yields `60/16/16` (total/converged/eligible); these rows are stored separately from the historical `60/26/16` table. |
| H5 exposure values | `0.285`, `0.273`, `69.35%`, and `70.65%` are reproducible from fixed center-value constants in the H5 neighborhood script. They are historical approximations, not current per-rho trace recomputations. |

The full source-backed report and executable check are linked from the pinned
authoritative branch:

```bash
python scripts/current/run_h3b_projection_forensic.py
python scripts/current/run_corrected_case4l_chain_forensic.py
python -m pytest -q tests/test_h3b_supplement_reproducibility.py tests/test_h3b_projection_forensic.py
```

The corrected-chain command writes a separate
`results/FORENSIC_20260715/corrected_case4l_chain_20260715/` tree, including
all 60 corrected raw/public traces, exposure components, a matched-rho table,
and a SHA-256 manifest. The tight corrected H3B reference is the comparison
baseline; the coarse corrected sweep is retained only as a stopping-rule
diagnostic because its `rho=0.1` run stops above H2F.

The physical interpretation remains limited to a benchmark-derived
shared-capacity allocation model.  No send/receive variable, direction,
conservation, transport cost, receiving-unit constraint, or real pipeline
capacity is present.

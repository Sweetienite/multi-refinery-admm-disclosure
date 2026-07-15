# Authoritative Case4-L numerical reconstruction

The manuscript-equivalent numerical evidence is maintained in exactly one
place: the
[`rebuild/missing-evidence-20260715` branch of the benchmark-derived repository](https://github.com/Sweetienite/-benchmark-derived-/tree/rebuild/missing-evidence-20260715).
The audited revision is pinned to commit
[`b9bcfdcf6c5217dd5918af08454e1fafa2d3dd82`](https://github.com/Sweetienite/-benchmark-derived-/tree/b9bcfdcf6c5217dd5918af08454e1fafa2d3dd82).

It rebuilds and checks the following chain from versioned inputs:

1. HiGHS standalone and centralized LP solutions, with independent LP/MPS
   replay;
2. the individual-rationality transfer interval;
3. the historical 32-iteration H3B distributed trace, its gap to the
   centralized reference, and a separately recorded Euclidean-projection
   forensic reference;
4. 60 historical disclosure traces and their run-level eligibility audit;
5. a separate Euclidean-projection rerun of the complete 60-run disclosure grid,
   with matched-rho exposure tables and per-run traces; and
6. the machine-readable reconstruction gate.

To reproduce the numerical evidence:

```bash
git clone https://github.com/Sweetienite/-benchmark-derived-.git
cd -benchmark-derived-
git checkout b9bcfdcf6c5217dd5918af08454e1fafa2d3dd82
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python scripts/current/run_rebuild_20260715.py
# Optional numerical-difference forensic chain (does not overwrite historical results)
python scripts/current/run_corrected_case4l_chain_forensic.py
```

Use Python 3.10 or newer.  A successful run ends with `PASS`; the status file
is `results/REBUILD_20260715/reconstruction_gate.json`.

The compact `src/admm_capacity_sharing.py` in this reader repository is not the
algorithm that generated the manuscript Table 3/disclosure evidence and must
not be used as a substitute.  Similarly, the frozen Tables 2–6 and Figures 2–6
here are release artifacts: they can be validated, but are not independent
numerical reconstructions.

The reconstruction branch also states the necessary limits on interpretation:
the case is a shared-capacity allocation benchmark, objective values are not
observed enterprise profits, and disclosure results are empirical
trace-based observable-exposure measurements rather than formal privacy
guarantees. It preserves the historical H5 count `60/24/15` as a document
snapshot, the historical row-level audit `60/26/16`, and the separate corrected
projection audit `60/16/16`; the old H4D1R CSV behind `24/15` was not committed.
These are provenance labels, not interchangeable replacements.

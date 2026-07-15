# Authoritative Case4-L numerical reconstruction

The manuscript-equivalent numerical evidence is maintained in exactly one
place: the
[`rebuild/missing-evidence-20260715` branch of the benchmark-derived repository](https://github.com/Sweetienite/-benchmark-derived-/tree/rebuild/missing-evidence-20260715).
The audited revision is pinned to commit
[`46c8bf5977f0f9d832fca268586224d8acacb8b4`](https://github.com/Sweetienite/-benchmark-derived-/tree/46c8bf5977f0f9d832fca268586224d8acacb8b4).

It rebuilds and checks the following chain from versioned inputs:

1. HiGHS standalone and centralized LP solutions, with independent LP/MPS
   replay;
2. the individual-rationality transfer interval;
3. the 32-iteration H3B distributed trace and its gap to the centralized
   reference;
4. 60 disclosure traces and their run-level eligibility audit; and
5. the machine-readable reconstruction gate.

To reproduce the numerical evidence:

```bash
git clone https://github.com/Sweetienite/-benchmark-derived-.git
cd -benchmark-derived-
git checkout 46c8bf5977f0f9d832fca268586224d8acacb8b4
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python scripts/current/run_rebuild_20260715.py
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
guarantees.

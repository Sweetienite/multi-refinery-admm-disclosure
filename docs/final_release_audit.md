# Public-release audit scope

## What the manuscript availability statement covers

This repository publishes the public-parameter-derived case, scripts, and
reported-result summaries used for Tables 2–6 and Figures 2–6. It contains no
enterprise production data, operational records, or confidential information.

| Item | Authoritative public location | Check |
|---|---|---|
| Tables 2–6 | `results/tables/`, `results/expected_metrics.json` | `scripts/verify_reported_results.py` |
| Final Figure 2–6 panels | `figures_final_release/results/` | RGB, white opaque, 600 dpi, SHA-256 manifest |
| Final figure inputs and renderer | `figures_final_release/source/` | `validate_data.py`; rerender to a caller-selected directory |
| Public parameter provenance and final-data mapping | `figures_final_release/source/source_index.md` | Public benchmark link, local frozen CSVs, and local renderer |

## Source boundary

The public benchmark source is
[`EMRPS/refinery-planning-benchmark`](https://github.com/EMRPS/refinery-planning-benchmark),
including its public
[`case3/case3.gms`](https://github.com/EMRPS/refinery-planning-benchmark/blob/main/case3/case3.gms)
file. The index maps every final panel to a CSV and renderer shipped in this
repository. It does not require readers to access a private development
repository or environment.

## Compact diagnostics versus submitted artifacts

`src/` and the `scripts/run_*.py` commands provide independently runnable
compact diagnostics. They write beneath `results/generated/` by default.
They must not be used to replace the frozen manuscript tables or final PNGs.
The 32-iteration trajectory and full economic-sensitivity series are frozen
public result summaries supplied with the final plotting inputs.

## Recheck commands

```bash
python scripts/verify_reported_results.py
python figures_final_release/source/validate_data.py
python scripts/validate_public_release.py
python scripts/make_figures.py --output-dir /tmp/final-figure-render
```

The GitHub Actions workflow runs the first three checks, together with unit
tests for the compact model.

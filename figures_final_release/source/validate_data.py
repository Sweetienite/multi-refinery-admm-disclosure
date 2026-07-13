#!/usr/bin/env python3
"""Guard the frozen plot-input CSVs against accidental data edits."""
from __future__ import annotations

import csv
from pathlib import Path


DATA = Path(__file__).resolve().parent / "data"


def read(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def values(name: str, field: str) -> list[float]:
    return [float(row[field]) for row in read(name)]


def close(actual: float, expected: float, tolerance: float = 1e-10) -> None:
    assert abs(actual - expected) <= tolerance, (actual, expected)


def main() -> None:
    for actual, expected in zip(values("fig2_total_profit.csv", "profit_million"),
                                [56.28177, 60.4017, 60.28856364]):
        close(actual, expected)
    for actual, expected in zip(values("fig2_coordination_value.csv", "value_million"),
                                [4.11993, 0.11313636]):
        close(actual, expected)

    trace = read("fig3_admm_trace.csv")
    assert len(trace) == 32
    assert [int(row["iteration"]) for row in trace] == list(range(1, 33))
    close(float(trace[-1]["primal_residual"]), 7.109726048737386e-05, 1e-14)
    close(float(trace[-1]["dual_residual"]), 4.168652323111033e-07, 1e-16)

    for actual, expected in zip(values("fig4_compensation_interval.csv", "value_million"),
                                [-5.00775, -0.88782, 0.0]):
        close(actual, expected)
    for actual, expected in zip(values("fig5_utility_exposure.csv", "exposure_score"),
                                [0.93, 0.285, 0.273]):
        close(actual, expected)
    for actual, expected in zip(values("fig5_utility_exposure.csv", "utility_retention"),
                                [1.0, 0.9997, 0.9976]):
        close(actual, expected)

    figure6 = read("fig6_economic_sensitivity.csv")
    assert len(figure6) == 11
    expected = {
        ("交换成本乘数", "0.80"): 4.12313,
        ("交换成本乘数", "0.90"): 4.12153,
        ("交换成本乘数", "1.00"): 4.11993,
        ("交换成本乘数", "1.10"): 4.11833,
        ("交换成本乘数", "1.20"): 4.11673,
        ("交换容量乘数", "0.90"): 4.0787307,
        ("交换容量乘数", "1.00"): 4.11993,
        ("交换容量乘数", "1.10"): 4.11993,
        ("价差乘数", "0.90"): 3.707937,
        ("价差乘数", "1.00"): 4.11993,
        ("价差乘数", "1.10"): 4.531923,
    }
    for row in figure6:
        close(float(row["coordination_value_million"]), expected[(row["parameter"], row["multiplier"])])
    print("All figure input checks passed.")


if __name__ == "__main__":
    main()

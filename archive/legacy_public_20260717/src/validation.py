"""
validation.py — Verify computed results against reported paper values.

Compares output from the run scripts against the expected metrics stored in
``results/expected_metrics.json``.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# Relative tolerance for numerical comparisons
DEFAULT_RTOL = 1e-3   # 0.1%
DEFAULT_ATOL = 1.0    # 1 CNY absolute tolerance


@dataclass
class CheckResult:
    name: str
    expected: float
    actual: float
    rel_error: float
    passed: bool
    message: str


def check_value(
    name: str,
    expected: float,
    actual: float,
    rtol: float = DEFAULT_RTOL,
    atol: float = DEFAULT_ATOL,
) -> CheckResult:
    """Compare actual to expected with relative and absolute tolerance."""
    abs_err = abs(actual - expected)
    rel_err = abs_err / max(abs(expected), 1e-12)
    passed = abs_err <= atol or rel_err <= rtol
    msg = (
        f"PASS: {name} = {actual:.4f} (expected {expected:.4f}, "
        f"rel_err = {rel_err*100:.4f}%)"
        if passed
        else f"FAIL: {name} = {actual:.4f} (expected {expected:.4f}, "
             f"rel_err = {rel_err*100:.4f}% > rtol={rtol*100}%)"
    )
    return CheckResult(name=name, expected=expected, actual=actual,
                       rel_error=rel_err, passed=passed, message=msg)


def load_expected_metrics(results_dir: str | Path = "results") -> dict[str, Any]:
    path = Path(results_dir) / "expected_metrics.json"
    if not path.exists():
        raise FileNotFoundError(f"Expected metrics not found: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def verify_results(
    computed: dict[str, float],
    results_dir: str | Path = "results",
    rtol: float = DEFAULT_RTOL,
) -> tuple[list[CheckResult], bool]:
    """
    Verify computed metrics against stored expected values.

    Parameters
    ----------
    computed : dict
        Dictionary of metric_name -> computed_value.
    results_dir : str or Path
        Directory containing expected_metrics.json.
    rtol : float
        Relative tolerance.

    Returns
    -------
    checks : list of CheckResult
    all_passed : bool
    """
    expected = load_expected_metrics(results_dir)
    checks: list[CheckResult] = []

    for key, exp_val in expected.items():
        if not isinstance(exp_val, (int, float)):
            continue
        if key not in computed:
            checks.append(CheckResult(
                name=key, expected=float(exp_val), actual=float("nan"),
                rel_error=float("nan"), passed=False,
                message=f"MISSING: {key} not found in computed results",
            ))
            continue
        checks.append(check_value(key, float(exp_val), float(computed[key]), rtol=rtol))

    all_passed = all(c.passed for c in checks)
    return checks, all_passed


def print_verification_report(checks: list[CheckResult]) -> None:
    """Print a human-readable verification report."""
    passed = sum(1 for c in checks if c.passed)
    total = len(checks)
    print(f"\n{'='*60}")
    print(f"Verification report: {passed}/{total} checks passed")
    print(f"{'='*60}")
    for c in checks:
        print(c.message)
    print(f"{'='*60}\n")
    if passed < total:
        raise AssertionError(f"{total - passed} verification check(s) failed.")

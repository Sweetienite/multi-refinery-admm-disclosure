"""
tests/test_disclosure_metrics.py — Unit tests for exposure metrics.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.disclosure_metrics import (
    DisclosureMessage,
    compute_exposure_score,
    messages_from_history_none,
    messages_from_history_ts_ladder,
    messages_from_history_bucketing,
)


STREAMS = ["s1", "s2", "s3"]
CAP = {"s1": 1.0, "s2": 2.0, "s3": 1.5}
FLOWS_ITER = [{"s1": 0.9, "s2": 1.8, "s3": 1.0},
              {"s1": 0.8, "s2": 1.7, "s3": 0.9}]


def test_exposure_none_is_high():
    msgs = messages_from_history_none(FLOWS_ITER, CAP)
    result = compute_exposure_score(msgs, STREAMS, mechanism="none")
    assert result.total_score > 0.5, "No-control mechanism should have high exposure"


def test_ts_ladder_reduces_exposure():
    msgs_none = messages_from_history_none(FLOWS_ITER, CAP)
    msgs_ts = messages_from_history_ts_ladder(FLOWS_ITER, CAP)
    score_none = compute_exposure_score(msgs_none, STREAMS, mechanism="none")
    score_ts = compute_exposure_score(msgs_ts, STREAMS, mechanism="ts_ladder")
    assert score_ts.total_score < score_none.total_score, (
        "ts_ladder should reduce exposure vs no-control"
    )


def test_bucketing_reduces_exposure():
    msgs_none = messages_from_history_none(FLOWS_ITER, CAP)
    msgs_bucket = messages_from_history_bucketing(FLOWS_ITER, CAP)
    score_none = compute_exposure_score(msgs_none, STREAMS, mechanism="none")
    score_bucket = compute_exposure_score(msgs_bucket, STREAMS, mechanism="bucketing")
    assert score_bucket.total_score < score_none.total_score, (
        "bucketing should reduce exposure vs no-control"
    )


def test_exposure_score_components_sum():
    """Weighted sum of components must equal total_score."""
    msgs = messages_from_history_none(FLOWS_ITER, CAP)
    result = compute_exposure_score(msgs, STREAMS)
    expected = sum(result.weights[k] * result.components[k] for k in result.components)
    assert abs(result.total_score - expected) < 1e-9


def test_empty_messages_returns_zero():
    result = compute_exposure_score([], STREAMS)
    assert result.total_score == 0.0


def test_exposure_score_in_range():
    msgs = messages_from_history_none(FLOWS_ITER, CAP)
    result = compute_exposure_score(msgs, STREAMS)
    assert 0.0 <= result.total_score <= 1.0 + 1e-9

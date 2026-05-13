"""
disclosure_metrics.py — Observable commercial information exposure metrics.

Computes the observable exposure score for ADMM coordination messages under
different disclosure-control mechanisms.

Mechanisms implemented:
  - ``none``       : No disclosure control (baseline, full trajectory visible)
  - ``ts_ladder``  : Adaptive threshold-ladder mechanism (main paper mechanism)
  - ``bucketing``  : Stream-bucketing mechanism (alternative main mechanism)
  - ``hard_mask``  : Hard-masking (strong restriction, boundary case)

Exposure score components (5 dimensions):
  1. direct_exposure      : exact values revealed in messages
  2. corridor_exposure    : narrow intervals that reveal capacity corridors
  3. temporal_exposure    : pattern revealed across iterations
  4. bottleneck_exposure  : bottleneck stream identities revealed
  5. side_exposure        : side-channel inference via message structure

Default weights: [0.25, 0.20, 0.20, 0.20, 0.15]
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Weights
# ---------------------------------------------------------------------------

DEFAULT_WEIGHTS = {
    "direct": 0.25,
    "corridor": 0.20,
    "temporal": 0.20,
    "bottleneck": 0.20,
    "side": 0.15,
}

WEIGHT_SCHEMES: dict[str, dict[str, float]] = {
    "main": {"direct": 0.25, "corridor": 0.20, "temporal": 0.20, "bottleneck": 0.20, "side": 0.15},
    "uniform": {"direct": 0.20, "corridor": 0.20, "temporal": 0.20, "bottleneck": 0.20, "side": 0.20},
    "direct_heavy": {"direct": 0.40, "corridor": 0.15, "temporal": 0.15, "bottleneck": 0.15, "side": 0.15},
    "trajectory_heavy": {"direct": 0.15, "corridor": 0.15, "temporal": 0.25, "bottleneck": 0.25, "side": 0.20},
    "side_heavy": {"direct": 0.15, "corridor": 0.15, "temporal": 0.15, "bottleneck": 0.20, "side": 0.35},
}


# ---------------------------------------------------------------------------
# Message representation
# ---------------------------------------------------------------------------

@dataclass
class DisclosureMessage:
    """
    Representation of one ADMM coordination message exchanged per iteration.

    Fields record what is visible to an observer of the public message channel.
    """
    iteration: int
    # Exact values visible in the message (stream -> value)
    exact_values: dict[str, float] = field(default_factory=dict)
    # Interval bounds visible (stream -> (lower, upper))
    interval_bounds: dict[str, tuple[float, float]] = field(default_factory=dict)
    # Bucket indices visible (stream -> bucket_id)
    bucket_indices: dict[str, int] = field(default_factory=dict)
    # Masked streams (identity hidden)
    masked_streams: set[str] = field(default_factory=set)
    # Capacity bound used for normalisation (stream -> cap)
    capacity_bounds: dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Per-component exposure calculators
# ---------------------------------------------------------------------------

def _direct_score(message: DisclosureMessage, all_streams: list[str]) -> float:
    n = max(1, len(all_streams))
    exact_visible = set(message.exact_values) - message.masked_streams
    return len(exact_visible) / n


def _corridor_score(message: DisclosureMessage, all_streams: list[str]) -> float:
    n = max(1, len(all_streams))
    score = 0.0
    for s, (lo, hi) in message.interval_bounds.items():
        if s in message.masked_streams:
            continue
        cap = message.capacity_bounds.get(s, 1.0) or 1.0
        width = max(0.0, hi - lo)
        narrowness = max(0.0, 1.0 - width / cap)
        score += narrowness
    return score / n


def _temporal_score(
    messages: list[DisclosureMessage], all_streams: list[str]
) -> float:
    """
    Temporal exposure: fraction of streams whose trajectory is recoverable
    from the sequence of messages.
    """
    n = max(1, len(all_streams))
    trajectory_revealed: set[str] = set()
    for msg in messages:
        for s in msg.exact_values:
            if s not in msg.masked_streams:
                trajectory_revealed.add(s)
        for s in msg.interval_bounds:
            if s not in msg.masked_streams:
                cap = msg.capacity_bounds.get(s, 1.0) or 1.0
                lo, hi = msg.interval_bounds[s]
                if (hi - lo) / cap < 0.1:
                    trajectory_revealed.add(s)
    return len(trajectory_revealed) / n


def _bottleneck_score(message: DisclosureMessage, all_streams: list[str]) -> float:
    n = max(1, len(all_streams))
    revealed_bottlenecks = {
        s for s in message.exact_values
        if s not in message.masked_streams
        and message.exact_values[s] >= 0.95 * message.capacity_bounds.get(s, float("inf"))
    }
    return len(revealed_bottlenecks) / n


def _side_score(message: DisclosureMessage, all_streams: list[str]) -> float:
    n = max(1, len(all_streams))
    # Side-channel: visible stream count reveals active-set size
    visible = (set(message.exact_values) | set(message.interval_bounds)) - message.masked_streams
    return len(visible) / n


# ---------------------------------------------------------------------------
# Aggregate exposure score
# ---------------------------------------------------------------------------

@dataclass
class ExposureScoreResult:
    """Composite observable exposure score for a run."""
    total_score: float
    components: dict[str, float]
    weights: dict[str, float]
    mechanism: str


def compute_exposure_score(
    messages: list[DisclosureMessage],
    all_streams: list[str],
    mechanism: str = "none",
    weight_scheme: str = "main",
) -> ExposureScoreResult:
    """
    Compute the composite observable exposure score for an ADMM run.

    Parameters
    ----------
    messages : list of DisclosureMessage
        All coordination messages produced in the run.
    all_streams : list of str
        Complete set of candidate exchange stream identifiers.
    mechanism : str
        Disclosure mechanism label (for bookkeeping).
    weight_scheme : str
        Key into WEIGHT_SCHEMES; defaults to "main".

    Returns
    -------
    ExposureScoreResult
    """
    weights = WEIGHT_SCHEMES.get(weight_scheme, DEFAULT_WEIGHTS)
    if not messages:
        components = {k: 0.0 for k in weights}
        return ExposureScoreResult(0.0, components, weights, mechanism)

    # Average direct, corridor, bottleneck, side across iterations
    direct_scores = [_direct_score(m, all_streams) for m in messages]
    corridor_scores = [_corridor_score(m, all_streams) for m in messages]
    bottleneck_scores = [_bottleneck_score(m, all_streams) for m in messages]
    side_scores = [_side_score(m, all_streams) for m in messages]

    avg = lambda lst: sum(lst) / len(lst) if lst else 0.0

    components = {
        "direct": avg(direct_scores),
        "corridor": avg(corridor_scores),
        "temporal": _temporal_score(messages, all_streams),
        "bottleneck": avg(bottleneck_scores),
        "side": avg(side_scores),
    }

    total = sum(weights.get(k, 0.0) * v for k, v in components.items())
    return ExposureScoreResult(
        total_score=total,
        components=components,
        weights=weights,
        mechanism=mechanism,
    )


# ---------------------------------------------------------------------------
# Mechanism simulators (produce messages from ADMM history)
# ---------------------------------------------------------------------------

def messages_from_history_none(
    exchange_flows_per_iter: list[dict[str, float]],
    capacity_bounds: dict[str, float],
) -> list[DisclosureMessage]:
    """No disclosure control — all exact values visible."""
    messages = []
    for i, flows in enumerate(exchange_flows_per_iter):
        messages.append(DisclosureMessage(
            iteration=i,
            exact_values=dict(flows),
            capacity_bounds=capacity_bounds,
        ))
    return messages


def messages_from_history_ts_ladder(
    exchange_flows_per_iter: list[dict[str, float]],
    capacity_bounds: dict[str, float],
    threshold_ratio: float = 0.15,
    bucket_width_ratio: float = 0.10,
) -> list[DisclosureMessage]:
    """
    Adaptive threshold-ladder mechanism.

    Streams with flow below ``threshold_ratio * cap`` are masked; others are
    reported as interval [floor, ceil] of width ``bucket_width_ratio * cap``.
    """
    messages = []
    for i, flows in enumerate(exchange_flows_per_iter):
        exact: dict[str, float] = {}
        intervals: dict[str, tuple[float, float]] = {}
        masked: set[str] = set()
        for s, v in flows.items():
            cap = capacity_bounds.get(s, 1.0) or 1.0
            if v < threshold_ratio * cap:
                masked.add(s)
            else:
                bw = bucket_width_ratio * cap
                lo = math.floor(v / bw) * bw
                hi = lo + bw
                intervals[s] = (lo, hi)
        messages.append(DisclosureMessage(
            iteration=i,
            interval_bounds=intervals,
            masked_streams=masked,
            capacity_bounds=capacity_bounds,
        ))
    return messages


def messages_from_history_bucketing(
    exchange_flows_per_iter: list[dict[str, float]],
    capacity_bounds: dict[str, float],
    n_buckets: int = 5,
) -> list[DisclosureMessage]:
    """
    Stream-bucketing mechanism.

    Each stream value is quantised into one of ``n_buckets`` equal-width buckets.
    The bucket index is reported instead of the exact value.
    """
    messages = []
    for i, flows in enumerate(exchange_flows_per_iter):
        buckets: dict[str, int] = {}
        intervals: dict[str, tuple[float, float]] = {}
        for s, v in flows.items():
            cap = capacity_bounds.get(s, 1.0) or 1.0
            bw = cap / n_buckets
            idx = min(n_buckets - 1, int(v / bw))
            buckets[s] = idx
            lo = idx * bw
            hi = (idx + 1) * bw
            intervals[s] = (lo, hi)
        messages.append(DisclosureMessage(
            iteration=i,
            bucket_indices=buckets,
            interval_bounds=intervals,
            capacity_bounds=capacity_bounds,
        ))
    return messages

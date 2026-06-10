"""Aggregate metrics across a batch of diff results.

Produces the report's headline numbers: % matching, latency delta, error-rate
delta, and a breakdown of divergence categories.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Sequence

from .models import DiffResult


@dataclass(frozen=True)
class BatchMetrics:
    total: int
    matched: int
    match_pct: float
    mean_prod_latency_ms: float
    mean_shadow_latency_ms: float
    latency_delta_ms: float
    prod_error_rate: float
    shadow_error_rate: float
    error_rate_delta: float
    category_counts: dict


def aggregate(results: Sequence[DiffResult]) -> BatchMetrics:
    """Aggregate a non-empty sequence of diff results into batch metrics."""
    total = len(results)
    if total == 0:
        raise ValueError("cannot aggregate an empty batch")

    matched = sum(1 for r in results if r.matched)
    prod_errors = sum(1 for r in results if r.prod_status >= 400)
    shadow_errors = sum(1 for r in results if r.shadow_status >= 400)

    mean_prod = sum(r.prod_latency_ms for r in results) / total
    mean_shadow = sum(r.shadow_latency_ms for r in results) / total

    counts: Counter = Counter()
    for r in results:
        for d in r.diffs:
            counts[d.category.value] += 1

    prod_err_rate = prod_errors / total
    shadow_err_rate = shadow_errors / total

    return BatchMetrics(
        total=total,
        matched=matched,
        match_pct=round(100.0 * matched / total, 4),
        mean_prod_latency_ms=round(mean_prod, 4),
        mean_shadow_latency_ms=round(mean_shadow, 4),
        latency_delta_ms=round(mean_shadow - mean_prod, 4),
        prod_error_rate=round(prod_err_rate, 4),
        shadow_error_rate=round(shadow_err_rate, 4),
        error_rate_delta=round(shadow_err_rate - prod_err_rate, 4),
        category_counts=dict(counts),
    )

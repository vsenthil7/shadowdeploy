"""Report builder and promotion verdict logic.

Turns a batch of diff results into a structured report and a GO/REVIEW/BLOCK
verdict. The verdict is advisory only — the human reviews it and decides
promotion (human-in-the-loop requirement). The harness never auto-promotes.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from ..core.metrics import BatchMetrics, aggregate
from ..core.models import DiffResult, Verdict

# Default thresholds — overridable via build_report.
DEFAULT_PROMOTE_MATCH_PCT = 99.0
DEFAULT_REVIEW_MATCH_PCT = 95.0
DEFAULT_MAX_ERROR_RATE_DELTA = 0.01
DEFAULT_MAX_LATENCY_DELTA_MS = 50.0


@dataclass(frozen=True)
class PromotionReport:
    metrics: BatchMetrics
    verdict: Verdict
    reasons: tuple[str, ...]


def decide_verdict(
    metrics: BatchMetrics,
    *,
    promote_match_pct: float = DEFAULT_PROMOTE_MATCH_PCT,
    review_match_pct: float = DEFAULT_REVIEW_MATCH_PCT,
    max_error_rate_delta: float = DEFAULT_MAX_ERROR_RATE_DELTA,
    max_latency_delta_ms: float = DEFAULT_MAX_LATENCY_DELTA_MS,
) -> tuple[Verdict, tuple[str, ...]]:
    """Return a verdict and the reasons that drove it.

    BLOCK if the shadow raised the error rate beyond tolerance.
    Otherwise based on match %, with latency as a downgrade-to-REVIEW signal.
    """
    reasons: list[str] = []

    if metrics.error_rate_delta > max_error_rate_delta:
        reasons.append(
            f"error-rate delta {metrics.error_rate_delta:.4f} exceeds "
            f"{max_error_rate_delta:.4f}"
        )
        return Verdict.BLOCK, tuple(reasons)

    if metrics.match_pct >= promote_match_pct:
        verdict = Verdict.PROMOTE
        reasons.append(f"match {metrics.match_pct:.2f}% >= {promote_match_pct:.2f}%")
    elif metrics.match_pct >= review_match_pct:
        verdict = Verdict.REVIEW
        reasons.append(
            f"match {metrics.match_pct:.2f}% in review band "
            f"[{review_match_pct:.2f}%, {promote_match_pct:.2f}%)"
        )
    else:
        verdict = Verdict.BLOCK
        reasons.append(f"match {metrics.match_pct:.2f}% < {review_match_pct:.2f}%")
        return verdict, tuple(reasons)

    if metrics.latency_delta_ms > max_latency_delta_ms:
        reasons.append(
            f"latency delta {metrics.latency_delta_ms:.2f}ms exceeds "
            f"{max_latency_delta_ms:.2f}ms"
        )
        if verdict is Verdict.PROMOTE:
            verdict = Verdict.REVIEW

    return verdict, tuple(reasons)


def build_report(results: Sequence[DiffResult], **thresholds) -> PromotionReport:
    """Aggregate results and attach a promotion verdict."""
    metrics = aggregate(results)
    verdict, reasons = decide_verdict(metrics, **thresholds)
    return PromotionReport(metrics=metrics, verdict=verdict, reasons=reasons)

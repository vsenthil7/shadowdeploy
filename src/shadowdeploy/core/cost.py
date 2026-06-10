"""Cost governance: estimate the added cost of shadowing and enforce caps.

Mirroring doubles compute for sampled requests. This module makes that cost
explicit (reviewer requirement: "print the added cost and keep sampling
bounded") and provides the kill-switch decision.
"""
from __future__ import annotations

from dataclasses import dataclass

from .models import MirrorConfig

# Conservative planning unit costs (USD). These are illustrative defaults;
# real numbers vary by region/service and are surfaced for human review.
DEFAULT_COST_PER_INVOKE = 0.0000002  # Lambda-ish per-invocation compute proxy
DEFAULT_S3_COST_PER_CAPTURE = 0.000005  # PUT + storage amortized per capture
DEFAULT_ATHENA_COST_PER_SCAN = 0.000001  # per-record diff scan proxy

# Standard billing-alert thresholds baked into every estimate (the prompt's
# $10/$50/$100 guardrail).
BILLING_ALERT_THRESHOLDS = (10.0, 50.0, 100.0)


@dataclass(frozen=True)
class CostEstimate:
    sampled_requests: int
    added_compute_cost: float
    capture_storage_cost: float
    diff_scan_cost: float
    total_added_cost: float
    within_budget: bool
    budget_alerts: tuple[float, ...]


def estimate_cost(
    config: MirrorConfig,
    monthly_requests: int,
    *,
    monthly_budget: float = 100.0,
    cost_per_invoke: float = DEFAULT_COST_PER_INVOKE,
    s3_cost_per_capture: float = DEFAULT_S3_COST_PER_CAPTURE,
    athena_cost_per_scan: float = DEFAULT_ATHENA_COST_PER_SCAN,
) -> CostEstimate:
    """Estimate the added monthly cost of shadowing at the configured rate."""
    if monthly_requests < 0:
        raise ValueError("monthly_requests must be non-negative")
    if monthly_budget <= 0:
        raise ValueError("monthly_budget must be positive")

    effective_rate = config.sampling_rate if config.shadow_enabled else 0.0
    sampled = int(monthly_requests * effective_rate)

    added_compute = sampled * cost_per_invoke
    capture_storage = sampled * 2 * s3_cost_per_capture  # prod + shadow capture
    diff_scan = sampled * athena_cost_per_scan
    total = added_compute + capture_storage + diff_scan

    return CostEstimate(
        sampled_requests=sampled,
        added_compute_cost=round(added_compute, 6),
        capture_storage_cost=round(capture_storage, 6),
        diff_scan_cost=round(diff_scan, 6),
        total_added_cost=round(total, 6),
        within_budget=total <= monthly_budget,
        budget_alerts=BILLING_ALERT_THRESHOLDS,
    )


def kill_switch_active(config: MirrorConfig) -> bool:
    """Return True when the one-flag disable is engaged."""
    return not config.shadow_enabled

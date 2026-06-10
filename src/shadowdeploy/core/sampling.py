"""Sampling decision logic.

Deterministic sampling keyed on the correlation id makes test traffic
reproducible and lets the same request be sampled consistently across retries.
"""
from __future__ import annotations

import hashlib

_HASH_SPACE = 1_000_000


def should_sample(correlation_id: str, sampling_rate: float, *, enabled: bool = True) -> bool:
    """Return True when this request should be mirrored to the shadow target.

    The decision is deterministic for a given ``correlation_id`` and
    ``sampling_rate`` so the same request always lands the same way.

    A ``sampling_rate`` of 0 never samples; 1.0 always samples (subject to the
    config-layer cap). ``enabled=False`` is the kill-switch and always wins.
    """
    if not enabled:
        return False
    if sampling_rate <= 0.0:
        return False
    if sampling_rate >= 1.0:
        return True
    if not correlation_id:
        raise ValueError("correlation_id required for sampling decision")
    bucket = _bucket(correlation_id)
    threshold = int(sampling_rate * _HASH_SPACE)
    return bucket < threshold


def _bucket(correlation_id: str) -> int:
    digest = hashlib.sha256(correlation_id.encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % _HASH_SPACE

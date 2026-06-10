"""Capture a request/response exchange into a persistable record.

The capture step applies PII masking before the record leaves the process, so
nothing unmasked is ever written to the diff store.
"""
from __future__ import annotations

import time
from typing import Any

from .models import CapturedExchange
from .pii import mask_body

VALID_SOURCES = ("prod", "shadow")


def capture_exchange(
    *,
    correlation_id: str,
    source: str,
    status_code: int,
    latency_ms: float,
    body: Any,
    pii_fields: tuple[str, ...] = (),
    clock=time.time,
) -> CapturedExchange:
    """Build a :class:`CapturedExchange` with PII already masked.

    ``clock`` is injectable for deterministic tests.
    """
    if source not in VALID_SOURCES:
        raise ValueError(f"source must be one of {VALID_SOURCES}, got {source!r}")
    if not correlation_id or not correlation_id.strip():
        raise ValueError("correlation_id must be non-empty")
    if latency_ms < 0:
        raise ValueError("latency_ms must be non-negative")
    if not isinstance(status_code, int) or status_code < 100 or status_code > 599:
        raise ValueError(f"status_code out of HTTP range: {status_code!r}")

    masked = mask_body(body, pii_fields)
    return CapturedExchange(
        correlation_id=correlation_id,
        source=source,
        status_code=status_code,
        latency_ms=float(latency_ms),
        body=masked,
        captured_at=float(clock()),
    )

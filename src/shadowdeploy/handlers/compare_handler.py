"""Comparison handler — pairs prod/shadow captures and produces diff results.

Runs out-of-band (e.g. triggered on S3 writes or on a schedule). It normalizes
both bodies before diffing so non-deterministic fields don't create noise.
"""
from __future__ import annotations

from typing import Iterable

from ..core.diff import compare_exchanges
from ..core.models import CapturedExchange, DiffResult, MirrorConfig
from ..core.normalize import normalize


def pair_captures(
    captures: Iterable[CapturedExchange],
) -> list[tuple[CapturedExchange, CapturedExchange]]:
    """Pair prod and shadow captures by correlation id.

    Unpaired captures (only one side present) are dropped — they can't be
    diffed. Returns pairs as ``(prod, shadow)``.
    """
    prod: dict = {}
    shadow: dict = {}
    for cap in captures:
        if cap.source == "prod":
            prod[cap.correlation_id] = cap
        elif cap.source == "shadow":
            shadow[cap.correlation_id] = cap
        else:  # pragma: no cover - capture_exchange already guards source
            raise ValueError(f"unexpected source {cap.source!r}")
    pairs = []
    for cid, p in prod.items():
        if cid in shadow:
            pairs.append((p, shadow[cid]))
    return pairs


def compare_batch(
    captures: Iterable[CapturedExchange], config: MirrorConfig
) -> list[DiffResult]:
    """Normalize, pair, and diff a batch of captures."""
    pairs = pair_captures(captures)
    results = []
    for prod, shadow in pairs:
        norm_prod = _renorm(prod, config)
        norm_shadow = _renorm(shadow, config)
        results.append(compare_exchanges(norm_prod, norm_shadow))
    return results


def _renorm(capture: CapturedExchange, config: MirrorConfig) -> CapturedExchange:
    return CapturedExchange(
        correlation_id=capture.correlation_id,
        source=capture.source,
        status_code=capture.status_code,
        latency_ms=capture.latency_ms,
        body=normalize(capture.body, config.ignore_fields),
        captured_at=capture.captured_at,
    )

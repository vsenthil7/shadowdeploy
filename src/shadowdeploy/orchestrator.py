"""End-to-end orchestration of a shadow-testing run.

Wires the pieces together: config -> (per request) sample + mirror + capture ->
compare batch -> report. This is the in-process pipeline used by the CLI and by
functional tests; in production the mirror runs in a Lambda and the compare runs
out-of-band, but the logic is identical.
"""
from __future__ import annotations

from typing import Callable, Iterable

from .core.models import CapturedExchange, MirrorConfig
from .handlers.compare_handler import compare_batch
from .handlers.mirror import handle_request
from .reporting.report import PromotionReport, build_report


def run_pipeline(
    events: Iterable[dict],
    config: MirrorConfig,
    prod_invoke: Callable[[dict], dict],
    shadow_invoke: Callable[[dict], dict],
    **thresholds,
) -> PromotionReport:
    """Run a batch of events through mirror + compare and return a report.

    Raises ``ValueError`` if no shadow captures were produced (nothing to
    compare) — surfacing the "you sampled nothing" condition explicitly rather
    than emitting an empty report.
    """
    captures: list[CapturedExchange] = []
    sink = captures.append

    for event in events:
        outcome = handle_request(
            event, config, prod_invoke, shadow_invoke, sink=_capture_only(sink)
        )
        # prod capture is on the outcome; ensure it's in the batch too
        # (sink already received it via handle_request).
        _ = outcome

    results = compare_batch(captures, config)
    if not results:
        raise ValueError(
            "no comparable prod/shadow pairs produced — "
            "check sampling_rate and shadow_enabled"
        )
    return build_report(results, **thresholds)


def _capture_only(sink):
    """Wrap a sink so only CapturedExchange records are collected.

    Shadow-error dicts emitted by the mirror are dropped from the compare batch
    but would still be logged in production.
    """
    def _inner(record):
        if isinstance(record, CapturedExchange):
            sink(record)
    return _inner

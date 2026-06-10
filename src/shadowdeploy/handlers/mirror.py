"""Mirror handler — the heart of the shadow-discard guarantee.

Production traffic flows through here. The prod response is ALWAYS what the
client receives. The shadow target is invoked only for sampled requests, and
its response is captured for diffing then DISCARDED — it can never reach the
client. This is enforced structurally: the function returns the prod response
before the shadow result is ever consulted for the return value.
"""
from __future__ import annotations

from typing import Any, Callable

from ..core.capture import capture_exchange
from ..core.correlation import extract_correlation_id
from ..core.models import MirrorConfig
from ..core.sampling import should_sample


class MirrorOutcome:
    """Result of handling one request through the mirror.

    ``client_response`` is what the client gets — always the prod response.
    ``shadow_captured`` indicates whether a shadow capture was recorded.
    """

    __slots__ = ("client_response", "prod_capture", "shadow_capture", "shadow_captured")

    def __init__(self, client_response, prod_capture, shadow_capture):
        self.client_response = client_response
        self.prod_capture = prod_capture
        self.shadow_capture = shadow_capture
        self.shadow_captured = shadow_capture is not None


def handle_request(
    event: dict,
    config: MirrorConfig,
    prod_invoke: Callable[[dict], dict],
    shadow_invoke: Callable[[dict], dict],
    *,
    sink: Callable[[Any], None] | None = None,
) -> MirrorOutcome:
    """Process one request.

    ``prod_invoke`` / ``shadow_invoke`` each take the event and return a dict
    with ``status_code``, ``latency_ms`` and ``body``.

    The shadow is invoked only if sampling selects this request AND shadowing is
    enabled. A failure in the shadow path is swallowed (logged via sink) so it
    can never affect the client — error isolation.
    """
    headers = event.get("headers") or {}
    correlation_id = extract_correlation_id(headers)

    prod_result = prod_invoke(event)
    prod_capture = capture_exchange(
        correlation_id=correlation_id,
        source="prod",
        status_code=prod_result["status_code"],
        latency_ms=prod_result["latency_ms"],
        body=prod_result["body"],
        pii_fields=config.pii_fields,
    )
    _emit(sink, prod_capture)

    # Client response is locked in here — nothing below can change it.
    client_response = prod_result

    shadow_capture = None
    if should_sample(correlation_id, config.sampling_rate, enabled=config.shadow_enabled):
        shadow_capture = _run_shadow(event, config, correlation_id, shadow_invoke, sink)

    return MirrorOutcome(client_response, prod_capture, shadow_capture)


def _run_shadow(event, config, correlation_id, shadow_invoke, sink):
    try:
        shadow_result = shadow_invoke(event)
        capture = capture_exchange(
            correlation_id=correlation_id,
            source="shadow",
            status_code=shadow_result["status_code"],
            latency_ms=shadow_result["latency_ms"],
            body=shadow_result["body"],
            pii_fields=config.pii_fields,
        )
        _emit(sink, capture)
        return capture
    except Exception as exc:  # noqa: BLE001 - error isolation is intentional
        _emit(sink, {"shadow_error": repr(exc), "correlation_id": correlation_id})
        return None


def _emit(sink, record):
    if sink is not None:
        sink(record)

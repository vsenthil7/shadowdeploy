"""Correlation ID generation and propagation.

Each mirrored request carries a correlation id so the prod and shadow captures
can be paired during diffing.
"""
from __future__ import annotations

import uuid

CORRELATION_HEADER = "x-shadowdeploy-correlation-id"


def new_correlation_id() -> str:
    """Generate a fresh correlation id."""
    return f"sd-{uuid.uuid4().hex}"


def extract_correlation_id(headers: dict | None) -> str:
    """Return the correlation id from request headers, generating one if absent.

    Header lookup is case-insensitive.
    """
    if not headers:
        return new_correlation_id()
    for key, value in headers.items():
        if key.lower() == CORRELATION_HEADER:
            text = str(value).strip()
            if text:
                return text
    return new_correlation_id()


def inject_correlation_id(headers: dict | None, correlation_id: str) -> dict:
    """Return a new headers dict with the correlation id set."""
    if not correlation_id or not correlation_id.strip():
        raise ValueError("correlation_id must be non-empty")
    result = dict(headers or {})
    result[CORRELATION_HEADER] = correlation_id
    return result

"""PII masking applied to captured bodies before they are persisted to S3.

Reviewer requirement: shadow captures must mask PII so the diff store never
becomes a copy of customer personal data. Masking covers both well-known
patterns (email, phone, SSN, card, bearer token) and caller-named fields.
"""
from __future__ import annotations

import re
from typing import Any, Iterable

MASK = "***MASKED***"

_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CARD = re.compile(r"\b(?:\d[ -]?){13,16}\b")
_PHONE = re.compile(r"\b\+?\d{1,3}[\s.\-]?\(?\d{2,4}\)?[\s.\-]?\d{3,4}[\s.\-]?\d{3,4}\b")
_BEARER = re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]+")

# Order matters: most specific first so a card number is not partially eaten by
# the phone pattern.
_PATTERNS = (_EMAIL, _SSN, _CARD, _BEARER, _PHONE)


def mask_text(text: str) -> str:
    """Mask all known PII patterns in a string."""
    for pattern in _PATTERNS:
        text = pattern.sub(MASK, text)
    return text


def mask_body(body: Any, pii_fields: Iterable[str] = ()) -> Any:
    """Recursively mask PII in an arbitrary JSON-like structure.

    - Strings are pattern-masked.
    - Any dict key whose name is in ``pii_fields`` is fully masked regardless of
      its value type.
    """
    named = {f.lower() for f in pii_fields}
    return _mask(body, named)


def _mask(node: Any, named: set[str]) -> Any:
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if str(key).lower() in named:
                out[key] = MASK
            else:
                out[key] = _mask(value, named)
        return out
    if isinstance(node, list):
        return [_mask(item, named) for item in node]
    if isinstance(node, str):
        return mask_text(node)
    return node

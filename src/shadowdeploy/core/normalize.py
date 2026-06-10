"""Normalization of non-deterministic fields before diffing.

Without this step, every comparison flags timestamps, generated UUIDs, and
request ids as divergences (the reviewer's "everything flagged as a diff"
troubleshooting note). Normalization replaces these with stable placeholders
so the diff focuses on meaningful changes.
"""
from __future__ import annotations

import re
from typing import Any, Iterable

PLACEHOLDER = "<normalized>"

_ISO_TS = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+\-]\d{2}:?\d{2})?")
_UUID = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
_EPOCH = re.compile(r"\b1[6-9]\d{8}\b")  # 10-digit epoch seconds, 2022+ range

_VALUE_PATTERNS = (_ISO_TS, _UUID, _EPOCH)


def normalize_text(text: str) -> str:
    for pattern in _VALUE_PATTERNS:
        text = pattern.sub(PLACEHOLDER, text)
    return text


def normalize(node: Any, ignore_fields: Iterable[str] = ()) -> Any:
    """Return a normalized copy of ``node``.

    - String values have timestamps/uuids/epochs replaced.
    - Any dict key in ``ignore_fields`` is dropped entirely (so it can never
      contribute a diff).
    """
    ignored = {f.lower() for f in ignore_fields}
    return _normalize(node, ignored)


def _normalize(node: Any, ignored: set[str]) -> Any:
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            if str(key).lower() in ignored:
                continue
            out[key] = _normalize(value, ignored)
        return out
    if isinstance(node, list):
        return [_normalize(item, ignored) for item in node]
    if isinstance(node, str):
        return normalize_text(node)
    return node

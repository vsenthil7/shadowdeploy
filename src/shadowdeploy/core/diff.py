"""Structural diff engine producing categorized field-level divergences.

Compares a normalized prod body against a normalized shadow body and yields a
list of :class:`FieldDiff`. The categories (added/removed/changed/type_mismatch)
feed the comparison report's "categorized differences" requirement.
"""
from __future__ import annotations

from typing import Any

from .models import DiffCategory, DiffResult, FieldDiff


def diff_bodies(prod: Any, shadow: Any) -> tuple[FieldDiff, ...]:
    """Return the tuple of field-level diffs between two JSON-like structures."""
    acc: list[FieldDiff] = []
    _diff(prod, shadow, "$", acc)
    return tuple(acc)


def _diff(prod: Any, shadow: Any, path: str, acc: list[FieldDiff]) -> None:
    if type(prod) is not type(shadow) and not _both_numbers(prod, shadow):
        acc.append(FieldDiff(path, DiffCategory.TYPE_MISMATCH, prod, shadow))
        return
    if isinstance(prod, dict):
        _diff_dict(prod, shadow, path, acc)
    elif isinstance(prod, list):
        _diff_list(prod, shadow, path, acc)
    else:
        if prod != shadow:
            acc.append(FieldDiff(path, DiffCategory.CHANGED, prod, shadow))


def _diff_dict(prod: dict, shadow: dict, path: str, acc: list[FieldDiff]) -> None:
    for key in prod:
        child = f"{path}.{key}"
        if key not in shadow:
            acc.append(FieldDiff(child, DiffCategory.REMOVED, prod[key], None))
        else:
            _diff(prod[key], shadow[key], child, acc)
    for key in shadow:
        if key not in prod:
            child = f"{path}.{key}"
            acc.append(FieldDiff(child, DiffCategory.ADDED, None, shadow[key]))


def _diff_list(prod: list, shadow: list, path: str, acc: list[FieldDiff]) -> None:
    common = min(len(prod), len(shadow))
    for i in range(common):
        _diff(prod[i], shadow[i], f"{path}[{i}]", acc)
    for i in range(common, len(prod)):
        acc.append(FieldDiff(f"{path}[{i}]", DiffCategory.REMOVED, prod[i], None))
    for i in range(common, len(shadow)):
        acc.append(FieldDiff(f"{path}[{i}]", DiffCategory.ADDED, None, shadow[i]))


def _both_numbers(a: Any, b: Any) -> bool:
    number = (int, float)
    # bool is a subclass of int; treat bools as non-numbers for diffing purposes
    if isinstance(a, bool) or isinstance(b, bool):
        return False
    return isinstance(a, number) and isinstance(b, number)


def compare_exchanges(prod, shadow) -> DiffResult:
    """Build a :class:`DiffResult` from two normalized captured exchanges.

    The two exchanges must share a correlation id.
    """
    if prod.correlation_id != shadow.correlation_id:
        raise ValueError("cannot compare exchanges with different correlation ids")
    diffs = diff_bodies(prod.body, shadow.body)
    return DiffResult(
        correlation_id=prod.correlation_id,
        matched=len(diffs) == 0 and prod.status_code == shadow.status_code,
        diffs=diffs,
        prod_latency_ms=prod.latency_ms,
        shadow_latency_ms=shadow.latency_ms,
        prod_status=prod.status_code,
        shadow_status=shadow.status_code,
    )

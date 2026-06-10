"""Typed domain models for the ShadowDeploy harness.

These models are intentionally dependency-free (stdlib only) so they run in a
Lambda runtime without packaging extra wheels.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Optional


class ServiceType(enum.Enum):
    """Type of service being shadowed."""

    REST_API = "rest_api"
    ML_INFERENCE = "ml_inference"
    ASYNC_WORKER = "async_worker"

    @classmethod
    def from_str(cls, value: str) -> "ServiceType":
        try:
            return cls(value.strip().lower())
        except ValueError as exc:  # pragma: no cover - re-raised with context below
            valid = ", ".join(s.value for s in cls)
            raise ValueError(
                f"unknown service type {value!r}; expected one of: {valid}"
            ) from exc


class IaCTool(enum.Enum):
    TERRAFORM = "terraform"
    CDK = "cdk"
    CLOUDFORMATION = "cloudformation"

    @classmethod
    def from_str(cls, value: str) -> "IaCTool":
        try:
            return cls(value.strip().lower())
        except ValueError as exc:
            valid = ", ".join(s.value for s in cls)
            raise ValueError(
                f"unknown IaC tool {value!r}; expected one of: {valid}"
            ) from exc


class DiffCategory(enum.Enum):
    """Category assigned to a single field-level divergence."""

    ADDED = "added"
    REMOVED = "removed"
    CHANGED = "changed"
    TYPE_MISMATCH = "type_mismatch"


class Verdict(enum.Enum):
    """Promotion recommendation produced by the report."""

    PROMOTE = "promote"
    REVIEW = "review"
    BLOCK = "block"


@dataclass(frozen=True)
class MirrorConfig:
    """Validated configuration for a shadow-testing run.

    Validation lives in ``core.config``; this model only stores values.
    """

    service_type: ServiceType
    prod_entry_point: str
    shadow_target: str
    region: str
    iac_tool: IaCTool
    sampling_rate: float
    log_retention_days: int = 7
    shadow_enabled: bool = True
    pii_fields: tuple[str, ...] = field(default_factory=tuple)
    ignore_fields: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CapturedExchange:
    """A single prod-or-shadow request/response capture."""

    correlation_id: str
    source: str  # "prod" or "shadow"
    status_code: int
    latency_ms: float
    body: Any
    captured_at: float


@dataclass(frozen=True)
class FieldDiff:
    path: str
    category: DiffCategory
    prod_value: Optional[Any] = None
    shadow_value: Optional[Any] = None


@dataclass(frozen=True)
class DiffResult:
    correlation_id: str
    matched: bool
    diffs: tuple[FieldDiff, ...]
    prod_latency_ms: float
    shadow_latency_ms: float
    prod_status: int
    shadow_status: int

    @property
    def latency_delta_ms(self) -> float:
        return self.shadow_latency_ms - self.prod_latency_ms

    @property
    def is_error_divergence(self) -> bool:
        """True when exactly one side returned an error status (>=400)."""
        prod_err = self.prod_status >= 400
        shadow_err = self.shadow_status >= 400
        return prod_err != shadow_err

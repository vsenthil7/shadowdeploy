"""Configuration loading and validation for ShadowDeploy.

All bounds enforcement (sampling caps, retention limits) lives here so the
models stay pure data.
"""
from __future__ import annotations

from typing import Any, Mapping

from .models import IaCTool, MirrorConfig, ServiceType

# Hard guardrails — shadow mirroring doubles compute for sampled requests, so
# the sampling rate is capped to keep cost bounded (reviewer requirement).
MAX_SAMPLING_RATE = 0.25
MIN_SAMPLING_RATE = 0.0
MAX_RETENTION_DAYS = 30
MIN_RETENTION_DAYS = 1

_REQUIRED_KEYS = (
    "service_type",
    "prod_entry_point",
    "shadow_target",
    "region",
    "iac_tool",
    "sampling_rate",
)


def load_config(raw: Mapping[str, Any]) -> MirrorConfig:
    """Build a validated :class:`MirrorConfig` from a raw mapping.

    Raises ``ValueError`` on any missing key or out-of-bounds value.
    """
    missing = [k for k in _REQUIRED_KEYS if k not in raw]
    if missing:
        raise ValueError(f"missing required config keys: {', '.join(missing)}")

    sampling_rate = _validate_sampling_rate(raw["sampling_rate"])
    retention = _validate_retention(raw.get("log_retention_days", 7))

    prod = _require_nonempty("prod_entry_point", raw["prod_entry_point"])
    shadow = _require_nonempty("shadow_target", raw["shadow_target"])
    region = _require_nonempty("region", raw["region"])

    return MirrorConfig(
        service_type=ServiceType.from_str(str(raw["service_type"])),
        prod_entry_point=prod,
        shadow_target=shadow,
        region=region,
        iac_tool=IaCTool.from_str(str(raw["iac_tool"])),
        sampling_rate=sampling_rate,
        log_retention_days=retention,
        shadow_enabled=bool(raw.get("shadow_enabled", True)),
        pii_fields=tuple(raw.get("pii_fields", ())),
        ignore_fields=tuple(raw.get("ignore_fields", ())),
    )


def _validate_sampling_rate(value: Any) -> float:
    try:
        rate = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"sampling_rate must be numeric, got {value!r}") from exc
    if rate != rate:  # NaN check
        raise ValueError("sampling_rate must not be NaN")
    if rate < MIN_SAMPLING_RATE or rate > MAX_SAMPLING_RATE:
        raise ValueError(
            f"sampling_rate {rate} out of bounds "
            f"[{MIN_SAMPLING_RATE}, {MAX_SAMPLING_RATE}]"
        )
    return rate


def _validate_retention(value: Any) -> int:
    try:
        days = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"log_retention_days must be an int, got {value!r}") from exc
    if days < MIN_RETENTION_DAYS or days > MAX_RETENTION_DAYS:
        raise ValueError(
            f"log_retention_days {days} out of bounds "
            f"[{MIN_RETENTION_DAYS}, {MAX_RETENTION_DAYS}]"
        )
    return days


def _require_nonempty(name: str, value: Any) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{name} must be a non-empty string")
    return text

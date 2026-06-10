import math

import pytest

from shadowdeploy.core.config import (
    MAX_RETENTION_DAYS,
    MAX_SAMPLING_RATE,
    load_config,
)
from shadowdeploy.core.models import (
    DiffCategory,
    DiffResult,
    FieldDiff,
    IaCTool,
    MirrorConfig,
    ServiceType,
    Verdict,
)
from shadowdeploy.core.sampling import should_sample


def base_raw(**over):
    raw = {
        "service_type": "rest_api",
        "prod_entry_point": "api-gw-prod",
        "shadow_target": "lambda-shadow",
        "region": "us-east-1",
        "iac_tool": "terraform",
        "sampling_rate": 0.05,
    }
    raw.update(over)
    return raw


# ---------------- models ----------------

@pytest.mark.unit
@pytest.mark.parametrize("value,expected", [
    ("rest_api", ServiceType.REST_API),
    ("ML_INFERENCE", ServiceType.ML_INFERENCE),
    (" async_worker ", ServiceType.ASYNC_WORKER),
])
def test_service_type_from_str(value, expected):
    assert ServiceType.from_str(value) is expected


@pytest.mark.negative
def test_service_type_invalid():
    with pytest.raises(ValueError, match="unknown service type"):
        ServiceType.from_str("nope")


@pytest.mark.unit
@pytest.mark.parametrize("value,expected", [
    ("terraform", IaCTool.TERRAFORM),
    ("CDK", IaCTool.CDK),
    ("cloudformation", IaCTool.CLOUDFORMATION),
])
def test_iac_tool_from_str(value, expected):
    assert IaCTool.from_str(value) is expected


@pytest.mark.negative
def test_iac_tool_invalid():
    with pytest.raises(ValueError, match="unknown IaC tool"):
        IaCTool.from_str("ansible")


@pytest.mark.unit
def test_diff_result_latency_delta_and_error_divergence():
    dr = DiffResult(
        correlation_id="c1",
        matched=False,
        diffs=(FieldDiff(path="$.a", category=DiffCategory.CHANGED, prod_value=1, shadow_value=2),),
        prod_latency_ms=10.0,
        shadow_latency_ms=25.0,
        prod_status=200,
        shadow_status=500,
    )
    assert dr.latency_delta_ms == 15.0
    assert dr.is_error_divergence is True


@pytest.mark.unit
def test_diff_result_no_error_divergence_when_both_ok():
    dr = DiffResult("c", True, (), 5.0, 5.0, 200, 200)
    assert dr.is_error_divergence is False
    assert dr.latency_delta_ms == 0.0


@pytest.mark.unit
def test_diff_result_no_error_divergence_when_both_error():
    dr = DiffResult("c", True, (), 5.0, 5.0, 500, 503)
    assert dr.is_error_divergence is False


@pytest.mark.unit
def test_verdict_enum_values():
    assert {v.value for v in Verdict} == {"promote", "review", "block"}


# ---------------- config ----------------

@pytest.mark.unit
def test_load_config_happy_path():
    cfg = load_config(base_raw(pii_fields=["email"], ignore_fields=["ts"]))
    assert isinstance(cfg, MirrorConfig)
    assert cfg.service_type is ServiceType.REST_API
    assert cfg.iac_tool is IaCTool.TERRAFORM
    assert cfg.sampling_rate == 0.05
    assert cfg.pii_fields == ("email",)
    assert cfg.ignore_fields == ("ts",)
    assert cfg.shadow_enabled is True
    assert cfg.log_retention_days == 7


@pytest.mark.unit
def test_load_config_custom_retention_and_disabled():
    cfg = load_config(base_raw(log_retention_days=14, shadow_enabled=False))
    assert cfg.log_retention_days == 14
    assert cfg.shadow_enabled is False


@pytest.mark.negative
def test_load_config_missing_keys():
    with pytest.raises(ValueError, match="missing required config keys"):
        load_config({"service_type": "rest_api"})


@pytest.mark.negative
@pytest.mark.parametrize("rate", [-0.1, MAX_SAMPLING_RATE + 0.01, 0.99])
def test_load_config_sampling_out_of_bounds(rate):
    with pytest.raises(ValueError, match="out of bounds"):
        load_config(base_raw(sampling_rate=rate))


@pytest.mark.negative
def test_load_config_sampling_non_numeric():
    with pytest.raises(ValueError, match="must be numeric"):
        load_config(base_raw(sampling_rate="abc"))


@pytest.mark.negative
def test_load_config_sampling_nan():
    with pytest.raises(ValueError, match="must not be NaN"):
        load_config(base_raw(sampling_rate=math.nan))


@pytest.mark.unit
def test_load_config_sampling_zero_ok():
    assert load_config(base_raw(sampling_rate=0)).sampling_rate == 0.0


@pytest.mark.negative
@pytest.mark.parametrize("days", [0, MAX_RETENTION_DAYS + 1])
def test_load_config_retention_out_of_bounds(days):
    with pytest.raises(ValueError, match="out of bounds"):
        load_config(base_raw(log_retention_days=days))


@pytest.mark.negative
def test_load_config_retention_non_int():
    with pytest.raises(ValueError, match="must be an int"):
        load_config(base_raw(log_retention_days="seven"))


@pytest.mark.negative
@pytest.mark.parametrize("field_name", ["prod_entry_point", "shadow_target", "region"])
def test_load_config_empty_strings(field_name):
    with pytest.raises(ValueError, match="non-empty string"):
        load_config(base_raw(**{field_name: "   "}))


# ---------------- sampling ----------------

@pytest.mark.unit
def test_should_sample_kill_switch():
    assert should_sample("anything", 1.0, enabled=False) is False


@pytest.mark.unit
def test_should_sample_zero_rate():
    assert should_sample("anything", 0.0) is False


@pytest.mark.unit
def test_should_sample_full_rate():
    assert should_sample("anything", 1.0) is True


@pytest.mark.unit
def test_should_sample_deterministic():
    r1 = should_sample("corr-123", 0.5)
    r2 = should_sample("corr-123", 0.5)
    assert r1 == r2


@pytest.mark.unit
def test_should_sample_distribution_roughly_matches_rate():
    hits = sum(should_sample(f"id-{i}", 0.1) for i in range(2000))
    # ~10% with tolerance
    assert 120 < hits < 280


@pytest.mark.negative
def test_should_sample_requires_correlation_id_for_partial_rate():
    with pytest.raises(ValueError, match="correlation_id required"):
        should_sample("", 0.5)

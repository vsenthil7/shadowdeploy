import pytest

from shadowdeploy.core.models import IaCTool, MirrorConfig, ServiceType
from shadowdeploy.orchestrator import run_pipeline


def cfg(**over):
    params = dict(
        service_type=ServiceType.REST_API,
        prod_entry_point="api",
        shadow_target="shadow",
        region="us-east-1",
        iac_tool=IaCTool.TERRAFORM,
        sampling_rate=1.0,
        ignore_fields=(),
    )
    params.update(over)
    return MirrorConfig(**params)


def prod(event):
    return {"status_code": 200, "latency_ms": 10.0, "body": {"v": event["n"]}}


def shadow_same(event):
    return {"status_code": 200, "latency_ms": 11.0, "body": {"v": event["n"]}}


def shadow_diff(event):
    return {"status_code": 200, "latency_ms": 11.0, "body": {"v": event["n"] + 100}}


def events(n=5):
    return [{"headers": {"x-shadowdeploy-correlation-id": f"c{i}"}, "n": i} for i in range(n)]


@pytest.mark.functional
def test_pipeline_all_match_promotes():
    report = run_pipeline(events(100), cfg(), prod, shadow_same)
    assert report.verdict.value == "promote"
    assert report.metrics.total == 100


@pytest.mark.functional
def test_pipeline_all_diff_blocks():
    report = run_pipeline(events(100), cfg(), prod, shadow_diff)
    assert report.verdict.value == "block"


@pytest.mark.functional
def test_pipeline_shadow_error_records_dropped_from_batch():
    def boom(event):
        raise RuntimeError("nope")
    # prod still succeeds for all; shadow errors -> no shadow captures -> no pairs
    with pytest.raises(ValueError, match="no comparable"):
        run_pipeline(events(5), cfg(), prod, boom)


@pytest.mark.negative
def test_pipeline_no_sampling_raises():
    with pytest.raises(ValueError, match="no comparable"):
        run_pipeline(events(5), cfg(shadow_enabled=False), prod, shadow_same)

import pytest

from shadowdeploy.core.models import (
    CapturedExchange,
    IaCTool,
    MirrorConfig,
    ServiceType,
)
from shadowdeploy.handlers.compare_handler import compare_batch, pair_captures
from shadowdeploy.handlers.mirror import handle_request


def cfg(**over):
    """Build a MirrorConfig directly.

    Handlers must work at any sampling rate; the production cap is enforced at
    config-load time (tested in the config suite), not here.
    """
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
    if isinstance(params.get("ignore_fields"), list):
        params["ignore_fields"] = tuple(params["ignore_fields"])
    return MirrorConfig(**params)


def prod_ok(event):
    return {"status_code": 200, "latency_ms": 10.0, "body": {"result": "prod"}}


def shadow_ok(event):
    return {"status_code": 200, "latency_ms": 14.0, "body": {"result": "shadow"}}


def shadow_boom(event):
    raise RuntimeError("shadow exploded")


@pytest.mark.functional
def test_client_always_gets_prod_response_even_when_shadow_differs():
    records = []
    outcome = handle_request(
        {"headers": {"x-shadowdeploy-correlation-id": "c1"}},
        cfg(sampling_rate=1.0),
        prod_ok,
        shadow_ok,
        sink=records.append,
    )
    # Client gets PROD, never shadow — the core guarantee.
    assert outcome.client_response["body"] == {"result": "prod"}
    assert outcome.shadow_captured is True
    assert outcome.shadow_capture.body == {"result": "shadow"}
    # both captures emitted
    assert len(records) == 2


@pytest.mark.functional
def test_shadow_error_is_isolated_from_client():
    records = []
    outcome = handle_request(
        {"headers": {"x-shadowdeploy-correlation-id": "c1"}},
        cfg(sampling_rate=1.0),
        prod_ok,
        shadow_boom,
        sink=records.append,
    )
    assert outcome.client_response["status_code"] == 200
    assert outcome.shadow_captured is False
    # prod capture + shadow_error record
    assert any("shadow_error" in r for r in records if isinstance(r, dict))


@pytest.mark.unit
def test_no_shadow_when_disabled():
    outcome = handle_request(
        {"headers": {}}, cfg(sampling_rate=1.0, shadow_enabled=False),
        prod_ok, shadow_ok,
    )
    assert outcome.shadow_captured is False


@pytest.mark.unit
def test_no_shadow_when_sampling_zero():
    outcome = handle_request(
        {"headers": {}}, cfg(sampling_rate=0.0), prod_ok, shadow_ok,
    )
    assert outcome.shadow_captured is False


@pytest.mark.unit
def test_handle_request_no_sink():
    outcome = handle_request({"headers": {}}, cfg(sampling_rate=1.0), prod_ok, shadow_ok)
    assert outcome.shadow_captured is True


@pytest.mark.unit
def test_handle_request_missing_headers_key():
    outcome = handle_request({}, cfg(sampling_rate=1.0), prod_ok, shadow_ok)
    assert outcome.client_response["status_code"] == 200


# ---------------- pairing & batch ----------------

def _cap(cid, source, body, status=200):
    return CapturedExchange(cid, source, status, 10.0, body, 1000.0)


@pytest.mark.unit
def test_pair_captures_matches_by_correlation():
    caps = [
        _cap("a", "prod", {"x": 1}),
        _cap("a", "shadow", {"x": 1}),
        _cap("b", "prod", {"x": 2}),  # unpaired -> dropped
    ]
    pairs = pair_captures(caps)
    assert len(pairs) == 1
    assert pairs[0][0].source == "prod"
    assert pairs[0][1].source == "shadow"


@pytest.mark.unit
def test_pair_captures_shadow_without_prod_dropped():
    pairs = pair_captures([_cap("a", "shadow", {})])
    assert pairs == []


@pytest.mark.functional
def test_compare_batch_normalizes_before_diff():
    caps = [
        _cap("a", "prod", {"ts": "2026-06-08T09:02:11Z", "v": 1}),
        _cap("a", "shadow", {"ts": "2026-06-08T10:00:00Z", "v": 1}),
    ]
    results = compare_batch(caps, cfg())
    # timestamps normalized => match despite different ts strings
    assert len(results) == 1
    assert results[0].matched is True


@pytest.mark.functional
def test_compare_batch_detects_real_diff():
    caps = [
        _cap("a", "prod", {"v": 1}),
        _cap("a", "shadow", {"v": 2}),
    ]
    results = compare_batch(caps, cfg())
    assert results[0].matched is False


@pytest.mark.unit
def test_compare_batch_ignore_fields():
    caps = [
        _cap("a", "prod", {"debug": "x", "v": 1}),
        _cap("a", "shadow", {"debug": "y", "v": 1}),
    ]
    results = compare_batch(caps, cfg(ignore_fields=["debug"]))
    assert results[0].matched is True

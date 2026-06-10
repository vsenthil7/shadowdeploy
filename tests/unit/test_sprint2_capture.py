import pytest

from shadowdeploy.core.capture import capture_exchange
from shadowdeploy.core.correlation import (
    CORRELATION_HEADER,
    extract_correlation_id,
    inject_correlation_id,
    new_correlation_id,
)
from shadowdeploy.core.pii import MASK, mask_body, mask_text


# ---------------- correlation ----------------

@pytest.mark.unit
def test_new_correlation_id_unique_and_prefixed():
    a, b = new_correlation_id(), new_correlation_id()
    assert a != b
    assert a.startswith("sd-")


@pytest.mark.unit
def test_extract_generates_when_no_headers():
    assert extract_correlation_id(None).startswith("sd-")


@pytest.mark.unit
def test_extract_generates_when_empty_dict():
    assert extract_correlation_id({}).startswith("sd-")


@pytest.mark.unit
def test_extract_case_insensitive():
    cid = extract_correlation_id({CORRELATION_HEADER.upper(): "abc"})
    assert cid == "abc"


@pytest.mark.unit
def test_extract_generates_when_blank_value():
    cid = extract_correlation_id({CORRELATION_HEADER: "   "})
    assert cid.startswith("sd-")


@pytest.mark.unit
def test_extract_ignores_unrelated_header():
    cid = extract_correlation_id({"other": "x"})
    assert cid.startswith("sd-")


@pytest.mark.unit
def test_inject_sets_header():
    headers = inject_correlation_id({"a": "1"}, "cid-1")
    assert headers[CORRELATION_HEADER] == "cid-1"
    assert headers["a"] == "1"


@pytest.mark.unit
def test_inject_none_headers():
    headers = inject_correlation_id(None, "cid-2")
    assert headers == {CORRELATION_HEADER: "cid-2"}


@pytest.mark.negative
def test_inject_requires_correlation_id():
    with pytest.raises(ValueError, match="non-empty"):
        inject_correlation_id({}, "  ")


# ---------------- pii ----------------

@pytest.mark.unit
def test_mask_email():
    assert mask_text("contact me at jane.doe@example.com now") == f"contact me at {MASK} now"


@pytest.mark.unit
def test_mask_ssn():
    assert MASK in mask_text("ssn 123-45-6789")


@pytest.mark.unit
def test_mask_card():
    assert MASK in mask_text("card 4111 1111 1111 1111")


@pytest.mark.unit
def test_mask_bearer():
    assert MASK in mask_text("Authorization: Bearer abc.def-123")


@pytest.mark.unit
def test_mask_phone():
    assert MASK in mask_text("call +1 415 555 1234")


@pytest.mark.unit
def test_mask_text_no_pii_unchanged():
    assert mask_text("hello world") == "hello world"


@pytest.mark.unit
def test_mask_body_nested_and_named_fields():
    body = {
        "user": {"email": "x@y.com", "name": "Jane"},
        "password": "supersecret",
        "items": ["plain", "ssn 123-45-6789"],
        "count": 3,
        "flag": True,
    }
    out = mask_body(body, pii_fields=["password"])
    assert out["user"]["email"] == MASK
    assert out["user"]["name"] == "Jane"
    assert out["password"] == MASK
    assert out["items"][0] == "plain"
    assert MASK in out["items"][1]
    assert out["count"] == 3
    assert out["flag"] is True


@pytest.mark.unit
def test_mask_body_passthrough_scalar():
    assert mask_body(42) == 42
    assert mask_body(None) is None


# ---------------- capture ----------------

@pytest.mark.unit
def test_capture_exchange_masks_and_builds():
    ex = capture_exchange(
        correlation_id="c1",
        source="prod",
        status_code=200,
        latency_ms=12.5,
        body={"email": "a@b.com"},
        pii_fields=(),
        clock=lambda: 1000.0,
    )
    assert ex.correlation_id == "c1"
    assert ex.source == "prod"
    assert ex.body["email"] == MASK
    assert ex.captured_at == 1000.0
    assert ex.latency_ms == 12.5


@pytest.mark.unit
def test_capture_exchange_default_clock():
    ex = capture_exchange(
        correlation_id="c1", source="shadow", status_code=201,
        latency_ms=0.0, body="ok",
    )
    assert ex.captured_at > 0


@pytest.mark.negative
def test_capture_invalid_source():
    with pytest.raises(ValueError, match="source must be one of"):
        capture_exchange(correlation_id="c", source="staging",
                         status_code=200, latency_ms=1.0, body={})


@pytest.mark.negative
def test_capture_blank_correlation():
    with pytest.raises(ValueError, match="correlation_id must be non-empty"):
        capture_exchange(correlation_id="  ", source="prod",
                         status_code=200, latency_ms=1.0, body={})


@pytest.mark.negative
def test_capture_negative_latency():
    with pytest.raises(ValueError, match="latency_ms must be non-negative"):
        capture_exchange(correlation_id="c", source="prod",
                         status_code=200, latency_ms=-1.0, body={})


@pytest.mark.negative
@pytest.mark.parametrize("status", [99, 600, "200"])
def test_capture_bad_status(status):
    with pytest.raises(ValueError, match="status_code out of HTTP range"):
        capture_exchange(correlation_id="c", source="prod",
                         status_code=status, latency_ms=1.0, body={})

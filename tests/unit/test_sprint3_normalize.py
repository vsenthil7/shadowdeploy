import pytest

from shadowdeploy.core.normalize import PLACEHOLDER, normalize, normalize_text


@pytest.mark.unit
def test_normalize_iso_timestamp():
    assert normalize_text("at 2026-06-08T09:02:11.123Z done") == f"at {PLACEHOLDER} done"


@pytest.mark.unit
def test_normalize_iso_with_offset():
    assert PLACEHOLDER in normalize_text("2026-06-08 09:02:11+01:00")


@pytest.mark.unit
def test_normalize_uuid():
    assert normalize_text("id 550e8400-e29b-41d4-a716-446655440000") == f"id {PLACEHOLDER}"


@pytest.mark.unit
def test_normalize_epoch():
    assert PLACEHOLDER in normalize_text("ts 1749373331 end")


@pytest.mark.unit
def test_normalize_text_no_match():
    assert normalize_text("stable value") == "stable value"


@pytest.mark.unit
def test_normalize_nested_and_ignore_fields():
    body = {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "ts": "2026-06-08T09:02:11Z",
        "payload": {"value": 42, "stamp": "1749373331"},
        "tags": ["a", "2026-06-08T00:00:00Z"],
        "drop_me": "anything",
    }
    out = normalize(body, ignore_fields=["drop_me"])
    assert out["request_id"] == PLACEHOLDER
    assert out["ts"] == PLACEHOLDER
    assert out["payload"]["value"] == 42
    assert out["payload"]["stamp"] == PLACEHOLDER
    assert out["tags"][1] == PLACEHOLDER
    assert "drop_me" not in out


@pytest.mark.unit
def test_normalize_scalar_passthrough():
    assert normalize(7) == 7
    assert normalize(None) is None
    assert normalize(True) is True


@pytest.mark.unit
def test_normalize_no_ignore_fields():
    assert normalize({"a": 1}) == {"a": 1}

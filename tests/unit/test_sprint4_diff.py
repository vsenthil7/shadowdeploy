import pytest

from shadowdeploy.core.diff import compare_exchanges, diff_bodies
from shadowdeploy.core.models import CapturedExchange, DiffCategory


def cats(diffs):
    return {d.path: d.category for d in diffs}


@pytest.mark.unit
def test_diff_identical():
    assert diff_bodies({"a": 1}, {"a": 1}) == ()


@pytest.mark.unit
def test_diff_changed_scalar():
    diffs = diff_bodies({"a": 1}, {"a": 2})
    assert cats(diffs) == {"$.a": DiffCategory.CHANGED}


@pytest.mark.unit
def test_diff_added_and_removed_keys():
    diffs = diff_bodies({"a": 1, "b": 2}, {"a": 1, "c": 3})
    c = cats(diffs)
    assert c["$.b"] == DiffCategory.REMOVED
    assert c["$.c"] == DiffCategory.ADDED


@pytest.mark.unit
def test_diff_type_mismatch():
    diffs = diff_bodies({"a": 1}, {"a": "1"})
    assert cats(diffs) == {"$.a": DiffCategory.TYPE_MISMATCH}


@pytest.mark.unit
def test_diff_numbers_int_float_not_type_mismatch():
    # 1 == 1.0 so no diff at all
    assert diff_bodies({"a": 1}, {"a": 1.0}) == ()
    # different numeric values => changed, not type mismatch
    diffs = diff_bodies({"a": 1}, {"a": 2.5})
    assert cats(diffs) == {"$.a": DiffCategory.CHANGED}


@pytest.mark.unit
def test_diff_bool_vs_int_is_type_mismatch():
    diffs = diff_bodies({"a": True}, {"a": 1})
    assert cats(diffs) == {"$.a": DiffCategory.TYPE_MISMATCH}


@pytest.mark.unit
def test_diff_nested_dict():
    diffs = diff_bodies({"x": {"y": 1}}, {"x": {"y": 2}})
    assert cats(diffs) == {"$.x.y": DiffCategory.CHANGED}


@pytest.mark.unit
def test_diff_list_changed_element():
    diffs = diff_bodies({"l": [1, 2, 3]}, {"l": [1, 9, 3]})
    assert cats(diffs) == {"$.l[1]": DiffCategory.CHANGED}


@pytest.mark.unit
def test_diff_list_longer_prod():
    diffs = diff_bodies([1, 2, 3], [1])
    c = cats(diffs)
    assert c["$[1]"] == DiffCategory.REMOVED
    assert c["$[2]"] == DiffCategory.REMOVED


@pytest.mark.unit
def test_diff_list_longer_shadow():
    diffs = diff_bodies([1], [1, 2])
    assert cats(diffs) == {"$[1]": DiffCategory.ADDED}


@pytest.mark.unit
def test_diff_top_level_type_mismatch():
    diffs = diff_bodies({"a": 1}, [1, 2])
    assert cats(diffs) == {"$": DiffCategory.TYPE_MISMATCH}


def _ex(cid, source, status, body, latency=10.0):
    return CapturedExchange(cid, source, status, latency, body, 1000.0)


@pytest.mark.unit
def test_compare_exchanges_match():
    p = _ex("c", "prod", 200, {"a": 1})
    s = _ex("c", "shadow", 200, {"a": 1}, latency=12.0)
    res = compare_exchanges(p, s)
    assert res.matched is True
    assert res.diffs == ()
    assert res.latency_delta_ms == 2.0


@pytest.mark.unit
def test_compare_exchanges_status_diff_unmatched():
    p = _ex("c", "prod", 200, {"a": 1})
    s = _ex("c", "shadow", 500, {"a": 1})
    res = compare_exchanges(p, s)
    assert res.matched is False
    assert res.is_error_divergence is True


@pytest.mark.unit
def test_compare_exchanges_body_diff_unmatched():
    p = _ex("c", "prod", 200, {"a": 1})
    s = _ex("c", "shadow", 200, {"a": 2})
    res = compare_exchanges(p, s)
    assert res.matched is False
    assert len(res.diffs) == 1


@pytest.mark.negative
def test_compare_exchanges_mismatched_correlation():
    p = _ex("c1", "prod", 200, {})
    s = _ex("c2", "shadow", 200, {})
    with pytest.raises(ValueError, match="different correlation ids"):
        compare_exchanges(p, s)

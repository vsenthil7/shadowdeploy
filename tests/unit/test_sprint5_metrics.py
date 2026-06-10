import pytest

from shadowdeploy.core.diff import compare_exchanges
from shadowdeploy.core.metrics import aggregate
from shadowdeploy.core.models import CapturedExchange, DiffCategory, DiffResult, FieldDiff


def _ex(cid, source, status, body, latency):
    return CapturedExchange(cid, source, status, latency, body, 1000.0)


def _result(cid, matched, diffs, pl, sl, ps, ss):
    return DiffResult(cid, matched, diffs, pl, sl, ps, ss)


@pytest.mark.unit
def test_aggregate_all_match():
    results = [
        compare_exchanges(_ex("a", "prod", 200, {"x": 1}, 10), _ex("a", "shadow", 200, {"x": 1}, 11)),
        compare_exchanges(_ex("b", "prod", 200, {"x": 2}, 20), _ex("b", "shadow", 200, {"x": 2}, 19)),
    ]
    m = aggregate(results)
    assert m.total == 2
    assert m.matched == 2
    assert m.match_pct == 100.0
    assert m.mean_prod_latency_ms == 15.0
    assert m.mean_shadow_latency_ms == 15.0
    assert m.latency_delta_ms == 0.0
    assert m.category_counts == {}


@pytest.mark.unit
def test_aggregate_mixed_with_categories():
    diffs = (
        FieldDiff("$.a", DiffCategory.CHANGED, 1, 2),
        FieldDiff("$.b", DiffCategory.ADDED, None, 3),
    )
    results = [
        _result("a", False, diffs, 10.0, 30.0, 200, 500),
        _result("b", True, (), 10.0, 10.0, 200, 200),
    ]
    m = aggregate(results)
    assert m.matched == 1
    assert m.match_pct == 50.0
    assert m.latency_delta_ms == 10.0
    assert m.prod_error_rate == 0.0
    assert m.shadow_error_rate == 0.5
    assert m.error_rate_delta == 0.5
    assert m.category_counts == {"changed": 1, "added": 1}


@pytest.mark.unit
def test_aggregate_single():
    m = aggregate([_result("a", True, (), 5.0, 7.0, 200, 200)])
    assert m.total == 1
    assert m.match_pct == 100.0
    assert m.latency_delta_ms == 2.0


@pytest.mark.negative
def test_aggregate_empty_raises():
    with pytest.raises(ValueError, match="empty batch"):
        aggregate([])

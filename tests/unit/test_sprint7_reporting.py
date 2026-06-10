import json

import pytest

from shadowdeploy.core.models import DiffCategory, DiffResult, FieldDiff, Verdict
from shadowdeploy.reporting.render import to_dict, to_json, to_markdown
from shadowdeploy.reporting.report import build_report, decide_verdict
from shadowdeploy.core.metrics import aggregate


def result(matched, diffs=(), pl=10.0, sl=10.0, ps=200, ss=200):
    return DiffResult("c", matched, diffs, pl, sl, ps, ss)


def metrics_for(results):
    return aggregate(results)


@pytest.mark.unit
def test_verdict_promote_all_match():
    m = metrics_for([result(True) for _ in range(100)])
    verdict, reasons = decide_verdict(m)
    assert verdict is Verdict.PROMOTE
    assert reasons


@pytest.mark.unit
def test_verdict_review_band():
    results = [result(True) for _ in range(97)] + [result(False, (FieldDiff("$.a", DiffCategory.CHANGED, 1, 2),)) for _ in range(3)]
    m = metrics_for(results)
    verdict, _ = decide_verdict(m)
    assert verdict is Verdict.REVIEW


@pytest.mark.unit
def test_verdict_block_low_match():
    results = [result(True) for _ in range(80)] + [result(False, (FieldDiff("$.a", DiffCategory.CHANGED, 1, 2),)) for _ in range(20)]
    m = metrics_for(results)
    verdict, reasons = decide_verdict(m)
    assert verdict is Verdict.BLOCK
    assert any("<" in r for r in reasons)


@pytest.mark.unit
def test_verdict_block_on_error_rate_delta():
    # all "match" on body but shadow errors -> matched False + error divergence
    results = [result(False, (), ss=500) for _ in range(10)]
    m = metrics_for(results)
    verdict, reasons = decide_verdict(m)
    assert verdict is Verdict.BLOCK
    assert any("error-rate" in r for r in reasons)


@pytest.mark.unit
def test_verdict_latency_downgrades_promote_to_review():
    results = [result(True, pl=10.0, sl=100.0) for _ in range(100)]
    m = metrics_for(results)
    verdict, reasons = decide_verdict(m, max_latency_delta_ms=50.0)
    assert verdict is Verdict.REVIEW
    assert any("latency" in r for r in reasons)


@pytest.mark.unit
def test_verdict_latency_high_but_already_review_stays_review():
    # match in review band AND high latency
    results = [result(True, pl=10, sl=200) for _ in range(96)] + [
        result(False, (FieldDiff("$.a", DiffCategory.CHANGED, 1, 2),)) for _ in range(4)
    ]
    m = metrics_for(results)
    verdict, _ = decide_verdict(m)
    assert verdict is Verdict.REVIEW


@pytest.mark.unit
def test_build_report_wires_metrics_and_verdict():
    report = build_report([result(True) for _ in range(100)])
    assert report.verdict is Verdict.PROMOTE
    assert report.metrics.total == 100


# ---------------- rendering ----------------

@pytest.mark.unit
def test_to_dict_and_json_roundtrip():
    report = build_report([
        result(False, (FieldDiff("$.a", DiffCategory.CHANGED, 1, 2),)),
        result(True),
    ])
    d = to_dict(report)
    assert d["verdict"] in {"promote", "review", "block"}
    parsed = json.loads(to_json(report))
    assert parsed["metrics"]["total"] == 2


@pytest.mark.unit
def test_to_markdown_with_diffs():
    report = build_report([
        result(False, (FieldDiff("$.a", DiffCategory.CHANGED, 1, 2),)),
    ] + [result(True) for _ in range(99)])
    md = to_markdown(report)
    assert "Promotion Report" in md
    assert "Divergence categories" in md
    assert "changed" in md
    assert "never served to clients" in md


@pytest.mark.unit
def test_to_markdown_no_diffs():
    report = build_report([result(True) for _ in range(100)])
    md = to_markdown(report)
    assert "_No divergences._" in md
    assert "PROMOTE" in md

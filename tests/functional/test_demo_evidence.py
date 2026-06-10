import json
import os

import pytest

import scripts.generate_demo_evidence as demo


@pytest.mark.functional
def test_demo_generates_all_artifacts(tmp_path, monkeypatch):
    monkeypatch.setattr(demo, "OUT", str(tmp_path))
    demo.main()
    expected = [
        "sample_dataset.json", "diff_report.json", "diff_report.md",
        "execution_log.txt", "human_approval.json", "cost_report.json",
        "kpi_dashboard.txt", "evidence_manifest.json",
    ]
    for name in expected:
        assert os.path.exists(tmp_path / name), name


@pytest.mark.functional
def test_demo_masks_pii_in_dataset(tmp_path, monkeypatch):
    monkeypatch.setattr(demo, "OUT", str(tmp_path))
    demo.main()
    raw = (tmp_path / "sample_dataset.json").read_text()
    # no raw example emails — all masked
    assert "@example.com" not in raw
    assert "***MASKED***" in raw


@pytest.mark.functional
def test_demo_verdict_is_review_with_known_divergence(tmp_path, monkeypatch):
    monkeypatch.setattr(demo, "OUT", str(tmp_path))
    demo.main()
    report = json.loads((tmp_path / "diff_report.json").read_text())
    # v2 introduces a bounded divergence -> not a perfect match
    assert report["verdict"] in {"review", "block"}
    assert report["metrics"]["matched"] < report["metrics"]["total"]


@pytest.mark.functional
def test_demo_human_approval_not_auto_promoted(tmp_path, monkeypatch):
    monkeypatch.setattr(demo, "OUT", str(tmp_path))
    demo.main()
    approval = json.loads((tmp_path / "human_approval.json").read_text())
    assert approval["auto_promoted"] is False


@pytest.mark.functional
def test_demo_cost_within_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(demo, "OUT", str(tmp_path))
    demo.main()
    cost = json.loads((tmp_path / "cost_report.json").read_text())
    assert cost["within_budget"] is True


@pytest.mark.functional
def test_demo_manifest_flags_no_client_serving(tmp_path, monkeypatch):
    monkeypatch.setattr(demo, "OUT", str(tmp_path))
    demo.main()
    manifest = json.loads((tmp_path / "evidence_manifest.json").read_text())
    assert manifest["shadow_responses_served_to_clients"] is False


@pytest.mark.functional
def test_demo_main_default_out(monkeypatch, tmp_path):
    # exercise main() writing to the real OUT path via _write, then clean intent
    monkeypatch.setattr(demo, "OUT", str(tmp_path / "evidence"))
    demo.main()
    assert (tmp_path / "evidence" / "diff_report.md").exists()

import json

import pytest

from shadowdeploy.cli import main


@pytest.fixture
def config_file(tmp_path):
    cfg = {
        "service_type": "rest_api",
        "prod_entry_point": "api",
        "shadow_target": "shadow",
        "region": "us-east-1",
        "iac_tool": "terraform",
        "sampling_rate": 0.05,
    }
    p = tmp_path / "config.json"
    p.write_text(json.dumps(cfg))
    return str(p)


@pytest.fixture
def cdk_config_file(tmp_path):
    cfg = {
        "service_type": "ml_inference",
        "prod_entry_point": "api",
        "shadow_target": "shadow",
        "region": "us-east-1",
        "iac_tool": "cdk",
        "sampling_rate": 0.05,
    }
    p = tmp_path / "cdk.json"
    p.write_text(json.dumps(cfg))
    return str(p)


@pytest.fixture
def captures_file(tmp_path):
    caps = [
        {"correlation_id": "c1", "source": "prod", "status_code": 200,
         "latency_ms": 10.0, "body": {"v": 1}, "captured_at": 1000.0},
        {"correlation_id": "c1", "source": "shadow", "status_code": 200,
         "latency_ms": 11.0, "body": {"v": 1}, "captured_at": 1000.0},
    ]
    p = tmp_path / "caps.json"
    p.write_text(json.dumps(caps))
    return str(p)


@pytest.fixture
def diff_captures_file(tmp_path):
    caps = [
        {"correlation_id": "c1", "source": "prod", "status_code": 200,
         "latency_ms": 10.0, "body": {"v": 1}, "captured_at": 1000.0},
        {"correlation_id": "c1", "source": "shadow", "status_code": 500,
         "latency_ms": 11.0, "body": {"v": 2}, "captured_at": 1000.0},
    ]
    p = tmp_path / "diffcaps.json"
    p.write_text(json.dumps(caps))
    return str(p)


@pytest.fixture
def empty_captures_file(tmp_path):
    # only a prod capture -> no pairs
    caps = [{"correlation_id": "c1", "source": "prod", "status_code": 200,
             "latency_ms": 10.0, "body": {}, "captured_at": 1000.0}]
    p = tmp_path / "empty.json"
    p.write_text(json.dumps(caps))
    return str(p)


@pytest.mark.functional
def test_cli_emit_iac_terraform(config_file, capsys):
    rc = main(["emit-iac", "--config", config_file])
    assert rc == 0
    out = capsys.readouterr().out
    assert "terraform {" in out


@pytest.mark.functional
def test_cli_emit_iac_cdk(cdk_config_file, capsys):
    rc = main(["emit-iac", "--config", cdk_config_file, "--environment", "prod"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "ShadowDeployStack" in out


@pytest.mark.functional
def test_cli_estimate(config_file, capsys):
    rc = main(["estimate", "--config", config_file, "--monthly-requests", "1000000"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["sampled_requests"] == 50000


@pytest.mark.functional
def test_cli_report_json_promote(config_file, captures_file, capsys):
    rc = main(["report", "--config", config_file, "--captures", captures_file])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["verdict"] == "promote"


@pytest.mark.functional
def test_cli_report_markdown(config_file, captures_file, capsys):
    rc = main(["report", "--config", config_file, "--captures", captures_file,
               "--format", "markdown"])
    assert rc == 0
    assert "Promotion Report" in capsys.readouterr().out


@pytest.mark.functional
def test_cli_report_block_returns_1(config_file, diff_captures_file, capsys):
    rc = main(["report", "--config", config_file, "--captures", diff_captures_file])
    assert rc == 1


@pytest.mark.negative
def test_cli_report_no_pairs_returns_2(config_file, empty_captures_file, capsys):
    rc = main(["report", "--config", config_file, "--captures", empty_captures_file])
    assert rc == 2
    assert "no comparable pairs" in capsys.readouterr().err


@pytest.mark.negative
def test_cli_requires_subcommand():
    with pytest.raises(SystemExit):
        main([])

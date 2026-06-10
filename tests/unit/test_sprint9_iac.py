import json

import pytest

from shadowdeploy.core.models import IaCTool, MirrorConfig, ServiceType
from shadowdeploy.iac.cdk_emitter import emit_cdk
from shadowdeploy.iac.terraform_emitter import REQUIRED_TAGS, emit_terraform


def cfg(**over):
    params = dict(
        service_type=ServiceType.REST_API,
        prod_entry_point="api",
        shadow_target="shadow",
        region="eu-west-1",
        iac_tool=IaCTool.TERRAFORM,
        sampling_rate=0.05,
        log_retention_days=7,
        shadow_enabled=True,
    )
    params.update(over)
    return MirrorConfig(**params)


# ---------------- terraform ----------------

@pytest.mark.unit
def test_terraform_contains_region_and_sampling():
    tf = emit_terraform(cfg(region="eu-west-1", sampling_rate=0.07))
    assert 'region = "eu-west-1"' in tf
    assert "sampling_rate  = 0.07" in tf


@pytest.mark.unit
def test_terraform_has_all_required_tags():
    tf = emit_terraform(cfg(), environment="staging")
    for tag in REQUIRED_TAGS:
        assert tag in tf
    assert '"staging"' in tf


@pytest.mark.unit
def test_terraform_least_privilege_scoped_to_bucket():
    tf = emit_terraform(cfg())
    assert "s3:GetObject" in tf
    assert "s3:PutObject" in tf
    # scoped to the bucket arn, not "*"
    assert "${aws_s3_bucket.captures.arn}/*" in tf
    assert 'Resource = "*"' not in tf


@pytest.mark.unit
def test_terraform_billing_alarms_present():
    tf = emit_terraform(cfg())
    assert "threshold           = 10" in tf
    assert "threshold           = 50" in tf
    assert "threshold           = 100" in tf


@pytest.mark.unit
def test_terraform_public_access_blocked():
    tf = emit_terraform(cfg())
    assert "block_public_acls       = true" in tf
    assert "restrict_public_buckets = true" in tf


@pytest.mark.unit
def test_terraform_retention_in_lifecycle():
    tf = emit_terraform(cfg(log_retention_days=3))
    assert "days = 3" in tf


@pytest.mark.unit
def test_terraform_shadow_enabled_lowercased():
    assert "shadow_enabled = false" in emit_terraform(cfg(shadow_enabled=False))
    assert "shadow_enabled = true" in emit_terraform(cfg(shadow_enabled=True))


@pytest.mark.negative
def test_terraform_blank_environment():
    with pytest.raises(ValueError, match="environment must be non-empty"):
        emit_terraform(cfg(), environment="  ")


# ---------------- cdk ----------------

@pytest.mark.unit
def test_cdk_has_tags_and_least_priv():
    ts = emit_cdk(cfg(), environment="dev")
    assert "ShadowDeployStack" in ts
    assert "grantReadWrite" in ts  # least-priv to bucket
    assert "BLOCK_ALL" in ts


@pytest.mark.unit
def test_cdk_billing_alarms_loop():
    ts = emit_cdk(cfg())
    assert "[10, 50, 100]" in ts
    assert "AWS/Billing" in ts


@pytest.mark.unit
def test_cdk_retention_and_sampling_outputs():
    ts = emit_cdk(cfg(log_retention_days=14, sampling_rate=0.1))
    assert "Duration.days(14)" in ts
    assert "value: '0.1'" in ts


@pytest.mark.unit
def test_cdk_shadow_enabled_output():
    assert "value: 'false'" in emit_cdk(cfg(shadow_enabled=False))


@pytest.mark.negative
def test_cdk_blank_environment():
    with pytest.raises(ValueError, match="environment must be non-empty"):
        emit_cdk(cfg(), environment="")

import pytest

from shadowdeploy.core.cost import (
    BILLING_ALERT_THRESHOLDS,
    estimate_cost,
    kill_switch_active,
)
from shadowdeploy.core.models import IaCTool, MirrorConfig, ServiceType


def cfg(sampling_rate=0.05, shadow_enabled=True):
    return MirrorConfig(
        service_type=ServiceType.REST_API,
        prod_entry_point="api",
        shadow_target="shadow",
        region="us-east-1",
        iac_tool=IaCTool.TERRAFORM,
        sampling_rate=sampling_rate,
        shadow_enabled=shadow_enabled,
    )


@pytest.mark.unit
def test_estimate_basic_math():
    est = estimate_cost(cfg(sampling_rate=0.1), 1_000_000)
    assert est.sampled_requests == 100_000
    assert est.total_added_cost > 0
    assert est.budget_alerts == BILLING_ALERT_THRESHOLDS


@pytest.mark.unit
def test_estimate_disabled_zero_cost():
    est = estimate_cost(cfg(shadow_enabled=False), 1_000_000)
    assert est.sampled_requests == 0
    assert est.total_added_cost == 0.0
    assert est.within_budget is True


@pytest.mark.unit
def test_estimate_within_budget_true():
    est = estimate_cost(cfg(sampling_rate=0.05), 100_000, monthly_budget=100.0)
    assert est.within_budget is True


@pytest.mark.unit
def test_estimate_over_budget_false():
    est = estimate_cost(cfg(sampling_rate=0.25), 100_000_000, monthly_budget=1.0)
    assert est.within_budget is False


@pytest.mark.unit
def test_estimate_zero_requests():
    est = estimate_cost(cfg(), 0)
    assert est.sampled_requests == 0
    assert est.total_added_cost == 0.0


@pytest.mark.negative
def test_estimate_negative_requests():
    with pytest.raises(ValueError, match="monthly_requests must be non-negative"):
        estimate_cost(cfg(), -1)


@pytest.mark.negative
@pytest.mark.parametrize("budget", [0, -5.0])
def test_estimate_bad_budget(budget):
    with pytest.raises(ValueError, match="monthly_budget must be positive"):
        estimate_cost(cfg(), 100, monthly_budget=budget)


@pytest.mark.unit
def test_kill_switch():
    assert kill_switch_active(cfg(shadow_enabled=False)) is True
    assert kill_switch_active(cfg(shadow_enabled=True)) is False

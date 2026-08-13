"""Unit tests for investment recommendation logic."""

import pytest

from kenya_wealth_agent.domain.investment import get_investment_recommendations
from kenya_wealth_agent.domain.models import RiskTolerance


def test_negative_amount_rejected():
    with pytest.raises(ValueError, match="amount cannot be negative"):
        get_investment_recommendations(-1, RiskTolerance.CONSERVATIVE, "long")


def test_invalid_risk_tolerance():
    with pytest.raises(ValueError, match="Invalid risk tolerance"):
        get_investment_recommendations(10_000, "very risky", "long")


@pytest.mark.parametrize("input_value", ["conservative", "CONSERVATIVE", " Conservative "])
def test_case_insensitive_risk_string(input_value):
    result = get_investment_recommendations(10_000, input_value, "long")
    assert result.risk_profile == "conservative"


def test_enum_risk_tolerance_accepted():
    result = get_investment_recommendations(10_000, RiskTolerance.MODERATE, "long")
    assert result.risk_profile == "moderate"
    assert any("NSE Equities" in alloc["option"] for alloc in result.suggested_allocations)


def test_conservative_allocation():
    result = get_investment_recommendations(50_000, RiskTolerance.CONSERVATIVE, "long")
    options = {alloc["option"] for alloc in result.suggested_allocations}
    assert "Money Market Fund" in options
    assert "M-Akiba/Treasury Bonds" in options
    assert sum(alloc["allocation"] for alloc in result.suggested_allocations) == pytest.approx(1.0)


def test_short_timeline_overrides_risk():
    result = get_investment_recommendations(50_000, RiskTolerance.AGGRESSIVE, "short")
    options = {alloc["option"] for alloc in result.suggested_allocations}
    assert "NSE Equities" not in options
    assert any("Short timeline" in warning for warning in result.warnings)


def test_small_amount_warning():
    result = get_investment_recommendations(500, RiskTolerance.CONSERVATIVE, "long")
    assert any("Amount below KES 1,000" in warning for warning in result.warnings)

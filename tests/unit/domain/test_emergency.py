"""Unit tests for emergency fund calculations."""

import pytest

from kenya_wealth_agent.domain.emergency import calculate_emergency_fund_target


def test_negative_expenses_rejected():
    with pytest.raises(ValueError, match="monthly_expenses cannot be negative"):
        calculate_emergency_fund_target(-1)


def test_zero_or_negative_months_rejected():
    with pytest.raises(ValueError, match="months must be positive"):
        calculate_emergency_fund_target(20_000, 0)


def test_default_six_month_target():
    result = calculate_emergency_fund_target(30_000)
    assert result.target_amount == 180_000
    assert result.months_coverage == 6
    assert result.timeline_scenarios["1 year"] == pytest.approx(15_000)


def test_custom_coverage():
    result = calculate_emergency_fund_target(40_000, 3)
    assert result.target_amount == 120_000
    assert result.months_coverage == 3

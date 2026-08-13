"""Unit tests for savings strategy recommendations."""

import pytest

from kenya_wealth_agent.domain.models import FinancialGoal
from kenya_wealth_agent.domain.savings import recommend_savings_strategy


def test_invalid_goal_rejected():
    with pytest.raises(ValueError, match="Invalid goal"):
        recommend_savings_strategy("buy a spaceship", 100_000, 12)


def test_string_goal_normalized():
    result = recommend_savings_strategy("emergency fund", 60_000, 12)
    assert result.goal == "emergency_fund"
    assert result.monthly_savings_required == pytest.approx(5_000)


def test_enum_goal_accepted():
    result = recommend_savings_strategy(FinancialGoal.HOME_OWNERSHIP, 600_000, 60)
    assert result.goal == "home_ownership"
    assert result.monthly_savings_required == pytest.approx(10_000)
    vehicles = {v["name"] for v in result.recommended_vehicles}
    assert "SACCO Shares" in vehicles


def test_invalid_target_rejected():
    with pytest.raises(ValueError, match="target_amount must be positive"):
        recommend_savings_strategy(FinancialGoal.EDUCATION, 0, 12)


def test_invalid_timeline_rejected():
    with pytest.raises(ValueError, match="timeline_months must be positive"):
        recommend_savings_strategy(FinancialGoal.EDUCATION, 100_000, -1)

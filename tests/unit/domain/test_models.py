"""Unit tests for domain models."""

import pytest
from pydantic import ValidationError

from kenya_wealth_agent.domain.models import FinancialGoal, RiskTolerance, UserProfile


def test_risk_tolerance_case_insensitive_lookup():
    assert RiskTolerance._missing_("AGGRESSIVE") is RiskTolerance.AGGRESSIVE
    assert RiskTolerance._missing_("  Moderate ") is RiskTolerance.MODERATE
    assert RiskTolerance._missing_("unknown") is None


def test_user_profile_validates_age():
    with pytest.raises(ValidationError):
        UserProfile(name="Brian", age=150)


def test_user_profile_validates_negative_income():
    with pytest.raises(ValidationError):
        UserProfile(monthly_income=-1)


def test_user_profile_summary_includes_context():
    profile = UserProfile(
        name="Brian",
        age=30,
        monthly_income=100_000,
        risk_tolerance=RiskTolerance.MODERATE,
        financial_goals=[FinancialGoal.EMERGENCY_FUND],
    )
    summary = profile.summary()
    assert "Brian" in summary
    assert "KES 100,000" in summary
    assert "moderate" in summary
    assert "emergency fund" in summary

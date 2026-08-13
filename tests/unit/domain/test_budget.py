"""Unit tests for budget analysis."""

import pytest

from kenya_wealth_agent.domain.budget import analyze_budget


def test_negative_income_rejected():
    with pytest.raises(ValueError, match="income cannot be negative"):
        analyze_budget(-1, {})


def test_negative_expense_rejected():
    with pytest.raises(ValueError, match=r"expenses\[rent\] cannot be negative"):
        analyze_budget(50_000, {"rent": -1})


def test_zero_income():
    result = analyze_budget(0, {"rent": 10_000})
    assert result.total_income == 0
    assert result.savings_rate == 0
    assert result.surplus == -10_000


def test_basic_budget():
    income = 100_000
    expenses = {"rent": 30_000, "transport": 10_000, "food": 20_000, "airtime_data": 3_000}
    result = analyze_budget(income, expenses)
    assert result.total_expenses == 63_000
    assert result.surplus == 37_000
    assert result.savings_rate == pytest.approx(0.37)
    assert result.expense_breakdown["rent"] == 30.0
    assert any("surplus" in rec for rec in result.recommendations)


def test_rent_exceeds_threshold():
    result = analyze_budget(50_000, {"rent": 20_000})
    assert any("rent exceeds 30%" in rec for rec in result.recommendations)


def test_transport_exceeds_threshold():
    result = analyze_budget(50_000, {"transport": 10_000})
    assert any("Transport costs are high" in rec for rec in result.recommendations)


def test_airtime_exceeds_threshold():
    result = analyze_budget(50_000, {"airtime_data": 3_000})
    assert any("Airtime and data costs exceed 5%" in rec for rec in result.recommendations)


def test_low_savings_warning():
    result = analyze_budget(100_000, {"rent": 80_000, "food": 18_000})
    assert result.savings_rate < 0.10
    assert any("below the 10%" in rec for rec in result.recommendations)

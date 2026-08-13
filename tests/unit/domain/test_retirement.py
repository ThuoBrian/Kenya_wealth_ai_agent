"""Unit tests for retirement projections."""

import pytest

from kenya_wealth_agent.domain.retirement import project_retirement


def test_invalid_ages_rejected():
    with pytest.raises(ValueError, match="retirement_age must be greater"):
        project_retirement(30, 30, 5_000)


def test_negative_or_zero_contribution_rejected():
    with pytest.raises(ValueError, match="monthly_contribution must be positive"):
        project_retirement(30, 60, 0)


def test_basic_projection():
    result = project_retirement(30, 60, monthly_contribution=5_000, annual_return_rate=0.09)
    assert result.years_to_retirement == 30
    assert result.projected_accumulation > 5_000 * 30 * 12  # compounding beats simple sum
    assert result.monthly_contribution == 5_000


def test_zero_return_falls_back_to_simple_sum():
    result = project_retirement(30, 60, monthly_contribution=5_000, annual_return_rate=0.0)
    expected = 5_000 * 30 * 12
    assert result.projected_accumulation == pytest.approx(expected)

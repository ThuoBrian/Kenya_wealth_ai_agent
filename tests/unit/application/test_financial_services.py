"""Unit tests for financial application services."""

import pytest

from kenya_wealth_agent.application.financial_services import (
    BudgetService,
    EmergencyService,
    InvestmentService,
    RetirementService,
    SavingsService,
    TaxService,
)
from kenya_wealth_agent.domain.models import FinancialGoal, RiskTolerance


async def test_tax_service_delegates_to_domain():
    service = TaxService()
    result = await service.calculate(50_000)
    assert result.gross_salary == 50_000
    assert result.paye > 0


async def test_budget_service_delegates_to_domain():
    service = BudgetService()
    result = await service.analyze(100_000, {"rent": 30_000})
    assert result.total_income == 100_000
    assert result.total_expenses == 30_000


async def test_investment_service_delegates_to_domain():
    service = InvestmentService()
    result = await service.recommend(10_000, RiskTolerance.MODERATE, "long")
    assert result.risk_profile == "moderate"


async def test_investment_service_invalid_risk():
    service = InvestmentService()
    with pytest.raises(ValueError, match="Invalid risk tolerance"):
        await service.recommend(10_000, "unknown", "long")


async def test_emergency_service_delegates_to_domain():
    service = EmergencyService()
    result = await service.calculate_target(30_000)
    assert result.target_amount == 180_000


async def test_retirement_service_delegates_to_domain():
    service = RetirementService()
    result = await service.project(30, 60, 5_000)
    assert result.years_to_retirement == 30
    assert result.projected_accumulation > 0


async def test_savings_service_delegates_to_domain():
    service = SavingsService()
    result = await service.recommend(FinancialGoal.EDUCATION, 120_000, 12)
    assert result.goal == "education"
    assert result.monthly_savings_required == pytest.approx(10_000)


async def test_savings_service_invalid_goal():
    service = SavingsService()
    with pytest.raises(ValueError, match="Invalid goal"):
        await service.recommend("spaceship", 100_000, 12)

"""Direct financial calculation routes.

These endpoints expose the domain calculators without going through the LLM.
They are useful for the frontend's dedicated tool views, third-party clients,
and quick sanity checks.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from kenya_wealth_agent.domain import (
    BudgetAnalysis,
    EmergencyFundTarget,
    FinancialGoal,
    InvestmentRecommendation,
    PayeCalculation,
    RetirementProjection,
    RiskTolerance,
    SavingsStrategy,
)
from kenya_wealth_agent.interfaces.web.dependencies import AppComponents, get_financial_services

router = APIRouter(tags=["tools"])


class BudgetRequest(BaseModel):
    """Payload for budget analysis."""

    income: float = Field(..., gt=0)
    expenses: dict[str, float]

    @field_validator("expenses")
    @classmethod
    def _non_negative_expenses(cls, value: dict[str, float]) -> dict[str, float]:
        if any(amount < 0 for amount in value.values()):
            raise ValueError("Expense amounts must be non-negative")
        return value


class TaxRequest(BaseModel):
    """Payload for PAYE calculation."""

    gross_salary: float = Field(..., gt=0)


class InvestmentRequest(BaseModel):
    """Payload for investment recommendations."""

    amount: float = Field(..., gt=0)
    risk_tolerance: str
    timeline: str


class EmergencyRequest(BaseModel):
    """Payload for emergency fund calculation."""

    monthly_expenses: float = Field(..., gt=0)
    months: int = Field(default=6, ge=1)


class RetirementRequest(BaseModel):
    """Payload for retirement projection."""

    current_age: int = Field(..., ge=18, le=100)
    retirement_age: int = Field(..., ge=19, le=100)
    monthly_contribution: float = Field(..., gt=0)
    annual_return_rate: float = Field(default=0.09, ge=0, le=1)


class SavingsRequest(BaseModel):
    """Payload for savings strategy recommendation."""

    goal: str
    target_amount: float = Field(..., gt=0)
    timeline_months: int = Field(..., ge=1)


def _components() -> AppComponents:
    """Dependency shim to keep router signatures short."""
    return get_financial_services()


@router.post("/budget", response_model=BudgetAnalysis)
async def analyze_budget(
    request: BudgetRequest,
    components: AppComponents = Depends(_components),
) -> BudgetAnalysis:
    """Analyze a budget and return recommendations."""
    return await components.budget_service.analyze(
        income=request.income,
        expenses=request.expenses,
    )


@router.post("/tax", response_model=PayeCalculation)
async def calculate_tax(
    request: TaxRequest,
    components: AppComponents = Depends(_components),
) -> PayeCalculation:
    """Calculate PAYE and statutory deductions for a gross salary."""
    return await components.tax_service.calculate(gross_salary=request.gross_salary)


@router.post("/invest", response_model=InvestmentRecommendation)
async def recommend_investment(
    request: InvestmentRequest,
    components: AppComponents = Depends(_components),
) -> InvestmentRecommendation:
    """Recommend an investment allocation given amount, risk, and timeline."""
    try:
        risk = RiskTolerance(request.risk_tolerance)
    except ValueError as exc:
        allowed = ", ".join(member.value for member in RiskTolerance)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"risk_tolerance must be one of: {allowed}",
        ) from exc
    return await components.investment_service.recommend(
        amount=request.amount,
        risk_tolerance=risk,
        timeline=request.timeline,
    )


@router.post("/emergency", response_model=EmergencyFundTarget)
async def calculate_emergency_fund(
    request: EmergencyRequest,
    components: AppComponents = Depends(_components),
) -> EmergencyFundTarget:
    """Calculate an emergency fund target."""
    return await components.emergency_service.calculate_target(
        monthly_expenses=request.monthly_expenses,
        months=request.months,
    )


@router.post("/retirement", response_model=RetirementProjection)
async def project_retirement(
    request: RetirementRequest,
    components: AppComponents = Depends(_components),
) -> RetirementProjection:
    """Project retirement accumulation."""
    return await components.retirement_service.project(
        current_age=request.current_age,
        retirement_age=request.retirement_age,
        monthly_contribution=request.monthly_contribution,
        annual_return_rate=request.annual_return_rate,
    )


@router.post("/savings", response_model=SavingsStrategy)
async def recommend_savings(
    request: SavingsRequest,
    components: AppComponents = Depends(_components),
) -> SavingsStrategy:
    """Recommend a savings strategy for a financial goal."""
    try:
        goal = FinancialGoal(request.goal)
    except ValueError as exc:
        allowed = ", ".join(member.value for member in FinancialGoal)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"goal must be one of: {allowed}",
        ) from exc
    return await components.savings_service.recommend(
        goal=goal,
        target_amount=request.target_amount,
        timeline_months=request.timeline_months,
    )

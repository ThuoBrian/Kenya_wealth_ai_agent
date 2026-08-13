"""Application services that wrap pure domain calculations.

Each service here is a thin, async-aware orchestrator around the domain layer.
They validate inputs (often via Pydantic models) and return typed results that
interface layers can serialize directly.
"""

from datetime import datetime
from pathlib import Path

import structlog

from kenya_wealth_agent.application.ports import ReportRenderer
from kenya_wealth_agent.domain import (
    BudgetAnalysis,
    EmergencyFundTarget,
    FinancialGoal,
    InvestmentRecommendation,
    PayeCalculation,
    RetirementProjection,
    RiskTolerance,
    SavingsStrategy,
    analyze_budget,
    calculate_emergency_fund_target,
    calculate_tax,
    get_investment_recommendations,
    project_retirement,
    recommend_savings_strategy,
)

logger = structlog.get_logger()


class TaxService:
    """Application service for PAYE and statutory deduction calculations."""

    async def calculate(self, gross_salary: float) -> PayeCalculation:
        """Calculate PAYE and statutory deductions."""
        return calculate_tax(gross_salary)


class BudgetService:
    """Application service for budget analysis."""

    async def analyze(
        self,
        income: float,
        expenses: dict[str, float],
    ) -> BudgetAnalysis:
        """Analyze a user's budget."""
        return analyze_budget(income, expenses)


class InvestmentService:
    """Application service for investment recommendations."""

    async def recommend(
        self,
        amount: float,
        risk_tolerance: RiskTolerance | str,
        timeline: str,
    ) -> InvestmentRecommendation:
        """Recommend an investment allocation."""
        return get_investment_recommendations(amount, risk_tolerance, timeline)


class EmergencyService:
    """Application service for emergency fund calculations."""

    async def calculate_target(
        self,
        monthly_expenses: float,
        months: int = 6,
    ) -> EmergencyFundTarget:
        """Calculate an emergency fund target."""
        return calculate_emergency_fund_target(monthly_expenses, months)


class RetirementService:
    """Application service for retirement projections."""

    async def project(
        self,
        current_age: int,
        retirement_age: int,
        monthly_contribution: float,
        annual_return_rate: float = 0.09,
    ) -> RetirementProjection:
        """Project retirement accumulation from regular contributions."""
        return project_retirement(
            current_age, retirement_age, monthly_contribution, annual_return_rate
        )


class SavingsService:
    """Application service for savings strategy recommendations."""

    async def recommend(
        self,
        goal: FinancialGoal | str,
        target_amount: float,
        timeline_months: int,
    ) -> SavingsStrategy:
        """Recommend a savings strategy for a goal."""
        return recommend_savings_strategy(goal, target_amount, timeline_months)


class ReportService:
    """Application service for generating and saving conversation reports."""

    def __init__(
        self,
        renderer: ReportRenderer,
        output_dir: str | Path = "output",
        filename: str = "kenya_wealth_advice.html",
    ):
        self.renderer = renderer
        self.output_dir = Path(output_dir)
        self.filename = filename

    async def export(
        self,
        messages: list[dict[str, str]],
        session_start: datetime | None = None,
        custom_path: str | Path | None = None,
    ) -> str:
        """Render and save a report, returning the absolute file path.

        Args:
            messages: Conversation history.
            session_start: Optional session start time for report metadata.
            custom_path: Optional full path to write the report to.

        Returns:
            Absolute path of the saved report file.
        """
        html = self.renderer.render(messages, session_start)

        path = Path(custom_path) if custom_path else self.output_dir / self.filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        logger.info("report_saved", path=str(path.resolve()))
        return str(path.resolve())

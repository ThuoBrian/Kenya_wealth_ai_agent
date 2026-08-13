"""Domain models for Kenya Wealth Agent.

Models in this module are pure data structures with validation.  They know
nothing about LLMs, web frameworks, or CLI presentation.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FinancialGoal(str, Enum):
    """Financial goals that users can set for themselves."""

    EMERGENCY_FUND = "emergency_fund"
    RETIREMENT = "retirement"
    HOME_OWNERSHIP = "home_ownership"
    EDUCATION = "education"
    INVESTMENT = "investment"
    DEBT_REDUCTION = "debt_reduction"


class RiskTolerance(str, Enum):
    """Risk tolerance levels for investment recommendations."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

    @classmethod
    def _missing_(cls, value: object) -> Optional["RiskTolerance"]:
        """Allow case-insensitive lookup."""
        if isinstance(value, str):
            lowered = value.lower().strip()
            for member in cls:
                if member.value == lowered:
                    return member
        return None


class UserProfile(BaseModel):
    """User financial profile for personalized advice.

    Attributes:
        name: User's name.
        age: User's age in years.
        monthly_income: Monthly income in KES.
        monthly_expenses: Monthly expenses in KES.
        current_savings: Current savings in KES.
        risk_tolerance: User's risk tolerance level.
        financial_goals: List of user's financial goals.
        has_mpesa: Whether user has an MPesa account.
        has_bank_account: Whether user has a bank account.
        is_sacco_member: Whether user is a SACCO member.
    """

    model_config = ConfigDict(use_enum_values=True)

    name: str | None = Field(default=None, max_length=100)
    age: int | None = Field(default=None, ge=18, le=120)
    monthly_income: float | None = Field(default=None, ge=0)
    monthly_expenses: float | None = Field(default=None, ge=0)
    current_savings: float | None = Field(default=None, ge=0)
    risk_tolerance: RiskTolerance | None = None
    financial_goals: list[FinancialGoal] = Field(default_factory=list)
    has_mpesa: bool = True
    has_bank_account: bool = True
    is_sacco_member: bool = False

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str | None) -> str | None:
        return value.strip() if value else value

    def summary(self) -> str:
        """Return a concise, human-readable summary for prompt injection."""
        parts: list[str] = []
        if self.name:
            parts.append(f"Name: {self.name}")
        if self.age is not None:
            parts.append(f"Age: {self.age}")
        if self.monthly_income is not None:
            parts.append(f"Monthly income: KES {self.monthly_income:,.2f}")
        if self.monthly_expenses is not None:
            parts.append(f"Monthly expenses: KES {self.monthly_expenses:,.2f}")
        if self.current_savings is not None:
            parts.append(f"Current savings: KES {self.current_savings:,.2f}")
        if self.risk_tolerance:
            risk_label = (
                self.risk_tolerance.value
                if isinstance(self.risk_tolerance, RiskTolerance)
                else self.risk_tolerance
            )
            parts.append(f"Risk tolerance: {risk_label}")
        if self.financial_goals:
            goals = ", ".join(
                (g.value if isinstance(g, FinancialGoal) else g).replace("_", " ")
                for g in self.financial_goals
            )
            parts.append(f"Goals: {goals}")
        parts.append(f"MPesa: {'yes' if self.has_mpesa else 'no'}")
        parts.append(f"Bank account: {'yes' if self.has_bank_account else 'no'}")
        parts.append(f"SACCO member: {'yes' if self.is_sacco_member else 'no'}")
        return "\n".join(parts)


class PayeCalculation(BaseModel):
    """Result of a Kenyan PAYE/statutory deduction calculation."""

    model_config = ConfigDict(frozen=True)

    gross_salary: float
    paye: float
    nhif_shif: float
    nssf: float
    housing_levy: float
    total_deductions: float
    net_salary: float


class BudgetAnalysis(BaseModel):
    """Result of a budget analysis."""

    total_income: float
    total_expenses: float
    surplus: float
    savings_rate: float
    expense_breakdown: dict[str, float]
    recommendations: list[str]


class InvestmentRecommendation(BaseModel):
    """Result of an investment recommendation."""

    amount: float
    risk_profile: str
    timeline: str
    suggested_allocations: list[dict[str, object]]
    warnings: list[str]


class EmergencyFundTarget(BaseModel):
    """Result of an emergency fund calculation."""

    target_amount: float
    monthly_expenses: float
    months_coverage: int
    savings_strategies: list[dict[str, str]]
    timeline_scenarios: dict[str, float]


class RetirementProjection(BaseModel):
    """Result of a basic retirement projection."""

    current_age: int
    retirement_age: int
    years_to_retirement: int
    monthly_contribution: float
    projected_accumulation: float
    assumptions: dict[str, object]


class SavingsStrategy(BaseModel):
    """Result of a savings strategy recommendation."""

    goal: str
    target_amount: float
    timeline_months: int
    monthly_savings_required: float
    recommended_vehicles: list[dict[str, str]]

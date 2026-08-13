"""Domain layer for Kenya Wealth Agent.

This package contains pure business logic: models, value objects, validation,
and financial calculations.  It has no dependencies on web frameworks, LLM
clients, or CLI presentation.
"""

from kenya_wealth_agent.domain.budget import analyze_budget
from kenya_wealth_agent.domain.emergency import calculate_emergency_fund_target
from kenya_wealth_agent.domain.investment import get_investment_recommendations
from kenya_wealth_agent.domain.models import (
    BudgetAnalysis,
    EmergencyFundTarget,
    FinancialGoal,
    InvestmentRecommendation,
    PayeCalculation,
    RetirementProjection,
    RiskTolerance,
    SavingsStrategy,
    UserProfile,
)
from kenya_wealth_agent.domain.retirement import project_retirement
from kenya_wealth_agent.domain.savings import recommend_savings_strategy
from kenya_wealth_agent.domain.tax import calculate_tax

__all__ = [
    "BudgetAnalysis",
    "EmergencyFundTarget",
    "FinancialGoal",
    "InvestmentRecommendation",
    "PayeCalculation",
    "RetirementProjection",
    "RiskTolerance",
    "SavingsStrategy",
    "UserProfile",
    "analyze_budget",
    "calculate_emergency_fund_target",
    "calculate_tax",
    "get_investment_recommendations",
    "project_retirement",
    "recommend_savings_strategy",
]

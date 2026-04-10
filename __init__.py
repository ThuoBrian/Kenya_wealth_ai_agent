"""
Kenya Wealth & Finance Agent

A personalized financial advisor for the Kenyan market context.
Provides advice on budgeting, saving, investing, and wealth building.
"""

from .agent import KenyaWealthAgent
from .models.user import FinancialGoal, RiskTolerance, UserProfile
from .services.budget import analyze_budget
from .services.tax import calculate_tax
from .services.investment import get_investment_recommendations
from .services.emergency import calculate_emergency_fund_target
from .config import get_config, Config, AVAILABLE_MODELS

__version__ = "1.0.0"
__author__ = "Brian Thuo"

__all__ = [
    # Main agent
    "KenyaWealthAgent",
    # Models
    "FinancialGoal",
    "RiskTolerance",
    "UserProfile",
    # Services
    "analyze_budget",
    "calculate_tax",
    "get_investment_recommendations",
    "calculate_emergency_fund_target",
    # Config
    "get_config",
    "Config",
    "AVAILABLE_MODELS",
]
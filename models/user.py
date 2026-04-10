"""
Data models for user financial profiles.

This module contains the core data structures used throughout
the Kenya Wealth Agent for representing user financial information.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class FinancialGoal(Enum):
    """Financial goals that users can set for themselves."""
    EMERGENCY_FUND = "emergency_fund"
    RETIREMENT = "retirement"
    HOME_OWNERSHIP = "home_ownership"
    EDUCATION = "education"
    INVESTMENT = "investment"
    DEBT_REDUCTION = "debt_reduction"


class RiskTolerance(Enum):
    """Risk tolerance levels for investment recommendations."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


@dataclass
class UserProfile:
    """User financial profile for personalized advice.

    Attributes:
        name: User's name
        age: User's age in years
        monthly_income: Monthly income in KES (Kenyan Shillings)
        monthly_expenses: Monthly expenses in KES
        current_savings: Current savings in KES
        risk_tolerance: User's risk tolerance level
        financial_goals: List of user's financial goals
        has_mpesa: Whether user has MPesa account
        has_bank_account: Whether user has bank account
        is_cic_member: Whether user is a SACCO member
    """
    name: str
    age: int
    monthly_income: float  # In KES
    monthly_expenses: float  # In KES
    current_savings: float  # In KES
    risk_tolerance: RiskTolerance
    financial_goals: List[FinancialGoal]
    has_mpesa: bool = True
    has_bank_account: bool = True
    is_cic_member: bool = False  # SACCO membership
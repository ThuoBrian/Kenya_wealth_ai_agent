"""
Emergency fund calculation service for Kenya Wealth Agent.

This module provides emergency fund target calculations and
savings strategies.
"""

from typing import Dict, Any, List


def calculate_emergency_fund_target(
    monthly_expenses: float, months: int = 6
) -> Dict[str, Any]:
    """Calculate emergency fund target and timeline.

    Args:
        monthly_expenses: Monthly expenses in KES
        months: Number of months of coverage (default: 6)

    Returns:
        Dictionary containing:
            - target_amount: Total emergency fund target in KES
            - monthly_expenses: Input monthly expenses
            - months_coverage: Number of months covered
            - savings_strategies: List of savings options
            - timeline_scenarios: Monthly savings needed for different timelines
    """
    target = monthly_expenses * months

    savings_strategies: List[Dict[str, str]] = [
        {
            "method": "M-Shwari Lock Savings",
            "rate": "6-8%",
            "pros": "Easy to set up, automatic savings",
        },
        {
            "method": "SACCO Savings",
            "rate": "8-12%",
            "pros": "Higher returns, access to loans",
        },
        {
            "method": "Money Market Fund",
            "rate": "8-10%",
            "pros": "Professional management, liquid",
        },
    ]

    timeline_scenarios: Dict[str, float] = {
        "1 year": target / 12,
        "2 years": target / 24,
        "3 years": target / 36,
    }

    return {
        "target_amount": target,
        "monthly_expenses": monthly_expenses,
        "months_coverage": months,
        "savings_strategies": savings_strategies,
        "timeline_scenarios": timeline_scenarios,
    }
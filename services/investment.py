"""
Investment recommendation service for Kenyan market.

This module provides functions for generating investment
recommendations based on risk profile and timeline.
"""

from typing import Dict, Any, List

from config.constants import INVESTMENT_OPTIONS


def get_investment_recommendations(
    amount: float, risk_tolerance: str, timeline: str
) -> Dict[str, Any]:
    """Get investment recommendations based on profile.

    Provides personalized investment recommendations based on
    amount, risk tolerance, and investment timeline.

    Args:
        amount: Investment amount in KES
        risk_tolerance: Risk tolerance level ('conservative', 'moderate', 'aggressive')
        timeline: Investment timeline ('short', '1-2 years', 'medium', '5+ years', 'long')

    Returns:
        Dictionary containing:
            - amount: Investment amount
            - risk_profile: Risk tolerance level
            - timeline: Investment timeline
            - suggested_allocations: List of recommended allocations
            - warnings: List of relevant warnings
    """
    risk_level = risk_tolerance.lower()

    recommendations: Dict[str, Any] = {
        "amount": amount,
        "risk_profile": risk_tolerance,
        "timeline": timeline,
        "suggested_allocations": [],
        "warnings": [],
    }

    # Base recommendations on risk profile
    if risk_level == "conservative":
        recommendations["suggested_allocations"] = [
            {"option": "Money Market Fund", "allocation": 0.40, "expected_return": "8-10%"},
            {"option": "M-Akiba/Treasury Bonds", "allocation": 0.35, "expected_return": "10-14%"},
            {"option": "SACCO Shares", "allocation": 0.25, "expected_return": "8-15%"},
        ]
    elif risk_level == "moderate":
        recommendations["suggested_allocations"] = [
            {"option": "Money Market Fund", "allocation": 0.25, "expected_return": "8-10%"},
            {"option": "NSE Equities (ETF/Direct)", "allocation": 0.35, "expected_return": "10-20%"},
            {"option": "SACCO Shares", "allocation": 0.20, "expected_return": "8-15%"},
            {"option": "Unit Trusts", "allocation": 0.20, "expected_return": "10-15%"},
        ]
    else:  # Aggressive
        recommendations["suggested_allocations"] = [
            {"option": "NSE Equities", "allocation": 0.50, "expected_return": "Variable"},
            {"option": "Real Estate/Land", "allocation": 0.30, "expected_return": "15-25%"},
            {"option": "Unit Trusts", "allocation": 0.20, "expected_return": "10-15%"},
        ]

    # Timeline adjustments
    if timeline in ["short", "1-2 years"]:
        recommendations["warnings"].append(
            "Short timeline: Prioritize liquid investments. "
            "Avoid locking funds in fixed deposits or real estate."
        )
        # Adjust for short timeline - more conservative
        recommendations["suggested_allocations"] = [
            {"option": "Money Market Fund", "allocation": 0.60, "expected_return": "8-10%"},
            {"option": "SACCO Shares", "allocation": 0.40, "expected_return": "8-15%"},
        ]

    # Minimum investment warnings
    if amount < 1000:
        recommendations["warnings"].append(
            "Amount below KES 1,000. Consider M-Shwari Lock Savings "
            "or starting with a SACCO."
        )

    return recommendations
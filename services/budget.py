"""
Budget analysis service for Kenyan financial context.

This module provides functions for analyzing budgets and
providing Kenyan-specific financial recommendations.
"""

from typing import Dict, Any, List


def analyze_budget(income: float, expenses: Dict[str, float]) -> Dict[str, Any]:
    """Analyze a user's budget and provide recommendations.

    Analyzes income vs expenses and generates personalized
    recommendations based on Kenyan financial context.

    Args:
        income: Monthly income in KES
        expenses: Dictionary of expense categories and amounts in KES

    Returns:
        Dictionary containing:
            - total_income: Monthly income
            - total_expenses: Sum of all expenses
            - surplus: Income minus expenses
            - savings_rate: Surplus as percentage of income
            - expense_breakdown: Percentage breakdown by category
            - recommendations: List of personalized recommendations
    """
    total_expenses = sum(expenses.values())
    surplus = income - total_expenses
    savings_rate = surplus / income if income > 0 else 0

    # Calculate percentages
    expense_percentages = {
        category: (amount / income * 100) if income > 0 else 0
        for category, amount in expenses.items()
    }

    analysis = {
        "total_income": income,
        "total_expenses": total_expenses,
        "surplus": surplus,
        "savings_rate": savings_rate,
        "expense_breakdown": expense_percentages,
        "recommendations": [],
    }

    # Generate recommendations based on Kenyan context
    recommendations: List[str] = []

    if savings_rate < 0.10:
        recommendations.append(
            "Your savings rate is below 10%. Aim for at least 20% "
            "(the recommended rate in Kenya). Consider reviewing discretionary "
            "spending like entertainment and airtime."
        )

    if expenses.get("rent", 0) > income * 0.30:
        recommendations.append(
            "Your rent exceeds 30% of income. Consider house-sharing, "
            "moving to a more affordable area, or negotiating with your landlord. "
            "In Nairobi, areas further from CBD often offer better value."
        )

    if expenses.get("transport", 0) > income * 0.15:
        recommendations.append(
            "Transport costs are high. Consider: using matatus instead of Uber/Bolt, "
            "carpooling with colleagues, or living closer to work if rent savings "
            "offset transport costs."
        )

    if expenses.get("airtime_data", 0) > income * 0.05:
        recommendations.append(
            "Airtime and data costs exceed 5% of income. Consider: buying data bundles "
            "in bulk, using free WiFi where available, or switching to more affordable "
            "providers like Telkom."
        )

    if surplus > 0:
        recommendations.append(
            f"You have KES {surplus:,.0f} surplus monthly. Allocate this to: "
            f"1) Emergency fund first, 2) SACCO contributions, "
            f"3) Money market funds or unit trusts."
        )

    analysis["recommendations"] = recommendations
    return analysis
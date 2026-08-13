"""Budget analysis domain logic for Kenyan financial context."""

from kenya_wealth_agent.config.constants import (
    AIRTIME_DATA_TARGET,
    MIN_SAVINGS_RATE_TARGET,
    RENT_TARGET,
    TRANSPORT_TARGET,
)
from kenya_wealth_agent.domain.models import BudgetAnalysis
from kenya_wealth_agent.domain.validators import require_non_negative


def analyze_budget(income: float, expenses: dict[str, float]) -> BudgetAnalysis:
    """Analyze a user's budget and provide Kenyan-specific recommendations.

    Args:
        income: Monthly income in KES.
        expenses: Dictionary of expense categories and amounts in KES.

    Returns:
        A ``BudgetAnalysis`` containing totals, savings rate, breakdown, and
        recommendations.

    Raises:
        ValueError: If ``income`` or any expense amount is negative.
    """
    income = require_non_negative(income, "income")
    validated_expenses = {
        category: require_non_negative(amount, f"expenses[{category}]")
        for category, amount in (expenses or {}).items()
    }

    total_expenses = sum(validated_expenses.values())
    surplus = income - total_expenses
    savings_rate = surplus / income if income > 0 else 0.0

    expense_percentages = {
        category: (amount / income * 100.0) if income > 0 else 0.0
        for category, amount in validated_expenses.items()
    }

    recommendations = _generate_recommendations(income, savings_rate, validated_expenses, surplus)

    return BudgetAnalysis(
        total_income=income,
        total_expenses=total_expenses,
        surplus=surplus,
        savings_rate=savings_rate,
        expense_breakdown=expense_percentages,
        recommendations=recommendations,
    )


def _generate_recommendations(
    income: float,
    savings_rate: float,
    expenses: dict[str, float],
    surplus: float,
) -> list[str]:
    """Build recommendation strings based on Kenyan financial context."""
    recommendations: list[str] = []

    if savings_rate < MIN_SAVINGS_RATE_TARGET:
        recommendations.append(
            f"Your savings rate is {savings_rate:.1%}, below the {MIN_SAVINGS_RATE_TARGET:.0%} "
            "minimum. Aim for at least 20% (the recommended rate in Kenya). "
            "Consider reviewing discretionary spending like entertainment and airtime."
        )

    if income > 0 and expenses.get("rent", 0) > income * RENT_TARGET:
        recommendations.append(
            f"Your rent exceeds {RENT_TARGET:.0%} of income. Consider house-sharing, "
            "moving to a more affordable area, or negotiating with your landlord. "
            "In Nairobi, areas further from CBD often offer better value."
        )

    if income > 0 and expenses.get("transport", 0) > income * TRANSPORT_TARGET:
        recommendations.append(
            "Transport costs are high. Consider: using matatus instead of Uber/Bolt, "
            "carpooling with colleagues, or living closer to work if rent savings "
            "offset transport costs."
        )

    if income > 0 and expenses.get("airtime_data", 0) > income * AIRTIME_DATA_TARGET:
        recommendations.append(
            "Airtime and data costs exceed 5% of income. Consider: buying data bundles "
            "in bulk, using free WiFi where available, or switching to more affordable "
            "providers like Telkom."
        )

    if surplus > 0:
        recommendations.append(
            f"You have KES {surplus:,.0f} surplus monthly. Allocate this to: "
            "1) Emergency fund first, 2) SACCO contributions, "
            "3) Money market funds or unit trusts."
        )

    return recommendations

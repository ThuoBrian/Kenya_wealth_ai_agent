"""Emergency fund calculation domain logic for Kenya Wealth Agent."""

from kenya_wealth_agent.domain.models import EmergencyFundTarget
from kenya_wealth_agent.domain.validators import require_non_negative, require_positive


def calculate_emergency_fund_target(
    monthly_expenses: float, months: int = 6
) -> EmergencyFundTarget:
    """Calculate emergency fund target and timeline.

    Args:
        monthly_expenses: Monthly expenses in KES.
        months: Number of months of coverage (default: 6).

    Returns:
        An ``EmergencyFundTarget`` with target amount, strategies, and scenarios.

    Raises:
        ValueError: If ``monthly_expenses`` or ``months`` is negative/zero.
    """
    monthly_expenses = require_non_negative(monthly_expenses, "monthly_expenses")
    months = int(require_positive(months, "months"))

    target = monthly_expenses * months

    savings_strategies: list[dict[str, str]] = [
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

    timeline_scenarios: dict[str, float] = {
        "1 year": target / 12,
        "2 years": target / 24,
        "3 years": target / 36,
    }

    return EmergencyFundTarget(
        target_amount=target,
        monthly_expenses=monthly_expenses,
        months_coverage=months,
        savings_strategies=savings_strategies,
        timeline_scenarios=timeline_scenarios,
    )

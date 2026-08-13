"""Savings strategy domain logic for Kenya Wealth Agent."""

from kenya_wealth_agent.domain.models import FinancialGoal, SavingsStrategy
from kenya_wealth_agent.domain.validators import require_positive


def recommend_savings_strategy(
    goal: FinancialGoal | str,
    target_amount: float,
    timeline_months: int,
) -> SavingsStrategy:
    """Recommend a savings strategy for a specific financial goal.

    Args:
        goal: The financial goal as a ``FinancialGoal`` enum or string.
        target_amount: Target amount to save in KES.
        timeline_months: Number of months over which to reach the goal.

    Returns:
        A ``SavingsStrategy`` with required monthly savings and vehicle suggestions.

    Raises:
        ValueError: If ``target_amount`` or ``timeline_months`` is invalid.
    """
    parsed_goal = _parse_goal(goal)
    target_amount = require_positive(target_amount, "target_amount")
    timeline_months = int(require_positive(timeline_months, "timeline_months"))

    monthly_savings = target_amount / timeline_months

    recommended_vehicles = _vehicles_for_goal(parsed_goal)

    return SavingsStrategy(
        goal=parsed_goal.value,
        target_amount=target_amount,
        timeline_months=timeline_months,
        monthly_savings_required=round(monthly_savings, 2),
        recommended_vehicles=recommended_vehicles,
    )


def _parse_goal(value: FinancialGoal | str) -> FinancialGoal:
    """Normalize a goal value to the enum.

    Raises:
        ValueError: If the value cannot be mapped to a known goal.
    """
    if isinstance(value, FinancialGoal):
        return value
    if isinstance(value, str):
        value = value.strip().lower().replace(" ", "_")
        try:
            return FinancialGoal(value)
        except ValueError as exc:
            allowed = ", ".join(g.value for g in FinancialGoal)
            raise ValueError(f"Invalid goal {value!r}. Expected one of: {allowed}.") from exc
    allowed = ", ".join(g.value for g in FinancialGoal)
    raise ValueError(f"Invalid goal {value!r}. Expected one of: {allowed}.")


def _vehicles_for_goal(goal: FinancialGoal) -> list[dict[str, str]]:
    """Return recommended savings vehicles for a given goal."""
    common = [
        {"name": "Money Market Fund", "expected_return": "8-10%", "liquidity": "High"},
    ]

    if goal is FinancialGoal.EMERGENCY_FUND:
        return [
            {"name": "M-Shwari Lock Savings", "expected_return": "6-8%", "liquidity": "High"},
            {"name": "Money Market Fund", "expected_return": "8-10%", "liquidity": "High"},
            {"name": "SACCO Savings", "expected_return": "8-12%", "liquidity": "Medium"},
        ]
    if goal is FinancialGoal.RETIREMENT:
        return [
            {"name": "NSSF (mandatory)", "expected_return": "Variable", "liquidity": "Very Low"},
            {"name": "Personal Pension Plan", "expected_return": "8-12%", "liquidity": "Low"},
            {
                "name": "Unit Trust / Balanced Fund",
                "expected_return": "9-13%",
                "liquidity": "Medium",
            },
        ]
    if goal is FinancialGoal.HOME_OWNERSHIP:
        return [
            {"name": "SACCO Shares", "expected_return": "8-15%", "liquidity": "Low"},
            {"name": "Money Market Fund", "expected_return": "8-10%", "liquidity": "High"},
            {
                "name": "Treasury Bonds / M-Akiba",
                "expected_return": "10-15%",
                "liquidity": "Medium",
            },
        ]
    if goal is FinancialGoal.EDUCATION:
        return [
            {
                "name": "Education Insurance / Policy",
                "expected_return": "6-10%",
                "liquidity": "Low",
            },
            {"name": "Money Market Fund", "expected_return": "8-10%", "liquidity": "High"},
            {"name": "Unit Trust", "expected_return": "10-15%", "liquidity": "Medium"},
        ]
    if goal is FinancialGoal.DEBT_REDUCTION:
        return [
            {"name": "Dedicated savings account", "expected_return": "0%", "liquidity": "High"},
            {"name": "Money Market Fund", "expected_return": "8-10%", "liquidity": "High"},
        ]

    # INVESTMENT and fallback
    return [
        *common,
        {"name": "Unit Trusts", "expected_return": "10-15%", "liquidity": "Medium"},
        {"name": "SACCO Shares", "expected_return": "8-15%", "liquidity": "Low"},
    ]

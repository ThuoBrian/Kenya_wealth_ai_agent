"""Retirement planning domain logic for Kenya Wealth Agent.

Provides a simplified projection based on regular contributions and a assumed
real rate of return.  This is educational only and not actuarial advice.
"""

from kenya_wealth_agent.config.constants import NSSF_MAX
from kenya_wealth_agent.domain.models import RetirementProjection
from kenya_wealth_agent.domain.validators import require_positive


def project_retirement(
    current_age: int,
    retirement_age: int,
    monthly_contribution: float,
    annual_return_rate: float = 0.09,
) -> RetirementProjection:
    """Project retirement accumulation from regular contributions.

    Uses a simplified future-value-of-annuity formula with monthly compounding:

        FV = PMT * (((1 + r/12)^n - 1) / (r/12))

    where ``n`` is the number of months until retirement and ``r`` is the annual
    return rate.  If ``r`` is 0, the formula falls back to simple accumulation.

    Args:
        current_age: User's current age in years.
        retirement_age: Desired retirement age in years.
        monthly_contribution: Monthly retirement savings in KES.
        annual_return_rate: Assumed annual real return rate (default 9%).

    Returns:
        A ``RetirementProjection`` with years to retirement and projected total.

    Raises:
        ValueError: If ages or contributions are invalid, or if retirement age
            is not greater than current age.
    """
    current_age = int(require_positive(current_age, "current_age"))
    retirement_age = int(require_positive(retirement_age, "retirement_age"))
    monthly_contribution = require_positive(monthly_contribution, "monthly_contribution")

    if retirement_age <= current_age:
        raise ValueError("retirement_age must be greater than current_age")

    years_to_retirement = retirement_age - current_age
    months = years_to_retirement * 12
    monthly_rate = annual_return_rate / 12

    if monthly_rate == 0:
        projected = monthly_contribution * months
    else:
        projected = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)

    return RetirementProjection(
        current_age=current_age,
        retirement_age=retirement_age,
        years_to_retirement=years_to_retirement,
        monthly_contribution=monthly_contribution,
        projected_accumulation=round(projected, 2),
        assumptions={
            "annual_return_rate": annual_return_rate,
            "months": months,
            "monthly_rate": monthly_rate,
            "nssf_monthly_max_note": (
                f"NSSF employee contribution is capped at KES {NSSF_MAX:,.2f}/month. "
                "Consider supplementing NSSF with a personal pension scheme."
            ),
        },
    )

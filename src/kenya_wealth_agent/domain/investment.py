"""Investment recommendation domain logic for Kenyan market."""

from typing import Any

from kenya_wealth_agent.config.constants import (
    AGGRESSIVE_ALLOCATION,
    CONSERVATIVE_ALLOCATION,
    MODERATE_ALLOCATION,
    SHORT_TIMELINE_ALLOCATION,
)
from kenya_wealth_agent.domain.models import InvestmentRecommendation, RiskTolerance
from kenya_wealth_agent.domain.validators import require_non_negative


def get_investment_recommendations(
    amount: float,
    risk_tolerance: RiskTolerance | str,
    timeline: str,
) -> InvestmentRecommendation:
    """Get investment recommendations based on profile.

    Args:
        amount: Investment amount in KES.
        risk_tolerance: Risk tolerance level as a ``RiskTolerance`` enum or a
            supported string (case-insensitive).
        timeline: Investment timeline (e.g. 'short', '1-2 years', 'medium',
            '5+ years', 'long').

    Returns:
        An ``InvestmentRecommendation`` containing allocations and warnings.

    Raises:
        ValueError: If ``amount`` is negative or ``risk_tolerance`` is invalid.
    """
    amount = require_non_negative(amount, "amount")
    risk = _parse_risk_tolerance(risk_tolerance)

    allocations = _allocations_for_risk(risk)
    warnings: list[str] = []

    if _is_short_timeline(timeline):
        warnings.append(
            "Short timeline: Prioritize liquid investments. "
            "Avoid locking funds in fixed deposits or real estate."
        )
        allocations = SHORT_TIMELINE_ALLOCATION

    if amount < 1000:
        warnings.append(
            "Amount below KES 1,000. Consider M-Shwari Lock Savings or starting with a SACCO."
        )

    return InvestmentRecommendation(
        amount=amount,
        risk_profile=risk.value,
        timeline=timeline,
        suggested_allocations=allocations,
        warnings=warnings,
    )


def _parse_risk_tolerance(value: RiskTolerance | str) -> RiskTolerance:
    """Normalize a risk tolerance value to the enum.

    Accepts enum members, enum values, and case-insensitive strings.

    Raises:
        ValueError: If the value cannot be mapped to a known risk tolerance.
    """
    if isinstance(value, RiskTolerance):
        return value
    parsed = RiskTolerance._missing_(value) if isinstance(value, str) else None
    if parsed is None:
        allowed = ", ".join(rt.value for rt in RiskTolerance)
        raise ValueError(f"Invalid risk tolerance {value!r}. Expected one of: {allowed}.")
    return parsed


def _allocations_for_risk(risk: RiskTolerance) -> list[dict[str, Any]]:
    """Return the base allocation table for a risk level."""
    if risk is RiskTolerance.CONSERVATIVE:
        return CONSERVATIVE_ALLOCATION
    if risk is RiskTolerance.MODERATE:
        return MODERATE_ALLOCATION
    return AGGRESSIVE_ALLOCATION


def _is_short_timeline(timeline: str) -> bool:
    """Identify timelines that should force a conservative, liquid allocation."""
    normalized = timeline.lower().strip()
    short_indicators = {"short", "1-2 years", "1 year", "2 years", "<1 year"}
    return normalized in short_indicators or normalized.startswith("short")

"""Tax calculation domain logic for Kenya PAYE.

This module provides pure functions for calculating Kenyan taxes including PAYE,
SHIF, NSSF, and Housing Levy.  It contains no I/O and no framework code.

Rate sources and effective dates
--------------------------------
PAYE brackets   : KRA PAYE guidelines, FY 2024/25
Personal relief  : KES 2,400/month (KES 28,800/year) — Finance Act 2023
SHIF             : 2.75 % of gross, min KES 300, max KES 1,700 — SHIF Act 2023
NSSF             : 6 % of pensionable earnings, capped at KES 2,160/month
                   (pensionable earnings ceiling: KES 36,000/month) — NSSF Act 2013
Housing Levy     : 1.5 % of gross — Finance Act 2023
"""

from kenya_wealth_agent.config.constants import (
    HOUSING_LEVY_RATE,
    NSSF_MAX,
    NSSF_RATE,
    PERSONAL_RELIEF,
    SHIF_MAX,
    SHIF_MIN,
    SHIF_RATE,
    TAX_BRACKETS,
)
from kenya_wealth_agent.domain.models import PayeCalculation
from kenya_wealth_agent.domain.validators import require_non_negative


def calculate_tax(gross_salary: float) -> PayeCalculation:
    """Calculate PAYE and statutory deductions for a given gross salary.

    Applies Kenya's progressive PAYE brackets to the full gross salary, then
    subtracts the personal relief credit.  All other statutory deductions (SHIF,
    NSSF, Housing Levy) are calculated separately and do not reduce PAYE
    taxable income.

    Args:
        gross_salary: Monthly gross salary in KES (must be >= 0).

    Returns:
        A ``PayeCalculation`` with all values rounded to 2 decimal places.

    Raises:
        ValueError: If ``gross_salary`` is negative or not numeric.
    """
    gross_salary = require_non_negative(gross_salary, "gross_salary")

    # ── Step 1: gross PAYE via progressive half-open brackets ─────────────────
    # Brackets are stored as [min, max).  The loop stops once income falls below
    # a bracket's minimum.
    gross_tax = 0.0
    for bracket in TAX_BRACKETS:
        lower = float(bracket["min"])
        upper = float(bracket["max"])  # float("inf") for the top band
        if gross_salary < lower:
            break
        taxable_in_bracket = min(gross_salary, upper) - lower
        gross_tax += taxable_in_bracket * bracket["rate"]

    # ── Step 2: apply personal relief (tax credit) ────────────────────────────
    paye = max(0.0, gross_tax - PERSONAL_RELIEF)

    # ── SHIF (Social Health Insurance Fund, formerly NHIF) ────────────────────
    nhif = min(max(gross_salary * SHIF_RATE, SHIF_MIN), SHIF_MAX)

    # ── NSSF ──────────────────────────────────────────────────────────────────
    nssf = min(gross_salary * NSSF_RATE, NSSF_MAX)

    # ── Affordable Housing Levy ───────────────────────────────────────────────
    housing_levy = gross_salary * HOUSING_LEVY_RATE

    total_deductions = paye + nhif + nssf + housing_levy
    net_salary = gross_salary - total_deductions

    return PayeCalculation(
        gross_salary=gross_salary,
        paye=round(paye, 2),
        nhif_shif=round(nhif, 2),
        nssf=round(nssf, 2),
        housing_levy=round(housing_levy, 2),
        total_deductions=round(total_deductions, 2),
        net_salary=round(net_salary, 2),
    )

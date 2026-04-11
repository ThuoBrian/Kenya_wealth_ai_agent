"""
Tax calculation service for Kenya PAYE.

This module provides functions for calculating Kenyan taxes
including PAYE, SHIF, NSSF, and Housing Levy.

Rate sources and effective dates
---------------------------------
PAYE brackets   : KRA PAYE guidelines, FY 2024/25
Personal relief  : KES 2,400/month (KES 28,800/year) — Finance Act 2023
SHIF             : 2.75 % of gross, min KES 300, max KES 1,700 — SHIF Act 2023
NSSF             : 6 % of pensionable earnings, capped at KES 2,160/month
                   (pensionable earnings ceiling: KES 36,000/month) — NSSF Act 2013
Housing Levy     : 1.5 % of gross — Finance Act 2023
"""

from typing import Dict, Any

from config.constants import TAX_BRACKETS

# Personal relief is a monthly tax *credit* (not an income deduction).
# It equals the 10 % tax on the first KES 24,000, so any employee whose
# gross PAYE would otherwise be ≤ KES 2,400 effectively pays zero tax.
_PERSONAL_RELIEF: float = 2_400.0


def calculate_tax(gross_salary: float) -> Dict[str, Any]:
    """Calculate PAYE and statutory deductions for a given gross salary.

    Applies Kenya's progressive PAYE brackets to the full gross salary,
    then subtracts the personal relief credit.  All other statutory
    deductions (SHIF, NSSF, Housing Levy) are calculated separately and
    do not reduce PAYE taxable income.

    Args:
        gross_salary: Monthly gross salary in KES (must be >= 0).

    Returns:
        Dictionary with keys:
            gross_salary, paye, nhif_shif, nssf, housing_levy,
            total_deductions, net_salary  — all values in KES, rounded to
            2 decimal places.
    """
    # ── Step 1: gross PAYE via progressive brackets ───────────────────────────
    # Apply each bracket to the portion of income that falls within it.
    gross_tax = 0.0
    for bracket in TAX_BRACKETS:
        lower = float(bracket["min"])
        upper = float(bracket["max"])   # float("inf") for the top band
        if gross_salary <= lower:
            break
        taxable_in_bracket = min(gross_salary, upper) - lower
        gross_tax += taxable_in_bracket * bracket["rate"]

    # ── Step 2: apply personal relief (tax credit) ────────────────────────────
    paye = max(0.0, gross_tax - _PERSONAL_RELIEF)

    # ── SHIF (Social Health Insurance Fund, formerly NHIF) ────────────────────
    # Rate: 2.75 % of gross; floor KES 300, ceiling KES 1,700.
    nhif = min(max(gross_salary * 0.0275, 300.0), 1_700.0)

    # ── NSSF ──────────────────────────────────────────────────────────────────
    # Employee contribution: 6 % of pensionable earnings (gross), capped at
    # KES 2,160/month (= 6 % × KES 36,000 pensionable earnings ceiling).
    nssf = min(gross_salary * 0.06, 2_160.0)

    # ── Affordable Housing Levy ───────────────────────────────────────────────
    housing_levy = gross_salary * 0.015

    total_deductions = paye + nhif + nssf + housing_levy
    net_salary = gross_salary - total_deductions

    return {
        "gross_salary": gross_salary,
        "paye": round(paye, 2),
        "nhif_shif": round(nhif, 2),
        "nssf": round(nssf, 2),
        "housing_levy": round(housing_levy, 2),
        "total_deductions": round(total_deductions, 2),
        "net_salary": round(net_salary, 2),
    }
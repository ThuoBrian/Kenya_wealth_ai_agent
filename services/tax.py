"""
Tax calculation service for Kenya PAYE.

This module provides functions for calculating Kenyan taxes
including PAYE, SHIF, NSSF, and Housing Levy.
"""

from typing import Dict, Any

from config.constants import TAX_BRACKETS


def calculate_tax(gross_salary: float) -> Dict[str, Any]:
    """Calculate PAYE tax for a given gross salary.

    Calculates all mandatory deductions including:
    - PAYE (Pay As You Earn)
    - SHIF (Social Health Insurance Fund) - formerly NHIF
    - NSSF (National Social Security Fund)
    - Housing Levy

    Args:
        gross_salary: Monthly gross salary in KES

    Returns:
        Dictionary containing:
            - gross_salary: Original gross salary
            - paye: Calculated PAYE tax
            - nhif_shif: SHIF deduction
            - nssf: NSSF deduction
            - housing_levy: Housing levy
            - total_deductions: Sum of all deductions
            - net_salary: Gross minus all deductions
    """
    taxable_income = gross_salary - 24000  # Personal relief
    if taxable_income < 0:
        taxable_income = 0

    tax = 0
    remaining = taxable_income

    for bracket in TAX_BRACKETS[1:]:  # Skip first bracket (10% on first 24k)
        if remaining <= 0:
            break
        bracket_min = bracket["min"] - 24000  # Adjust for relief
        bracket_size = bracket["max"] - bracket["min"]
        taxable_in_bracket = min(remaining, bracket_size)
        tax += taxable_in_bracket * bracket["rate"]
        remaining -= taxable_in_bracket

    # Add 10% on first 24k after relief
    first_bracket_tax = min(gross_salary, 24000) * 0.10
    tax += first_bracket_tax

    # NHIF (now SHIF) - simplified
    nhif = min(max(gross_salary * 0.0275, 300), 1700)  # 2.75% of gross

    # NSSF
    nssf = min(gross_salary * 0.06, 2160)  # 6% up to 18,000 pensionable earnings

    # Housing levy (1.5%)
    housing_levy = gross_salary * 0.015

    net_salary = gross_salary - tax - nhif - nssf - housing_levy

    return {
        "gross_salary": gross_salary,
        "paye": round(tax, 2),
        "nhif_shif": round(nhif, 2),
        "nssf": round(nssf, 2),
        "housing_levy": round(housing_levy, 2),
        "total_deductions": round(tax + nhif + nssf + housing_levy, 2),
        "net_salary": round(net_salary, 2),
    }
"""
Configuration constants for Kenya Wealth Agent.

This module contains Kenya-specific financial benchmarks, investment options,
and tax brackets used throughout the application.
"""

from typing import Dict, List, Any


# Kenya-specific financial benchmarks
KENYA_CONTEXT: Dict[str, float] = {
    "inflation_rate": 0.065,  # Approximate annual inflation ~6.5%
    "cbk_rate": 0.10,  # Central Bank Rate ~10%
    "mpesa_transaction_cost": 0.01,  # ~1% average transaction cost
    "sacco_interest_rate": 0.08,  # Average SACCO dividend ~8%
    "money_market_fund_rate": 0.09,  # ~9% average return
    "treasury_bond_rate": 0.14,  # ~14% for government bonds
    "nse_average_return": 0.12,  # Historical NSE average ~12%
    "emergency_fund_months": 6,  # Recommended emergency fund in months
    "savings_rate_target": 0.20,  # Recommended 20% savings rate
}

# Investment options in Kenya categorized by risk level
INVESTMENT_OPTIONS: Dict[str, List[Dict[str, Any]]] = {
    "low_risk": [
        {
            "name": "Money Market Funds (MMF)",
            "min_investment": 1000,
            "expected_return": "8-10%",
            "liquidity": "High",
        },
        {
            "name": "Treasury Bills",
            "min_investment": 50000,
            "expected_return": "10-12%",
            "liquidity": "Medium",
        },
        {
            "name": "Fixed Deposit Accounts",
            "min_investment": 10000,
            "expected_return": "6-8%",
            "liquidity": "Low",
        },
        {
            "name": "M-Akiba (Government Bond)",
            "min_investment": 3000,
            "expected_return": "10-15%",
            "liquidity": "Medium",
        },
    ],
    "medium_risk": [
        {
            "name": "SACCO Shares",
            "min_investment": 5000,
            "expected_return": "8-15%",
            "liquidity": "Low",
        },
        {
            "name": "Unit Trusts",
            "min_investment": 1000,
            "expected_return": "10-15%",
            "liquidity": "Medium",
        },
        {
            "name": "Corporate Bonds",
            "min_investment": 100000,
            "expected_return": "12-18%",
            "liquidity": "Low",
        },
    ],
    "high_risk": [
        {
            "name": "NSE Equities",
            "min_investment": 1000,
            "expected_return": "Variable (-20% to +30%)",
            "liquidity": "High",
        },
        {
            "name": "Real Estate Investment",
            "min_investment": 50000,
            "expected_return": "15-25%",
            "liquidity": "Low",
        },
        {
            "name": "Start-up Investment",
            "min_investment": 50000,
            "expected_return": "Variable",
            "liquidity": "Very Low",
        },
    ],
}

# Kenya PAYE tax brackets — monthly income thresholds in KES.
# Source : KRA PAYE guidelines, effective FY 2024/25.
# Review : verify against KRA website before each new financial year.
#
# How they are used:
#   gross_tax = sum of (income in bracket × rate) for all brackets
#   paye      = max(0, gross_tax − personal_relief)
#   personal_relief = KES 2,400/month (Finance Act 2023)
TAX_BRACKETS: List[Dict[str, Any]] = [
    {"min": 0,      "max": 24_000,        "rate": 0.10},
    {"min": 24_001, "max": 32_333,        "rate": 0.25},
    {"min": 32_334, "max": 500_000,       "rate": 0.30},
    {"min": 500_001,"max": 800_000,       "rate": 0.325},
    {"min": 800_001,"max": float("inf"),  "rate": 0.35},
]
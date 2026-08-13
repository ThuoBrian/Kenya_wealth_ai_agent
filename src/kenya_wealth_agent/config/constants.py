"""Configuration constants for Kenya Wealth Agent.

This module contains Kenya-specific financial benchmarks, investment options,
and tax brackets used throughout the application.

Tax brackets are stored as **half-open ranges** ``[min, max)`` where ``min`` is
inclusive and ``max`` is exclusive.  This representation matches how progressive
PAYE is actually applied: the first KES 24,000 is taxed at 10%, the next KES
8,333 (amounts 24,001 through 32,333) at 25%, and so on.

The KRA-published labels such as "24,001 - 32,333" are the integer amounts that
fall inside the half-open range ``[24_000, 32_333)``.
"""

from typing import Any

# Kenya-specific financial benchmarks
KENYA_CONTEXT: dict[str, float] = {
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
INVESTMENT_OPTIONS: dict[str, list[dict[str, Any]]] = {
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
# Source: KRA PAYE guidelines, effective FY 2024/25.
# Review: verify against KRA website before each new financial year.
#
# Brackets are stored as half-open ranges [min, max).  This avoids the
# off-by-one errors that occur when treating brackets as fully inclusive.
#
# How they are used:
#   gross_tax = sum of (income in bracket * rate) for all brackets
#   paye      = max(0, gross_tax - personal_relief)
#   personal_relief = KES 2,400/month (Finance Act 2023)
TAX_BRACKETS: list[dict[str, Any]] = [
    {"min": 0, "max": 24_000, "rate": 0.10},
    {"min": 24_000, "max": 32_333, "rate": 0.25},
    {"min": 32_333, "max": 500_000, "rate": 0.30},
    {"min": 500_000, "max": 800_000, "rate": 0.325},
    {"min": 800_000, "max": float("inf"), "rate": 0.35},
]

# Statutory deduction rates and caps — Finance Act 2023 / NSSF Act 2013.
# Values are monthly unless otherwise noted.
SHIF_RATE: float = 0.0275  # 2.75% of gross
SHIF_MIN: float = 300.0  # KES 300/month floor
SHIF_MAX: float = 1_700.0  # KES 1,700/month ceiling
NSSF_RATE: float = 0.06  # 6% employee contribution
NSSF_PENSIONABLE_CEILING: float = 36_000.0  # pensionable earnings cap
NSSF_MAX: float = NSSF_RATE * NSSF_PENSIONABLE_CEILING  # KES 2,160
HOUSING_LEVY_RATE: float = 0.015  # 1.5% of gross
PERSONAL_RELIEF: float = 2_400.0  # monthly tax credit

# Investment allocation presets by risk tolerance and timeline.
# These are intentionally conservative educational defaults, not personalized advice.
CONSERVATIVE_ALLOCATION: list[dict[str, Any]] = [
    {"option": "Money Market Fund", "allocation": 0.40, "expected_return": "8-10%"},
    {"option": "M-Akiba/Treasury Bonds", "allocation": 0.35, "expected_return": "10-14%"},
    {"option": "SACCO Shares", "allocation": 0.25, "expected_return": "8-15%"},
]

MODERATE_ALLOCATION: list[dict[str, Any]] = [
    {"option": "Money Market Fund", "allocation": 0.25, "expected_return": "8-10%"},
    {"option": "NSE Equities (ETF/Direct)", "allocation": 0.35, "expected_return": "10-20%"},
    {"option": "SACCO Shares", "allocation": 0.20, "expected_return": "8-15%"},
    {"option": "Unit Trusts", "allocation": 0.20, "expected_return": "10-15%"},
]

AGGRESSIVE_ALLOCATION: list[dict[str, Any]] = [
    {"option": "NSE Equities", "allocation": 0.50, "expected_return": "Variable"},
    {"option": "Real Estate/Land", "allocation": 0.30, "expected_return": "15-25%"},
    {"option": "Unit Trusts", "allocation": 0.20, "expected_return": "10-15%"},
]

SHORT_TIMELINE_ALLOCATION: list[dict[str, Any]] = [
    {"option": "Money Market Fund", "allocation": 0.60, "expected_return": "8-10%"},
    {"option": "SACCO Shares", "allocation": 0.40, "expected_return": "8-15%"},
]

# Budget rule targets (as fractions of income)
RENT_TARGET: float = 0.30
TRANSPORT_TARGET: float = 0.15
AIRTIME_DATA_TARGET: float = 0.05
MIN_SAVINGS_RATE_TARGET: float = 0.10

# Available Ollama model aliases.
# Users can set the short alias in config.ini / env vars; it is resolved to the
# full model tag on startup.
AVAILABLE_MODELS: dict[str, str] = {
    "nemotron": "nemotron-3-super:cloud",
    "llama3": "llama3.1:latest",
    "llama3.1": "llama3.1:latest",
    "mistral": "mistral:latest",
    "qwen": "qwen2.5:latest",
    "qwen2.5": "qwen2.5:latest",
    "glm": "glm-5:cloud",
    "glm-5": "glm-5:cloud",
}

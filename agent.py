#!/usr/bin/env python3
"""
Kenya Wealth & Finance Agent
A personalized financial advisor for the Kenyan market context.

This module contains the core agent class that interfaces with
the Ollama LLM to provide financial advice.
"""

import os
from datetime import datetime
from typing import Optional, List, Dict

try:
    import ollama
except ImportError:
    raise ImportError(
        "The 'ollama' package is not installed.\n"
        "Run:  pip install -r requirements.txt"
    )

from config.constants import KENYA_CONTEXT, INVESTMENT_OPTIONS, TAX_BRACKETS
from models.user import FinancialGoal, RiskTolerance, UserProfile
from services.budget import analyze_budget
from services.tax import calculate_tax
from services.investment import get_investment_recommendations
from services.emergency import calculate_emergency_fund_target
from prompts.system import get_system_prompt


class KenyaWealthAgent:
    """
    AI-powered financial advisor specialized for the Kenyan market.

    Provides advice on budgeting, saving, investing, and wealth building
    through natural language conversation with an LLM backend.

    Attributes:
        model: The Ollama model name to use
        base_url: The Ollama server URL
        client: The Ollama client instance
        conversation_history: List of conversation messages
    """

    def __init__(
        self, model: str = "nemotron-3-super:cloud", base_url: Optional[str] = None
    ):
        """Initialize the agent with Ollama API.

        Args:
            model: Ollama model to use (default: nemotron-3-super:cloud)
            base_url: Optional Ollama server URL (default: http://localhost:11434)
        """
        self.model = model
        self.base_url = base_url or os.environ.get(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )
        self.client = ollama.Client(host=self.base_url)
        self.conversation_history: List[Dict[str, str]] = []

    def chat(self, user_message: str) -> str:
        """Have a conversation with the agent.

        Sends the user message to the LLM and returns the response.
        The conversation history is stored for later report generation.

        Args:
            user_message: The user's message to send

        Returns:
            The assistant's response as a string
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat(),
        })

        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": get_system_prompt()},
                *self.conversation_history,
            ],
        )

        assistant_message = response["message"]["content"]
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message,
            "timestamp": datetime.now().isoformat(),
        })

        return assistant_message

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history.

        Returns:
            List of message dictionaries with 'role' and 'content' keys
        """
        return self.conversation_history.copy()

    def analyze_budget(
        self, income: float, expenses: Dict[str, float]
    ) -> Dict[str, float]:
        """Analyze a user's budget and provide recommendations.

        Args:
            income: Monthly income in KES
            expenses: Dictionary of expense categories and amounts

        Returns:
            Budget analysis with recommendations
        """
        return analyze_budget(income, expenses)

    def get_investment_recommendations(
        self, amount: float, risk_tolerance: str, timeline: str
    ) -> Dict[str, str]:
        """Get investment recommendations based on profile.

        Args:
            amount: Investment amount in KES
            risk_tolerance: Risk tolerance level
            timeline: Investment timeline

        Returns:
            Investment recommendations
        """
        return get_investment_recommendations(amount, risk_tolerance, timeline)

    def calculate_emergency_fund_target(
        self, monthly_expenses: float, months: int = 6
    ) -> Dict[str, float]:
        """Calculate emergency fund target and timeline.

        Args:
            monthly_expenses: Monthly expenses in KES
            months: Number of months to cover

        Returns:
            Emergency fund calculation results
        """
        return calculate_emergency_fund_target(monthly_expenses, months)

    def calculate_tax(self, gross_salary: float) -> Dict[str, float]:
        """Calculate PAYE tax for a given gross salary.

        Args:
            gross_salary: Monthly gross salary in KES

        Returns:
            Tax calculation results
        """
        return calculate_tax(gross_salary)

    def reset_conversation(self) -> None:
        """Reset the conversation history."""
        self.conversation_history = []

    # Expose constants for external use
    KENYA_CONTEXT = KENYA_CONTEXT
    INVESTMENT_OPTIONS = INVESTMENT_OPTIONS
    TAX_BRACKETS = TAX_BRACKETS
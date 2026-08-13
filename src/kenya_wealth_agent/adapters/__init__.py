"""Adapters for Kenya Wealth Agent.

Concrete implementations of the ports defined in the application layer.
"""

from kenya_wealth_agent.adapters.llm.fake_client import FakeLLMClient
from kenya_wealth_agent.adapters.llm.ollama_client import OllamaLLMClient
from kenya_wealth_agent.adapters.persistence.memory_session_repo import (
    InMemorySessionRepository,
)
from kenya_wealth_agent.adapters.prompts.system_prompt import KenyaSystemPromptBuilder
from kenya_wealth_agent.adapters.rendering.html_report import HTMLReportRenderer

__all__ = [
    "FakeLLMClient",
    "HTMLReportRenderer",
    "InMemorySessionRepository",
    "KenyaSystemPromptBuilder",
    "OllamaLLMClient",
]

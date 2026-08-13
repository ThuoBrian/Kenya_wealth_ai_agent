"""FastAPI dependencies for the Kenya Wealth Agent web interface.

Dependencies build or reuse the application's adapters and services.  They are
intentionally thin: all construction logic lives here so routers stay focused
on HTTP mapping.
"""

from functools import lru_cache
from typing import NamedTuple
from uuid import uuid4

from fastapi import Cookie, Request

from kenya_wealth_agent.adapters.llm.ollama_client import OllamaLLMClient
from kenya_wealth_agent.adapters.persistence.memory_session_repo import (
    InMemorySessionRepository,
)
from kenya_wealth_agent.adapters.prompts.system_prompt import KenyaSystemPromptBuilder
from kenya_wealth_agent.adapters.rendering.html_report import HTMLReportRenderer
from kenya_wealth_agent.application.agent_service import AgentService
from kenya_wealth_agent.application.financial_services import (
    BudgetService,
    EmergencyService,
    InvestmentService,
    ReportService,
    RetirementService,
    SavingsService,
    TaxService,
)
from kenya_wealth_agent.config.settings import Settings, get_settings


class AppComponents(NamedTuple):
    """Container for the singleton-like application components used by routers."""

    settings: Settings
    agent_service: AgentService
    report_service: ReportService
    tax_service: TaxService
    budget_service: BudgetService
    investment_service: InvestmentService
    emergency_service: EmergencyService
    retirement_service: RetirementService
    savings_service: SavingsService


@lru_cache(maxsize=1)
def _session_repository() -> InMemorySessionRepository:
    """Return the shared in-memory session repository.

    A single repository instance is required so that every HTTP request sees
    the same session state while the process is running.
    """
    return InMemorySessionRepository()


@lru_cache(maxsize=1)
def get_components() -> AppComponents:
    """Build and cache the application's web-layer components."""
    settings = get_settings()
    llm_client = OllamaLLMClient(base_url=settings.base_url)
    prompt_builder = KenyaSystemPromptBuilder()
    repository = _session_repository()
    agent_service = AgentService(
        llm_client=llm_client,
        prompt_builder=prompt_builder,
        repository=repository,
        model=settings.model,
        max_message_length=settings.max_message_length,
    )
    renderer = HTMLReportRenderer()
    report_service = ReportService(
        renderer=renderer,
        output_dir=settings.output_dir,
        filename=settings.report_filename,
    )
    return AppComponents(
        settings=settings,
        agent_service=agent_service,
        report_service=report_service,
        tax_service=TaxService(),
        budget_service=BudgetService(),
        investment_service=InvestmentService(),
        emergency_service=EmergencyService(),
        retirement_service=RetirementService(),
        savings_service=SavingsService(),
    )


def get_settings_dependency() -> Settings:
    """FastAPI dependency that returns the resolved application settings."""
    return get_components().settings


def get_agent_service() -> AgentService:
    """FastAPI dependency that returns the shared agent service."""
    return get_components().agent_service


def get_report_service() -> ReportService:
    """FastAPI dependency that returns the shared report service."""
    return get_components().report_service


def get_financial_services() -> AppComponents:
    """Return all cached financial service instances."""
    return get_components()


def get_session_id(
    request: Request,
    kwa_session_id: str | None = Cookie(default=None),
) -> str:
    """Resolve a stable session id for the current client.

    If the client already sent a ``kwa_session_id`` cookie we reuse it so the
    conversation history persists across requests.  Otherwise a new UUID is
    generated and the caller is responsible for setting it as a cookie on the
    response.
    """
    return kwa_session_id or str(uuid4())

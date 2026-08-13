"""CLI command implementations for Kenya Wealth Agent.

Each command builds the same application components as the web interface so
that behaviour is consistent across interfaces.
"""

import asyncio
import json
from typing import Any

import structlog
import uvicorn

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
from kenya_wealth_agent.domain import FinancialGoal, RiskTolerance
from kenya_wealth_agent.infrastructure.logging import configure_logging


class CliContext:
    """Holds the application components for a CLI invocation."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.repository = InMemorySessionRepository()
        self.llm_client = OllamaLLMClient(base_url=self.settings.base_url)
        self.prompt_builder = KenyaSystemPromptBuilder()
        self.agent_service = AgentService(
            llm_client=self.llm_client,
            prompt_builder=self.prompt_builder,
            repository=self.repository,
            model=self.settings.model,
            max_message_length=self.settings.max_message_length,
        )
        self.renderer = HTMLReportRenderer()
        self.report_service = ReportService(
            renderer=self.renderer,
            output_dir=self.settings.output_dir,
            filename=self.settings.report_filename,
        )
        self.tax_service = TaxService()
        self.budget_service = BudgetService()
        self.investment_service = InvestmentService()
        self.emergency_service = EmergencyService()
        self.retirement_service = RetirementService()
        self.savings_service = SavingsService()


def _init_logging(settings: Settings) -> None:
    """Configure logging for CLI use (plain text, colours when available)."""
    configure_logging(
        log_level=settings.log_level,
        structured=False,
    )


def run_web(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
) -> None:
    """Start the FastAPI web server."""
    settings = get_settings()
    _init_logging(settings)
    logger = structlog.get_logger()
    logger.info(
        "starting_web_server",
        host=host,
        port=port,
        model=settings.model,
    )
    uvicorn.run(
        app="kenya_wealth_agent.interfaces.web.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level=settings.log_level.lower(),
    )


async def _chat_session(agent_service: AgentService, session_id: str) -> None:
    """Run an interactive chat loop in the terminal."""
    print("\n🇰🇪 Kenya Wealth Agent — interactive chat")
    print("Type your question, or 'exit' / 'quit' to leave.\n")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "q"}:
            print("Goodbye!")
            break
        try:
            response = await agent_service.chat(
                session_id=session_id,
                user_message=user_input,
            )
            print(f"\nAdvisor:\n{response}\n")
        except ValueError as exc:
            print(f"Input error: {exc}")
        except RuntimeError as exc:
            print(f"LLM error: {exc}")


def run_chat() -> None:
    """Run the interactive CLI chat."""
    settings = get_settings()
    _init_logging(settings)
    context = CliContext(settings)
    session_id = "cli-session"
    asyncio.run(_chat_session(context.agent_service, session_id))


def run_tax(gross_salary: float) -> None:
    """Calculate and print PAYE for a gross salary."""
    settings = get_settings()
    _init_logging(settings)
    context = CliContext(settings)
    result = asyncio.run(context.tax_service.calculate(gross_salary=gross_salary))
    _print_json(result.model_dump())


def run_budget(income: float, expenses: str) -> None:
    """Analyze a budget from a JSON expenses map."""
    parsed_expenses: dict[str, float] = json.loads(expenses)
    if not isinstance(parsed_expenses, dict):
        raise ValueError("expenses must be a JSON object mapping name to amount")
    settings = get_settings()
    _init_logging(settings)
    context = CliContext(settings)
    result = asyncio.run(
        context.budget_service.analyze(
            income=income,
            expenses=parsed_expenses,
        )
    )
    _print_json(result.model_dump())


def run_invest(amount: float, risk_tolerance: str, timeline: str) -> None:
    """Print an investment recommendation."""
    risk = RiskTolerance(risk_tolerance)
    settings = get_settings()
    _init_logging(settings)
    context = CliContext(settings)
    result = asyncio.run(
        context.investment_service.recommend(
            amount=amount,
            risk_tolerance=risk,
            timeline=timeline,
        )
    )
    _print_json(result.model_dump())


def run_emergency(monthly_expenses: float, months: int = 6) -> None:
    """Print an emergency fund target."""
    settings = get_settings()
    _init_logging(settings)
    context = CliContext(settings)
    result = asyncio.run(
        context.emergency_service.calculate_target(
            monthly_expenses=monthly_expenses,
            months=months,
        )
    )
    _print_json(result.model_dump())


def run_retirement(
    current_age: int,
    retirement_age: int,
    monthly_contribution: float,
    annual_return_rate: float = 0.09,
) -> None:
    """Print a retirement projection."""
    settings = get_settings()
    _init_logging(settings)
    context = CliContext(settings)
    result = asyncio.run(
        context.retirement_service.project(
            current_age=current_age,
            retirement_age=retirement_age,
            monthly_contribution=monthly_contribution,
            annual_return_rate=annual_return_rate,
        )
    )
    _print_json(result.model_dump())


def run_savings(goal: str, target_amount: float, timeline_months: int) -> None:
    """Print a savings strategy recommendation."""
    parsed_goal = FinancialGoal(goal)
    settings = get_settings()
    _init_logging(settings)
    context = CliContext(settings)
    result = asyncio.run(
        context.savings_service.recommend(
            goal=parsed_goal,
            target_amount=target_amount,
            timeline_months=timeline_months,
        )
    )
    _print_json(result.model_dump())


def _print_json(data: dict[str, Any]) -> None:
    """Pretty-print a dictionary as JSON."""
    print(json.dumps(data, indent=2, default=str))


def run_export(session_id: str = "cli-session") -> None:
    """Export the current CLI session as an HTML report."""
    settings = get_settings()
    _init_logging(settings)
    context = CliContext(settings)
    messages = asyncio.run(context.agent_service.get_history(session_id))
    path = asyncio.run(context.report_service.export(messages))
    print(f"Report saved to: {path}")


__all__ = [
    "CliContext",
    "run_budget",
    "run_chat",
    "run_emergency",
    "run_export",
    "run_invest",
    "run_retirement",
    "run_savings",
    "run_tax",
    "run_web",
]

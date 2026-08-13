"""Tests for the Kenya Wealth Agent CLI."""

from unittest.mock import MagicMock

import pytest

from kenya_wealth_agent.adapters.llm.fake_client import FakeLLMClient
from kenya_wealth_agent.interfaces.cli.app import main


class StubLLMClient(FakeLLMClient):
    """Fake LLM client that accepts the ``base_url`` argument CliContext passes."""

    def __init__(self, response: str = "Stub response", base_url: str = ""):
        super().__init__(response)
        self.base_url = base_url


@pytest.fixture(autouse=True)
def patch_llm_client(monkeypatch):
    """Prevent CLI commands from trying to reach a real Ollama server."""
    monkeypatch.setattr(
        "kenya_wealth_agent.interfaces.cli.commands.OllamaLLMClient",
        StubLLMClient,
    )


def test_web_command(monkeypatch):
    mock_run = MagicMock()
    monkeypatch.setattr("kenya_wealth_agent.interfaces.cli.commands.uvicorn.run", mock_run)
    assert main(["web", "--host", "0.0.0.0", "--port", "9000"]) == 0
    mock_run.assert_called_once()
    call_kwargs = mock_run.call_args.kwargs
    assert call_kwargs["host"] == "0.0.0.0"
    assert call_kwargs["port"] == 9000
    assert call_kwargs["app"] == "kenya_wealth_agent.interfaces.web.app:app"


def test_tax_command(capsys):
    assert main(["tax", "--gross-salary", "100000"]) == 0
    captured = capsys.readouterr()
    assert "gross_salary" in captured.out


def test_budget_command(capsys):
    assert main(["budget", "--income", "200000", "--expenses", '{"rent": 50000}']) == 0
    captured = capsys.readouterr()
    assert "total_income" in captured.out


def test_invest_command(capsys):
    assert (
        main(["invest", "--amount", "100000", "--risk", "moderate", "--timeline", "5 years"]) == 0
    )
    captured = capsys.readouterr()
    assert "amount" in captured.out


def test_emergency_command(capsys):
    assert main(["emergency", "--monthly-expenses", "80000"]) == 0
    captured = capsys.readouterr()
    assert "target_amount" in captured.out


def test_retirement_command(capsys):
    assert (
        main(
            [
                "retirement",
                "--current-age",
                "30",
                "--retirement-age",
                "60",
                "--monthly-contribution",
                "10000",
            ]
        )
        == 0
    )
    captured = capsys.readouterr()
    assert "years_to_retirement" in captured.out


def test_savings_command(capsys):
    assert (
        main(
            [
                "savings",
                "--goal",
                "emergency_fund",
                "--target-amount",
                "120000",
                "--timeline-months",
                "12",
            ]
        )
        == 0
    )
    captured = capsys.readouterr()
    assert "monthly_savings_required" in captured.out


def test_chat_command(capsys, monkeypatch):
    inputs = iter(["Hello", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    assert main(["chat"]) == 0
    captured = capsys.readouterr()
    assert "Kenya Wealth Agent" in captured.out
    assert "Stub response" in captured.out


def test_export_command(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(
        "kenya_wealth_agent.interfaces.cli.commands.get_settings",
        lambda: MagicMock(
            base_url="",
            model="test",
            max_message_length=4_000,
            log_level="INFO",
            output_dir=str(tmp_path),
            report_filename="report.html",
            structured_logs=False,
        ),
    )
    assert main(["export"]) == 0
    captured = capsys.readouterr()
    assert "Report saved to:" in captured.out

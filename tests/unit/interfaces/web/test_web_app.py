"""Tests for the FastAPI web interface."""

import pytest
from fastapi.testclient import TestClient

from kenya_wealth_agent.adapters.llm.fake_client import FakeLLMClient
from kenya_wealth_agent.adapters.persistence.memory_session_repo import (
    InMemorySessionRepository,
)
from kenya_wealth_agent.adapters.prompts.system_prompt import KenyaSystemPromptBuilder
from kenya_wealth_agent.adapters.rendering.html_report import HTMLReportRenderer
from kenya_wealth_agent.application.agent_service import AgentService
from kenya_wealth_agent.application.financial_services import ReportService
from kenya_wealth_agent.config.settings import Settings, get_settings
from kenya_wealth_agent.interfaces.web.app import app
from kenya_wealth_agent.interfaces.web.dependencies import (
    get_agent_service,
    get_report_service,
    get_settings_dependency,
)


@pytest.fixture
def fake_settings():
    settings = get_settings()
    settings.model = "test-model"
    settings.enable_streaming = False
    return settings


@pytest.fixture
def fake_agent_service():
    return AgentService(
        llm_client=FakeLLMClient(response="Test response"),
        prompt_builder=KenyaSystemPromptBuilder(),
        repository=InMemorySessionRepository(),
        model="test-model",
    )


@pytest.fixture
def client(fake_agent_service: AgentService, fake_settings: Settings):
    app.dependency_overrides[get_agent_service] = lambda: fake_agent_service
    app.dependency_overrides[get_settings_dependency] = lambda: fake_settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_status_online(client: TestClient, fake_agent_service: AgentService):
    app.dependency_overrides[get_agent_service] = lambda: fake_agent_service
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is True
    assert data["model"] == "test-model"


def test_chat_json_response(client: TestClient):
    response = client.post("/api/chat?stream=false", json={"message": "Hello"})
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Test response"
    assert "timestamp" in data
    assert "kwa_session_id" in response.cookies


def test_chat_stream_response(client: TestClient, fake_settings: Settings):
    fake_settings.enable_streaming = True
    response = client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    body = response.text
    assert "Test" in body


def test_history_and_reset(client: TestClient):
    client.post("/api/chat?stream=false", json={"message": "Hello"})
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) == 2

    reset_response = client.post("/api/reset")
    assert reset_response.status_code == 200
    assert reset_response.json()["status"] == "ok"

    response = client.get("/api/history")
    assert response.json()["messages"] == []


def test_chat_empty_message_rejected(client: TestClient):
    response = client.post("/api/chat?stream=false", json={"message": "   "})
    assert response.status_code == 422


def test_tax_endpoint(client: TestClient):
    response = client.post("/api/tax", json={"gross_salary": 100_000})
    assert response.status_code == 200
    data = response.json()
    assert data["gross_salary"] == 100_000
    assert "paye" in data


def test_budget_endpoint(client: TestClient):
    response = client.post(
        "/api/budget",
        json={"income": 200_000, "expenses": {"rent": 50_000, "food": 20_000}},
    )
    assert response.status_code == 200
    assert response.json()["total_income"] == 200_000


def test_invest_endpoint(client: TestClient):
    response = client.post(
        "/api/invest",
        json={"amount": 100_000, "risk_tolerance": "moderate", "timeline": "5 years"},
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 100_000


def test_invest_invalid_risk_returns_422(client: TestClient):
    response = client.post(
        "/api/invest",
        json={"amount": 100_000, "risk_tolerance": "unknown", "timeline": "5 years"},
    )
    assert response.status_code == 422


def test_emergency_endpoint(client: TestClient):
    response = client.post("/api/emergency", json={"monthly_expenses": 80_000})
    assert response.status_code == 200
    assert response.json()["target_amount"] == 80_000 * 6


def test_retirement_endpoint(client: TestClient):
    response = client.post(
        "/api/retirement",
        json={
            "current_age": 30,
            "retirement_age": 60,
            "monthly_contribution": 10_000,
        },
    )
    assert response.status_code == 200
    assert response.json()["years_to_retirement"] == 30


def test_savings_endpoint(client: TestClient):
    response = client.post(
        "/api/savings",
        json={
            "goal": "emergency_fund",
            "target_amount": 120_000,
            "timeline_months": 12,
        },
    )
    assert response.status_code == 200
    assert response.json()["monthly_savings_required"] == 10_000


def test_static_index_served(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "Kenya Wealth Agent" in response.text


def test_export_report(client: TestClient, tmp_path, fake_agent_service: AgentService):
    app.dependency_overrides[get_agent_service] = lambda: fake_agent_service
    app.dependency_overrides[get_report_service] = lambda: ReportService(
        renderer=HTMLReportRenderer(),
        output_dir=tmp_path,
        filename="report.html",
    )
    client.post("/api/chat?stream=false", json={"message": "Hello"})
    response = client.get("/api/export")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "report.html" in data["path"]
    assert (tmp_path / "report.html").exists()

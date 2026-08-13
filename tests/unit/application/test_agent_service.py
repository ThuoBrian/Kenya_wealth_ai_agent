"""Unit tests for the AgentService orchestrator."""

from collections.abc import AsyncIterator

import pytest

from kenya_wealth_agent.application.agent_service import MAX_MESSAGE_LENGTH, AgentService
from kenya_wealth_agent.domain.models import UserProfile


class FakeLLMClient:
    """Test double that echoes the last user message."""

    def __init__(self, response: str = "Echo"):
        self.response = response
        self.last_messages: list[dict[str, str]] = []
        self.last_model: str | None = None

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> str:
        self.last_messages = messages
        self.last_model = model
        return self.response

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        self.last_messages = messages
        self.last_model = model
        words = self.response.split(" ")
        for word in words[:-1]:
            yield word + " "
        if words:
            yield words[-1]

    async def is_available(self) -> bool:
        return True


class FakePromptBuilder:
    def build(self, profile: UserProfile | None = None) -> str:
        if profile:
            return f"System prompt for {profile.name}"
        return "System prompt"


class FakeSessionRepository:
    def __init__(self):
        self._store: dict[str, list[dict[str, str]]] = {}

    async def get(self, session_id: str) -> list[dict[str, str]]:
        return list(self._store.get(session_id, []))

    async def save(
        self,
        session_id: str,
        messages: list[dict[str, str]],
    ) -> None:
        self._store[session_id] = messages

    async def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)


@pytest.fixture
def service():
    return AgentService(
        llm_client=FakeLLMClient(),
        prompt_builder=FakePromptBuilder(),
        repository=FakeSessionRepository(),
        model="test-model",
    )


async def test_chat_stores_history(service: AgentService):
    response = await service.chat("session-1", "Hello")
    assert response == "Echo"
    history = await service.get_history("session-1")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Echo"


async def test_chat_includes_system_prompt_and_profile(service: AgentService):
    profile = UserProfile(name="Brian", monthly_income=100_000)
    await service.chat("session-2", "Hi", profile=profile)
    assert service.llm_client.last_messages[0]["role"] == "system"
    assert "Brian" in service.llm_client.last_messages[0]["content"]


async def test_chat_uses_configured_model(service: AgentService):
    await service.chat("session-3", "Test")
    assert service.llm_client.last_model == "test-model"


async def test_empty_message_rejected(service: AgentService):
    with pytest.raises(ValueError, match="Message cannot be empty"):
        await service.chat("session-4", "   ")


async def test_long_message_rejected(service: AgentService):
    with pytest.raises(ValueError, match="exceeds"):
        await service.chat("session-5", "x" * (MAX_MESSAGE_LENGTH + 1))


async def test_reset_clears_history(service: AgentService):
    await service.chat("session-6", "Hello")
    await service.reset("session-6")
    assert await service.get_history("session-6") == []


async def test_chat_stream_returns_and_stores_response(service: AgentService):
    chunks = []
    async for chunk in service.chat_stream("session-7", "Hello"):
        chunks.append(chunk)
    assert "".join(chunks) == "Echo"
    history = await service.get_history("session-7")
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
    assert history[1]["content"] == "Echo"


async def test_chat_stream_validates_messages(service: AgentService):
    with pytest.raises(ValueError, match="Message cannot be empty"):
        async for _ in service.chat_stream("session-8", "   "):
            pass


async def test_chat_stream_uses_system_prompt(service: AgentService):
    profile = UserProfile(name="Brian", monthly_income=100_000)
    async for _ in service.chat_stream("session-9", "Hi", profile=profile):
        pass
    assert service.llm_client.last_messages[0]["role"] == "system"
    assert "Brian" in service.llm_client.last_messages[0]["content"]

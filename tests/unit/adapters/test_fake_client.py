"""Tests for the Fake LLM client adapter."""

import pytest

from kenya_wealth_agent.adapters.llm.fake_client import FakeLLMClient


@pytest.fixture
def client():
    return FakeLLMClient(response="This is a fake response.")


async def test_chat_returns_canned_response(client: FakeLLMClient):
    result = await client.chat([{"role": "user", "content": "Hi"}], model="test")
    assert result == "This is a fake response."
    assert len(client.calls) == 1


async def test_chat_stream_yields_response_in_chunks(client: FakeLLMClient):
    chunks = [chunk async for chunk in client.chat_stream([], model="test")]
    assert "".join(chunks) == "This is a fake response."
    assert len(client.calls) == 1


async def test_is_available_returns_true(client: FakeLLMClient):
    assert await client.is_available() is True

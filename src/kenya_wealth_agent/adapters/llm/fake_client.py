"""Fake LLM client for testing and offline demos."""

from collections.abc import AsyncIterator

from kenya_wealth_agent.application.ports import LLMClient


class FakeLLMClient(LLMClient):
    """Test-double LLM client that returns a canned or echo response.

    Useful for:
    - Unit tests that must not depend on a running Ollama server.
    - CI pipelines where no LLM is available.
    - Offline demos.
    """

    def __init__(self, response: str = "This is a fake LLM response."):
        """Initialize with a fixed response.

        Args:
            response: Text to return from every ``chat`` call.
        """
        self.response = response
        self.calls: list[list[dict[str, str]]] = []

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> str:
        """Record the messages and return the configured response."""
        self.calls.append(messages)
        return self.response

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        """Yield the configured response one word at a time."""
        self.calls.append(messages)
        words = self.response.split(" ")
        for word in words[:-1]:
            yield word + " "
        if words:
            yield words[-1]

    async def is_available(self) -> bool:
        """Always report healthy for the fake adapter."""
        return True

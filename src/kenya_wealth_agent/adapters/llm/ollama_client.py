"""Async Ollama LLM adapter."""

from collections.abc import AsyncIterator
from typing import cast

import ollama
import structlog

from kenya_wealth_agent.application.ports import LLMClient

logger = structlog.get_logger()


class OllamaLLMClient(LLMClient):
    """Adapter that speaks to a local Ollama server using the async client."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """Initialize the Ollama client.

        Args:
            base_url: URL of the Ollama server.
        """
        self.base_url = base_url
        self._client = ollama.AsyncClient(host=base_url)

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> str:
        """Send messages to Ollama and return the assistant response.

        Args:
            messages: OpenAI-compatible conversation messages.
            model: Model name.  Must be non-empty.

        Returns:
            Assistant response text.

        Raises:
            ValueError: If no model is provided.
            RuntimeError: If Ollama returns an error.
        """
        if not model:
            raise ValueError("model is required for OllamaLLMClient.chat")

        try:
            response = await self._client.chat(model=model, messages=messages)
        except Exception as exc:
            logger.error("ollama_chat_failed", model=model, error=str(exc))
            raise RuntimeError(f"Ollama request failed: {exc}") from exc

        return cast(str, response["message"]["content"])

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream the assistant response from Ollama chunk-by-chunk.

        Args:
            messages: OpenAI-compatible conversation messages.
            model: Model name.  Must be non-empty.

        Yields:
            Response text chunks as they arrive.

        Raises:
            ValueError: If no model is provided.
            RuntimeError: If Ollama returns an error.
        """
        if not model:
            raise ValueError("model is required for OllamaLLMClient.chat_stream")

        try:
            stream = await self._client.chat(model=model, messages=messages, stream=True)
            async for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
        except Exception as exc:
            logger.error("ollama_stream_failed", model=model, error=str(exc))
            raise RuntimeError(f"Ollama streaming request failed: {exc}") from exc

    async def is_available(self) -> bool:
        """Return ``True`` if the Ollama server responds to a model list call."""
        try:
            await self._client.list()
            return True
        except Exception as exc:
            logger.warning("ollama_unavailable", base_url=self.base_url, error=str(exc))
            return False

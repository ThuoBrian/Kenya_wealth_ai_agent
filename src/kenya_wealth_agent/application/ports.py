"""Application ports (abstract interfaces / protocols).

A port defines a capability the application layer needs from the outside world.
Concrete adapters live in ``kenya_wealth_agent.adapters`` and are wired into
ports at application startup.
"""

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Protocol, runtime_checkable

from kenya_wealth_agent.domain.models import UserProfile


@runtime_checkable
class LLMClient(Protocol):
    """Abstraction over any local or remote LLM provider."""

    async def chat(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> str:
        """Send a list of messages to the LLM and return the assistant response.

        Args:
            messages: Conversation history in OpenAI-compatible format.  Each
                dict must contain ``role`` and ``content`` keys.
            model: Optional model override.  If ``None``, the adapter should
                use its configured default.

        Returns:
            The assistant's response text.

        Raises:
            RuntimeError: If the LLM is unreachable or returns an error.
        """
        ...

    def chat_stream(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
    ) -> AsyncIterator[str]:
        """Stream the assistant response token-by-token.

        This method is declared without ``async`` in the protocol because an
        async generator implementation is compatible with an ``AsyncIterator``
        return type.

        Args:
            messages: Conversation history in OpenAI-compatible format.
            model: Optional model override.

        Yields:
            Response chunks as they arrive from the LLM.

        Raises:
            RuntimeError: If the LLM is unreachable or returns an error.
        """
        ...

    async def is_available(self) -> bool:
        """Return ``True`` if the LLM provider is reachable and healthy."""
        ...


@runtime_checkable
class SessionRepository(Protocol):
    """Storage for conversation history keyed by session ID."""

    async def get(self, session_id: str) -> list[dict[str, str]]:
        """Return the full message history for a session, oldest first."""
        ...

    async def save(
        self,
        session_id: str,
        messages: list[dict[str, str]],
    ) -> None:
        """Persist the full message history for a session."""
        ...

    async def clear(self, session_id: str) -> None:
        """Delete the stored history for a session."""
        ...


@runtime_checkable
class ReportRenderer(Protocol):
    """Render a conversation transcript into a durable report format."""

    def render(
        self,
        messages: list[dict[str, str]],
        session_start: datetime | None = None,
    ) -> str:
        """Render messages into a report string (e.g. HTML).

        Args:
            messages: Conversation history.
            session_start: Optional session start time for report metadata.

        Returns:
            Rendered report content as a string.
        """
        ...


@runtime_checkable
class SystemPromptBuilder(Protocol):
    """Build the system prompt, optionally injecting a user profile."""

    def build(self, profile: UserProfile | None = None) -> str:
        """Return the system prompt text.

        Args:
            profile: Optional user profile to personalize the prompt.

        Returns:
            The complete system prompt string.
        """
        ...

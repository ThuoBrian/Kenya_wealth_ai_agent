"""Agent conversation orchestration service."""

from collections.abc import AsyncIterator
from datetime import datetime

import structlog

from kenya_wealth_agent.application.ports import (
    LLMClient,
    SessionRepository,
    SystemPromptBuilder,
)
from kenya_wealth_agent.domain.models import UserProfile
from kenya_wealth_agent.domain.validators import require_non_negative

logger = structlog.get_logger()

MAX_MESSAGE_LENGTH = 4_000


class AgentService:
    """Orchestrate LLM conversations for a Kenya financial advisor.

    The service is stateless with respect to any single session: it loads and
    saves history through the injected ``SessionRepository``.  This keeps
    per-user isolation at the repository layer and makes the service easy to
    test.
    """

    def __init__(
        self,
        llm_client: LLMClient,
        prompt_builder: SystemPromptBuilder,
        repository: SessionRepository,
        model: str,
        max_message_length: int = MAX_MESSAGE_LENGTH,
    ):
        """Initialize the agent service.

        Args:
            llm_client: Adapter that fulfills the LLM port.
            prompt_builder: Adapter that builds the system prompt.
            repository: Adapter that stores conversation history.
            model: Default model name to pass to the LLM client.
            max_message_length: Maximum characters accepted in a user message.
        """
        self.llm_client = llm_client
        self.prompt_builder = prompt_builder
        self.repository = repository
        self.model = model
        self.max_message_length = require_non_negative(max_message_length, "max_message_length")

    def _validate_message(self, user_message: str) -> str:
        """Strip and validate a user message, returning the normalized text."""
        normalized = user_message.strip()
        if not normalized:
            raise ValueError("Message cannot be empty")
        if len(normalized) > self.max_message_length:
            raise ValueError(f"Message exceeds {self.max_message_length} character limit")
        return normalized

    async def chat(
        self,
        session_id: str,
        user_message: str,
        profile: UserProfile | None = None,
    ) -> str:
        """Process a user message and return the assistant response.

        Args:
            session_id: Unique identifier for the conversation.
            user_message: The user's message text.
            profile: Optional user profile to personalize the system prompt.

        Returns:
            The assistant's response text.

        Raises:
            ValueError: If the message is empty or exceeds the length limit.
        """
        normalized = self._validate_message(user_message)
        history = await self.repository.get(session_id)
        timestamp = datetime.now().isoformat()
        history.append({"role": "user", "content": normalized, "timestamp": timestamp})

        system_prompt = self.prompt_builder.build(profile)
        messages = [{"role": "system", "content": system_prompt}, *history]

        logger.debug(
            "calling_llm",
            session_id=session_id,
            model=self.model,
            history_length=len(history),
        )
        response = await self.llm_client.chat(messages=messages, model=self.model)

        history.append(
            {"role": "assistant", "content": response, "timestamp": datetime.now().isoformat()}
        )
        await self.repository.save(session_id, history)

        logger.debug(
            "llm_response_received",
            session_id=session_id,
            response_length=len(response),
        )
        return response

    async def chat_stream(
        self,
        session_id: str,
        user_message: str,
        profile: UserProfile | None = None,
    ) -> AsyncIterator[str]:
        """Stream the assistant response for a user message.

        The response is accumulated and persisted as a single assistant message
        once the stream completes successfully.

        Args:
            session_id: Unique identifier for the conversation.
            user_message: The user's message text.
            profile: Optional user profile to personalize the system prompt.

        Yields:
            Response chunks as they arrive from the LLM.

        Raises:
            ValueError: If the message is empty or exceeds the length limit.
        """
        normalized = self._validate_message(user_message)
        history = await self.repository.get(session_id)
        history.append(
            {"role": "user", "content": normalized, "timestamp": datetime.now().isoformat()}
        )

        system_prompt = self.prompt_builder.build(profile)
        messages = [{"role": "system", "content": system_prompt}, *history]

        logger.debug(
            "calling_llm_stream",
            session_id=session_id,
            model=self.model,
            history_length=len(history),
        )

        chunks: list[str] = []
        async for chunk in self.llm_client.chat_stream(
            messages=messages,
            model=self.model,
        ):
            chunks.append(chunk)
            yield chunk

        response = "".join(chunks)
        history.append(
            {"role": "assistant", "content": response, "timestamp": datetime.now().isoformat()}
        )
        await self.repository.save(session_id, history)

        logger.debug(
            "llm_stream_complete",
            session_id=session_id,
            response_length=len(response),
        )

    async def get_history(self, session_id: str) -> list[dict[str, str]]:
        """Return the conversation history for a session."""
        return await self.repository.get(session_id)

    async def reset(self, session_id: str) -> None:
        """Clear the conversation history for a session."""
        await self.repository.clear(session_id)

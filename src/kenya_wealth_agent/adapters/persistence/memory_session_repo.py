"""In-memory session repository.

Default adapter for local, single-instance deployments.  Conversations are
isolated by session ID but are lost when the process exits.  A persistent
adapter (e.g. SQLite) can be dropped in later without changing services.
"""

from copy import deepcopy

from kenya_wealth_agent.application.ports import SessionRepository


class InMemorySessionRepository(SessionRepository):
    """Store conversation history in an in-memory dict keyed by session ID."""

    def __init__(self) -> None:
        self._sessions: dict[str, list[dict[str, str]]] = {}

    async def get(self, session_id: str) -> list[dict[str, str]]:
        """Return a shallow copy of the session's message history."""
        return deepcopy(self._sessions.get(session_id, []))

    async def save(
        self,
        session_id: str,
        messages: list[dict[str, str]],
    ) -> None:
        """Persist the full message list for a session."""
        self._sessions[session_id] = deepcopy(messages)

    async def clear(self, session_id: str) -> None:
        """Remove the session from memory."""
        self._sessions.pop(session_id, None)

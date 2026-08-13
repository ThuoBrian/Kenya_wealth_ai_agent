"""Conversation history and session management routes."""

from contextlib import suppress
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from kenya_wealth_agent.application.agent_service import AgentService
from kenya_wealth_agent.application.financial_services import ReportService
from kenya_wealth_agent.interfaces.web.dependencies import (
    get_agent_service,
    get_report_service,
    get_session_id,
)

router = APIRouter(tags=["history"])


class MessageItem(BaseModel):
    """A single message in the conversation history."""

    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: str


class ConversationHistory(BaseModel):
    """Conversation history for a session."""

    messages: list[MessageItem]
    started_at: str | None = None


class ResetResponse(BaseModel):
    """Response from a session reset."""

    status: str = "ok"
    message: str = "Conversation reset"


class ExportResponse(BaseModel):
    """Response from an HTML report export."""

    status: str = "ok"
    path: str


def _set_session_cookie(response: Response, session_id: str) -> None:
    """Attach the session id cookie to a response."""
    response.set_cookie(
        key="kwa_session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=86_400,
    )


@router.get("/history", response_model=ConversationHistory)
async def get_history(
    response: Response,
    session_id: str = Depends(get_session_id),
    agent_service: AgentService = Depends(get_agent_service),
) -> ConversationHistory:
    """Return the conversation history for the current session."""
    history = await agent_service.get_history(session_id)
    started_at: str | None = None
    for msg in history:
        if msg.get("role") == "user" and msg.get("timestamp"):
            started_at = msg["timestamp"]
            break

    messages = [
        MessageItem(role=m["role"], content=m["content"], timestamp=m.get("timestamp", ""))
        for m in history
        if m.get("role") in ("user", "assistant")
    ]
    _set_session_cookie(response, session_id)
    return ConversationHistory(messages=messages, started_at=started_at)


@router.post("/reset", response_model=ResetResponse)
async def reset_conversation(
    response: Response,
    session_id: str = Depends(get_session_id),
    agent_service: AgentService = Depends(get_agent_service),
) -> ResetResponse:
    """Clear the conversation history for the current session."""
    try:
        await agent_service.reset(session_id)
    except Exception as exc:  # pragma: no cover - defensive catch
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset session: {exc}",
        ) from exc
    _set_session_cookie(response, session_id)
    return ResetResponse()


@router.get("/export", response_model=ExportResponse)
async def export_report(
    response: Response,
    session_id: str = Depends(get_session_id),
    agent_service: AgentService = Depends(get_agent_service),
    report_service: ReportService = Depends(get_report_service),
) -> ExportResponse:
    """Export the current conversation as a styled HTML report."""
    history = await agent_service.get_history(session_id)
    session_start: datetime | None = None
    for msg in history:
        if msg.get("role") == "user" and msg.get("timestamp"):
            with suppress(ValueError):
                session_start = datetime.fromisoformat(msg["timestamp"])
            break

    try:
        path = await report_service.export(history, session_start=session_start)
    except Exception as exc:  # pragma: no cover - defensive catch
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export report: {exc}",
        ) from exc

    _set_session_cookie(response, session_id)
    return ExportResponse(status="ok", path=path)

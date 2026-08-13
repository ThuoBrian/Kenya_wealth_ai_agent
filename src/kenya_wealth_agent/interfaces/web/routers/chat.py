"""Chat and status routes for the Kenya Wealth Agent web API."""

from collections.abc import AsyncGenerator
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from kenya_wealth_agent.application.agent_service import AgentService
from kenya_wealth_agent.config.settings import Settings
from kenya_wealth_agent.interfaces.web.dependencies import (
    get_agent_service,
    get_session_id,
    get_settings_dependency,
)

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    """Payload for a single user message."""

    message: str = Field(..., min_length=1, max_length=4_000)

    @field_validator("message")
    @classmethod
    def _strip_and_require_non_empty(cls, value: str) -> str:
        """Reject whitespace-only messages at the validation layer."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("Message cannot be empty")
        return stripped


class ChatResponse(BaseModel):
    """Non-streaming response payload."""

    response: str
    timestamp: str


class StatusResponse(BaseModel):
    """Status response from the LLM health probe."""

    connected: bool
    model: str
    base_url: str
    version: str


@router.post("/chat")
@limiter.limit("10/minute")
async def chat(
    request: Request,
    payload: ChatRequest,
    session_id: str = Depends(get_session_id),
    agent_service: AgentService = Depends(get_agent_service),
    settings: Settings = Depends(get_settings_dependency),
    stream: bool = True,
) -> Response:
    """Receive a user message and return the assistant response.

    By default the response is streamed back as ``text/plain`` so the frontend
    can render tokens as they arrive.  Pass ``?stream=false`` (or an
    ``Accept: application/json`` header) to receive the full response as JSON.
    """
    if not settings.enable_streaming:
        stream = False

    if stream:

        async def _stream_bytes() -> AsyncGenerator[bytes, None]:
            try:
                async for chunk in agent_service.chat_stream(
                    session_id=session_id,
                    user_message=payload.message,
                ):
                    yield chunk.encode()
            except ValueError as exc:
                yield f"\n\n**Error:** {exc}".encode()
            except RuntimeError as exc:
                yield f"\n\n**Connection error:** {exc}".encode()

        stream_response = StreamingResponse(
            _stream_bytes(),
            media_type="text/plain; charset=utf-8",
        )
        stream_response.set_cookie(
            key="kwa_session_id",
            value=session_id,
            httponly=True,
            samesite="lax",
            max_age=86_400,
        )
        return stream_response

    try:
        response_text = await agent_service.chat(
            session_id=session_id,
            user_message=payload.message,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    payload_model = ChatResponse(
        response=response_text,
        timestamp=datetime.now().strftime("%H:%M"),
    )
    json_response = JSONResponse(content=payload_model.model_dump())
    json_response.set_cookie(
        key="kwa_session_id",
        value=session_id,
        httponly=True,
        samesite="lax",
        max_age=86_400,
    )
    return json_response


@router.get("/status", response_model=StatusResponse)
async def get_status(
    agent_service: AgentService = Depends(get_agent_service),
    settings: Settings = Depends(get_settings_dependency),
) -> StatusResponse:
    """Probe the LLM provider and report whether the agent is online."""
    connected = await agent_service.llm_client.is_available()
    return StatusResponse(
        connected=connected,
        model=settings.model,
        base_url=settings.base_url,
        version=settings.version,
    )

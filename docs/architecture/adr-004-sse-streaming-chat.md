# ADR-004: Server-Sent Events (SSE) Streaming for Chat

## Status

Accepted

## Context

The web frontend supports streaming responses: it checks the response
`Content-Type` for `text/plain` or `text/event-stream` and renders chunks as they
arrive. The backend therefore needs a streaming path that works with the
existing UI without requiring frontend changes.

## Decision

Implement streaming in the `AgentService` via the `LLMClient.chat_stream()`
port. The web router returns a FastAPI `StreamingResponse` with
`media_type="text/plain; charset=utf-8"`. Each chunk from Ollama is encoded and
yielded immediately; the full response is persisted once the stream completes.
Non-streaming JSON responses remain available via `?stream=false` and for
clients that do not request streaming.

## Consequences

- Perceived latency is lower because the user sees tokens as they arrive.
- The agent still accumulates and stores the complete response for history and
  report generation.
- A plain-text stream is easy for the frontend to consume without parsing SSE
  frames.

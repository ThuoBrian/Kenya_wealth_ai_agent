# ADR-002: Ollama-Only LLM Port

## Status

Accepted

## Context

The project needs a local-first, privacy-preserving LLM integration. Multiple
cloud providers would add configuration complexity and could expose sensitive
financial data to third parties.

## Decision

Provide a single LLM port backed by `ollama.AsyncClient`. The port exposes:

- `chat()` for full-response calls.
- `chat_stream()` for token-by-token streaming via Ollama's native streaming API.
- `is_available()` for health checks.

The `FakeLLMClient` adapter provides a deterministic test double and offline
 demo implementation of the same port.

## Consequences

- A single, intentionally narrow port keeps the codebase simple.
- Streaming and health checks are first-class operations, not afterthoughts.
- Future providers can be added by implementing the same port without touching
  services.

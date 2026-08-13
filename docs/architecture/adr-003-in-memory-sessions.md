# ADR-003: In-Memory Per-Session Persistence

## Status

Accepted

## Context

The agent is designed for local, single-user deployments. Persistent databases
would add operational overhead and conflict with the local-first, privacy-first
goals.

## Decision

Use an in-memory `SessionRepository` keyed by a session id cookie (`kwa_session_id`).
`InMemorySessionRepository` stores deep-copied message histories per session id
and is discarded when the process exits.

## Consequences

- No setup or migration is required.
- Conversation state is isolated per session id but lost on restart, which is
  acceptable for the current local-only use case.
- The port is swappable: a SQLite or Redis adapter can replace it later without
  changing the chat service.

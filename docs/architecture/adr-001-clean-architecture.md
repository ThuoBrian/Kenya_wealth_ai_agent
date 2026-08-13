# ADR-001: Clean Architecture / Ports & Adapters

## Status

Accepted

## Context

The original codebase was a monolithic script where domain logic, LLM calls,
HTML rendering, and web routing were tightly coupled. This made testing hard,
blocked alternative implementations (e.g. a different LLM backend), and made it
unclear where new features should live.

## Decision

Adopt Clean Architecture with explicit Ports & Adapters:

- `domain/` contains pure business logic (tax, budget, investment calculations,
  Pydantic models). It has no framework or LLM dependencies.
- `application/` contains orchestration services and `Protocol` ports such as
  `LLMClient`, `SessionRepository`, `ReportRenderer`, and `SystemPromptBuilder`.
- `adapters/` contains concrete implementations (Ollama client, in-memory session
  repository, HTML report renderer).
- `interfaces/` contains HTTP and CLI adapters.

## Consequences

- Domain logic can be unit tested without an LLM or database.
- A SQLite-backed session repository, a different LLM provider, or a PDF renderer
  can be added without changing services.
- The dependency direction is strictly inward: interfaces depend on application
  services, not the other way around.

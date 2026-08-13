# Kenya Wealth Agent — Architecture & Design Overhaul Plan

**Status:** Approved — implemented  
**Goal:** Elevate the project from a working MVP to a maintainable, secure, testable, and Kenya-context-accurate financial advisor that follows current Python/FastAPI industry best practices. Every decision below is intentional, documented, and aligned with the project’s stated purpose.

---

## 1. Project Goals & Constraints (North Star)

| Goal | How this plan serves it |
|------|--------------------------|
| Provide **Kenya-aware** financial advice (MPesa, SACCOs, NSE, PAYE, etc.) | Domain models and constants stay Kenya-specific; all calculations are unit-tested against KRA/CBK/NSSF/SHIF rules. |
| Run **locally-first** with local LLMs via Ollama | Adapters keep Ollama behind a port so it can be swapped for OpenAI/Anthropic later without touching domain logic. |
| Offer both **CLI** and **web** interfaces | Interfaces layer shares application services; no logic duplication. |
| Stay **educational, not a licensed advisor** | Disclaimers are injected in prompts, HTML reports, and API responses. |
| Prioritize **trust and correctness** for financial calculations | Pure domain functions are 100% unit-tested; LLM output is never trusted for math. |

**Constraints:** Single-machine/local usage today, but architecture must not prevent future multi-user deployment.

---

## 2. Target Architecture: Clean Architecture / Ports & Adapters

We will reorganize the codebase into four layers plus infrastructure. External dependencies (LLM, web framework, file system) point inward only.

```
┌─────────────────────────────────────────────┐
│  Interfaces (CLI / Web / Future API clients) │
├─────────────────────────────────────────────┤
│  Application Services                       │
│  - AgentService, BudgetService, TaxService, │
│    InvestmentService, EmergencyService,     │
│    ReportService                            │
├─────────────────────────────────────────────┤
│  Domain                                     │
│  - Models, value objects, enums, pure calc.   │
├─────────────────────────────────────────────┤
│  Ports (abstract)                           │
│  - LLMClient, SessionRepository,            │
│    ReportRenderer, Config                   │
├─────────────────────────────────────────────┤
│  Adapters (concrete)                        │
│  - OllamaLLMClient, InMemorySessionRepo,    │
│    HTMLReportRenderer, PydanticSettings       │
└─────────────────────────────────────────────┘
```

### Directory structure

```
kenya_wealth_agent/
├── pyproject.toml                # packaging, deps, tool configs
├── README.md
├── docs/
│   ├── ADR-001-clean-architecture.md
│   ├── ADR-002-pydantic-v2-domain-models.md
│   ├── ADR-003-async-ollama-adapter.md
│   └── ADR-004-session-storage-strategy.md
├── src/kenya_wealth_agent/       # package source
│   ├── __init__.py
│   ├── config/
│   │   ├── settings.py           # pydantic-settings, env + config.ini
│   │   └── constants.py          # KRA brackets, CBK rates, etc.
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py             # UserProfile, FinancialGoal, RiskTolerance, Money
│   │   ├── tax.py                # PAYE/SHIF/NSSF/HousingLevy pure calc
│   │   ├── budget.py             # 50/30/20 + Kenya recommendations
│   │   ├── investment.py         # allocation logic
│   │   ├── emergency.py          # emergency fund calc
│   │   ├── retirement.py         # NEW: retirement planning
│   │   ├── savings.py            # NEW: savings strategies
│   │   └── validators.py         # shared domain validation (>=0, etc.)
│   ├── application/
│   │   ├── __init__.py
│   │   ├── ports.py              # Protocols / ABCs
│   │   ├── agent_service.py      # conversation orchestration
│   │   ├── budget_service.py
│   │   ├── tax_service.py
│   │   ├── investment_service.py
│   │   ├── emergency_service.py
│   │   ├── retirement_service.py
│   │   ├── savings_service.py
│   │   └── report_service.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── llm/
│   │   │   ├── ollama_client.py      # async Ollama wrapper
│   │   │   └── fake_client.py        # test double / offline mode
│   │   ├── persistence/
│   │   │   ├── memory_session_repo.py  # per-session in-memory store
│   │   │   └── sqlite_session_repo.py  # future: durable sessions
│   │   └── rendering/
│   │       ├── html_report.py        # extracted from templates/html.py
│   │       └── static/
│   │           └── report.css        # extracted inline CSS
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── cli/
│   │   │   ├── __main__.py
│   │   │   ├── commands.py           # command classes instead of monolithic main()
│   │   │   └── app.py                # CLI setup
│   │   └── web/
│   │       ├── app.py                # FastAPI app factory
│   │       ├── dependencies.py       # DI wiring
│   │       ├── routers/
│   │       │   ├── chat.py
│   │       │   ├── tools.py
│   │       │   └── history.py
│   │       └── static/
│   │           └── index.html        # moved from web/index.html
│   └── prompts/
│       └── system.py                 # prompt builder with UserProfile injection
├── tests/
│   ├── conftest.py
│   ├── unit/domain/               # pure calculation tests
│   ├── unit/application/          # service orchestration tests
│   ├── unit/adapters/             # adapter contract tests
│   └── integration/interfaces/    # FastAPI endpoint tests
├── .github/workflows/
│   └── ci.yml
├── .pre-commit-config.yaml
├── Dockerfile
└── docker-compose.yml
```

---

## 3. Key Architectural Decisions (ADRs)

### ADR-001: Clean Architecture / Ports & Adapters
- **Decision:** Separate domain, application, adapters, and interfaces.
- **Rationale:** Financial calculation correctness must be testable in isolation from LLM, web framework, and CLI. It also lets us swap Ollama for another provider or add a Telegram/WhatsApp interface later.
- **Trade-off:** More files and slightly more boilerplate than the current flat layout, but the project is growing and the audit identified this as a maintainability risk.

### ADR-002: Pydantic v2 for Domain Models
- **Decision:** Replace dataclass-only models with Pydantic v2 `BaseModel`/`@validate_call` for all financial inputs and `UserProfile`.
- **Rationale:** Built-in validation, serialization, FastAPI-native integration, and excellent error messages. Prevents negative salaries, invalid risk tolerances, and empty messages at the boundary.
- **Trade-off:** Adds a dependency already required by FastAPI; no real downside.

### ADR-003: Async LLM Adapter
- **Decision:** Wrap Ollama in an async `LLMClient` port and call it via `await` from FastAPI endpoints. CLI can run the same adapter synchronously with `asyncio.run` or a sync shim.
- **Rationale:** FastAPI is async-by-default. The current synchronous `ollama.Client.chat(...)` blocks the event loop, which the code-review found. Async keeps the web UI responsive and allows SSE streaming later.
- **Trade-off:** Requires `ollama.AsyncClient` or `httpx.AsyncClient`; small learning curve, standard FastAPI practice.

### ADR-004: In-Memory Session Store with a Repository Port
- **Decision:** Replace the global `SessionState` singleton with a `SessionRepository` port. Default adapter is an in-memory dict keyed by session ID. A SQLite adapter can be added later without changing services.
- **Rationale:** Fixes the shared-conversation bug, enables per-user isolation, and keeps persistence optional/local. Aligns with the ROADMAP goal of “persistent profiles” without over-engineering today.
- **Trade-off:** Slightly more indirection; session ID must be passed by web clients.

### ADR-005: Sync over Async in Services, Async at Interface
- **Decision:** Core domain calculations remain synchronous pure functions. Application services are async only when they cross a port (e.g., LLM call, DB write).
- **Rationale:** Async adds no value to `calculate_tax` but is essential for I/O. This minimizes unnecessary `async`/`await` noise.

### ADR-006: Markdown Rendering Security
- **Decision:** Replace regex-based HTML sanitization with `nh3` (or `bleach`) for assistant markdown, and strict `html.escape` for user content. No raw HTML from the LLM is ever rendered without sanitization.
- **Rationale:** Regex sanitizer is fragile and flagged in the security audit. `nh3` is actively maintained and designed for this exact use case.
- **Trade-off:** New dependency; small and well-regarded.

### ADR-007: Test-First for Financial Logic
- **Decision:** Write pytest unit tests for all domain calculations before or alongside refactoring. Target >90% coverage in `domain/` and `application/`.
- **Rationale:** Financial advice must be numerically correct. Tests are the cheapest correctness guarantee and the project currently has zero tests.
- **Trade-off:** Upfront time; pays for itself immediately given the PAYE off-by-one and investment-parsing bugs found.

---

## 4. Critical Bugs to Fix (from code-review & audit)

| # | Bug | File(s) | Fix |
|---|-----|---------|-----|
| 1 | `/api/history` always empty because web routes never populate `session.messages` | `web/app.py` | Use the same `SessionRepository` the agent uses; history reads from it. |
| 2 | Investment risk parsing silently defaults unknown strings to aggressive | `services/investment.py` | Accept `RiskTolerance` enum or validated string; raise `ValueError` on invalid input. |
| 3 | FastAPI routes block event loop with sync Ollama calls | `web/app.py`, `agent.py` | Use async LLM adapter (`ollama.AsyncClient` or `httpx`). |
| 4 | Investment service crashes when passed the package’s own `RiskTolerance` enum | `services/investment.py` | Handle enum values, not just lowercase strings. |
| 5 | Tax calculator accepts negative salaries and emits negative deductions | `services/tax.py` | Pydantic/domain validation: `gross_salary >= 0`. |
| 6 | PAYE bracket math undercounts inclusive 1-KES boundary by 1 in non-first brackets | `config/constants.py` | Bracket definitions use correct inclusive bounds or bracket calc uses `max(0, min(...)) - lower` correctly; add tests against known KRA examples. |
| 7 | Global singleton session state leaks across users | `web/app.py` | Replace with keyed `SessionRepository`. |
| 8 | CORS `allow_origins=["*"]` + `allow_credentials=True` is insecure | `web/app.py` | Restrict to `localhost:8000` or make configurable; default safe. |
| 9 | Error responses leak internal exception text | `web/app.py` | Log full exception server-side; return generic safe messages to client. |
| 10 | Regex-based HTML sanitization is fragile | `templates/html.py` | Use `nh3`/`bleach`. |

---

## 5. Implementation Phases

### Phase 0 — Tooling & Safety Foundation
- Create `pyproject.toml` with:
  - project metadata, Python requirement, dependencies, dev dependencies
  - `ruff` config (lint + format + import sorting)
  - `mypy` strict config
  - `pytest` + `pytest-asyncio` + `pytest-cov`
- Add `.pre-commit-config.yaml` (ruff, mypy, trailing whitespace).
- Add GitHub Actions workflow: lint, type-check, test.
- Add `Makefile` / `poe` tasks for `lint`, `test`, `serve`, `cli`.
- Remove duplicate `fastapi`/`uvicorn` from `requirements.txt`; migrate deps to `pyproject.toml`.
- Introduce `structlog` for structured logging; replace `print()` in services with logger calls.

**Deliverable:** Project builds, lints, type-checks, and runs existing code with no regressions.

### Phase 1 — Domain Layer & Validation
- Create `domain/` package.
- Convert `UserProfile`, `FinancialGoal`, `RiskTolerance` to Pydantic v2 models.
- Add `Money`/`KESAmount` value object or `PositiveFloat` validators.
- Move tax calculation into `domain/tax.py` with correct inclusive bracket math and validation.
- Move budget, investment, emergency calculations into `domain/`.
- Add new `domain/retirement.py` and `domain/savings.py` modules.
- Write comprehensive unit tests for every pure function (target 95%+ domain coverage).

**Deliverable:** All financial calculations are tested and bug-free; negative inputs rejected at the boundary.

### Phase 2 — Application Services & Ports
- Define `application/ports.py`:
  - `LLMClient` (async `chat(messages) -> str`)
  - `SessionRepository` (async `get`, `save`, `delete`, `list`)
  - `ReportRenderer` (sync or async `render(history) -> str/path`)
- Implement `AgentService` that:
  - loads system prompt with optional `UserProfile` injection
  - stores conversation in the repository
  - returns assistant message
- Implement thin service wrappers for budget/tax/investment/emergency/retirement/savings that validate inputs and delegate to domain.
- Implement `ReportService`.

**Deliverable:** Business logic is independent of CLI, web, and Ollama.

### Phase 3 — Adapters
- `adapters/llm/ollama_client.py`: async wrapper using `ollama.AsyncClient`.
- `adapters/persistence/memory_session_repo.py`: keyed in-memory store.
- `adapters/rendering/html_report.py`: extract logic from `templates/html.py`.
- `adapters/rendering/static/report.css`: extract inline CSS.
- `config/settings.py`: migrate to `pydantic-settings` with env + `config.ini` support.

**Deliverable:** App can run with Ollama, in-memory sessions, and HTML reports via adapters.

### Phase 4 — Interfaces
- **Web:**
  - FastAPI app factory with dependency injection (`dependencies.py`).
  - Routers: `/api/chat`, `/api/history`, `/api/reset`, `/api/tools/{budget,tax,investment,emergency,retirement,savings}`, `/api/export`.
  - Per-session ID via cookie or header; history uses `SessionRepository`.
  - Async chat endpoint; optionally wire SSE streaming with `sse-starlette`.
  - Safe CORS, sanitized errors, request-size limits.
- **CLI:**
  - Refactor `main.py` into `interfaces/cli/commands.py` with a small command class per feature.
  - Use `AgentService` and other application services.
  - Keep report generation on exit.
- Move `web/index.html` to `interfaces/web/static/index.html`; update `start_web.sh`.

**Deliverable:** CLI and web both work, history is consistent, and the web UI is no longer globally shared.

### Phase 5 — Hardening & Documentation
- Replace regex HTML sanitization with `nh3` in report renderer.
- Add security headers to FastAPI.
- Add rate limiting (slowapi) on `/api/chat` to mitigate DoS/LLM cost abuse.
- Add input length limits (e.g., 4,000 chars per message).
- Write `docs/ADR-00x.md` for each decision above.
- Update `README.md` with architecture overview and contributor guide.
- Add `Dockerfile` + `docker-compose.yml` for local Ollama + app stack.

**Deliverable:** Project is documented, containerized, and passes security review.

---

## 6. Validation Criteria

Before the overhaul is considered complete, the following must pass:

1. **All existing bugs fixed:** The 10 bugs listed in §4 have regression tests.
2. **Test coverage:** `domain/` ≥95%, `application/` ≥90%, adapters ≥70%, web endpoints ≥60%.
3. **Lint/format/type:** `ruff check .`, `ruff format --check .`, `mypy src/` pass in CI.
4. **Functional parity:** CLI and web UI still launch and produce advice + reports.
5. **Security:** No raw exception text in API responses; CORS restricted; HTML sanitized; input validated.
6. **Documentation:** Each major decision has an ADR; README reflects new structure.

---

## 7. Open Questions for the User

To keep the plan aligned with your intent, please confirm:

1. **Scope:** Should I proceed with the full Clean Architecture restructure (Phases 0–5), or do you prefer a smaller incremental modernization (Phase 0 + critical bug fixes only)?
2. **Persistence:** Is in-memory per-session storage acceptable for now, or do you want SQLite/PostgreSQL introduced immediately?
3. **Streaming:** Should SSE streaming for `/api/chat` be wired now, or deferred to a later phase?
4. **LLM provider lock-in:** Do you want to keep Ollama-only, or design the port to allow swapping to OpenAI/Anthropic later?
5. **Packaging:** Are you comfortable moving to `pyproject.toml` and dropping `requirements.txt` as the primary source of truth?

Once you confirm scope and priorities, I will produce the detailed implementation plan and begin executing it file by file.

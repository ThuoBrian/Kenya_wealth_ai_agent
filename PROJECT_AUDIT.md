# Kenya Wealth Agent - Project Audit

**Audit Date:** 2026-04-18
**Auditor:** Claude Code
**Version Audited:** 1.0.0 (commit `bd21db5`)

---

## 1. Executive Summary

Kenya Wealth Agent is a functional MVP that delivers Kenya-specific financial advice via CLI and web interfaces, powered by a local LLM (Ollama). The core value proposition — conversational AI with Kenya-aware financial computation — works end-to-end. The web UI is notably polished for an MVP (dark mode, accessibility, responsive design, XSS mitigations).

**Overall Health: YELLOW** — Core features work, but the project has zero test coverage, incomplete security hardening, no persistence, and missing dev tooling. The ROADMAP is well-maintained and accurately tracks known issues.

| Category | Status | Key Concern |
|---|---|---|
| Security | ⚠️ Attention Required | XSS partially mitigated; input validation gaps |
| Test Coverage | 🔴 Critical | Zero tests |
| Feature Completeness | 🟡 Partial | Streaming, persistence, profile integration incomplete |
| Code Quality | 🟢 Good | Docstrings, type hints, clean module structure |
| Infrastructure | 🔴 Critical | No CI/CD, Docker, linting, or formatting tooling |

---

## 2. Project Overview

- **Purpose:** AI-powered personal financial advisor for the Kenyan market
- **Author:** Brian Thuo
- **License:** MIT
- **Domain:** Budgeting, tax (PAYE), investment, emergency funds, retirement — all localized to Kenyan financial instruments (MPesa, SACCOs, NSE, Treasury Bills, M-Akiba, etc.)

### Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ (running 3.14 in `.venv`) |
| LLM Backend | Ollama (default model: `glm-5.1:cloud`) |
| Web Framework | FastAPI + Uvicorn |
| Frontend | Vanilla HTML/CSS/JS (single-page, 2,158 lines) |
| SSE | `sse-starlette` (installed but **not wired**) |
| Markdown | `markdown` (Python, for report generation) |
| Terminal | `colorama` |
| Config | `configparser` (INI) + `python-dotenv` |
| Validation | Pydantic (via FastAPI models) |
| Data Models | Python `dataclasses` + `Enum` |
| Package Mgmt | `pip` + `requirements.txt` (no `pyproject.toml`) |

---

## 3. Codebase Metrics

| Metric | Value |
|---|---|
| Python source files | 20 (excluding `.venv`) |
| Python lines of code | 2,325 |
| Largest file | `templates/html.py` (804 lines) |
| Web frontend | `web/index.html` (2,158 lines) |
| HTML template | `templates/html.py` (804 lines — includes inline CSS) |
| Dependencies | 7 unique (9 listed — 2 duplicates) |
| Test files | 0 |
| Configuration files | `config.ini`, `.env`, `requirements.txt`, `.gitignore` |
| Git commits | 1 (initial) |

### Top Files by Size

| File | Lines | Role |
|---|---|---|
| `templates/html.py` | 804 | HTML report generator with inline CSS |
| `web/app.py` | 243 | FastAPI backend (API routes) |
| `config/settings.py` | 195 | Config class (INI + env loading) |
| `main.py` | 167 | CLI entry point |
| `agent.py` | 164 | Core agent class |
| `utils/display.py` | 111 | Terminal display helpers |
| `config/constants.py` | 107 | Kenya financial constants |
| `services/budget.py` | 87 | Budget analysis |
| `services/investment.py` | 83 | Investment recommendations |
| `services/tax.py` | 80 | PAYE calculator |
| `prompts/system.py` | 71 | System prompt generator |

---

## 4. Security Findings

### CRITICAL

| ID | Issue | File | Detail |
|---|---|---|---|
| SEC-1 | XSS in HTML reports | `templates/html.py` | User content passes through `html.escape()` + `_HTML_TAG_RE` regex stripping, but regex-based sanitization is inherently fragile. A dedicated sanitization library (e.g., `bleach`) would be more robust. ROADMAP still flags this as PENDING. |

### HIGH

| ID | Issue | File | Detail |
|---|---|---|---|
| SEC-2 | No input validation in `chat()` | `agent.py:61` | The `chat()` method accepts arbitrary-length strings with no length/type checks. A malicious or accidental oversized input could cause DoS or excessive LLM token consumption. |
| SEC-3 | Unsafe subprocess (historical) | `agent.py` | ROADMAP flags `os.system` usage. Current code does not use `os.system`, but the audit trail should be closed by removing this from the roadmap or documenting the fix. |
| SEC-4 | CORS allows all origins | `web/app.py:35` | `allow_origins=["*"]` with `allow_credentials=True` is insecure. For a local-only app this is acceptable, but if ever deployed publicly, this must be restricted. |
| SEC-5 | Global singleton session state | `web/app.py:51` | `SessionState` is a module-level singleton — no per-user isolation. If two users hit the web API, they share the same conversation. |

### MEDIUM

| ID | Issue | File | Detail |
|---|---|---|---|
| SEC-6 | Duplicate config loader (historical) | N/A | ROADMAP references `config/loader.py` but the file does not exist. Likely consolidated, but roadmap entry should be closed. |
| SEC-7 | Error messages expose internals | `web/app.py:148,197,217` | `HTTPException(detail=str(e))` passes raw exception text to the client, potentially leaking internal paths, model names, or stack info. |

---

## 5. Architecture Review

### Strengths

- **Clean separation of concerns:** `config/`, `models/`, `services/`, `prompts/`, `templates/`, `utils/`, `web/` — each module has a clear single responsibility.
- **Consistent patterns:** `__init__.py` re-exports with `__all__`, Google-style docstrings on all public functions, type hints throughout.
- **Centralized constants:** `config/constants.py` holds `TAX_BRACKETS`, `INVESTMENT_OPTIONS`, `KENYA_CONTEXT`.
- **Dual interface:** CLI (`main.py`) and web (`web/`) share the same `KenyaWealthAgent` core.

### Weaknesses

| Issue | Detail |
|---|---|
| **`UserProfile` never used** | `models/user.py` defines `UserProfile`, `FinancialGoal`, `RiskTolerance` — these are imported in `agent.py` but never passed to the LLM. The system prompt in `prompts/system.py` has no profile injection. This is dead code in practice. |
| **Monolithic `main()`** | `main.py:25-164` is a single 139-line function with inline command parsing. Should be a `CLIHandler` class. ROADMAP flags this. |
| **Large HTML template** | `templates/html.py` at 804 lines includes all CSS inline. Should extract CSS to a static file or template engine. |
| **No streaming** | `sse-starlette` is installed, the frontend `stream()` JS logic exists, but `web/app.py:/api/chat` returns a single JSON response. The feature is half-built. |
| **No persistence** | All conversation history is in-memory. Server restart = data loss. The only durable output is exported HTML files. |
| **No retirement/savings services** | CLI lists `retirement` and `savings` as commands, but there are no dedicated service modules — these fall through to LLM conversation only. |

### Module Dependency Graph

```
main.py ──→ agent.py ──→ config/
         │            ├── services/ (budget, tax, investment, emergency)
         │            ├── models/ (user)
         │            └── prompts/ (system)
         ├── templates/ (html)
         ├── utils/ (display)
         └── config/

web/app.py ──→ agent.py ──→ (same as above)
             └── templates/ (html)
```

---

## 6. Code Quality

### Strengths

| Attribute | Assessment |
|---|---|
| Docstrings | ✅ All public functions and classes have Google-style docstrings |
| Type hints | ✅ Consistent usage of `Dict`, `List`, `Optional`, `Any`, primitives |
| Module structure | ✅ Clean `__init__.py` with `__all__` exports |
| Import hygiene | ✅ No circular imports; clean dependency graph |
| Error handling | ✅ Try/except at integration boundaries (Ollama, web handlers) |
| Constants | ✅ Tax brackets, investment options centralized |

### Weaknesses

| Issue | Detail |
|---|---|
| **No linter** | No `ruff`, `flake8`, or `pylint` config |
| **No formatter** | No `black`, `isort`, or `ruff format` config |
| **No type checker** | No `mypy` config |
| **No pre-commit hooks** | No `.pre-commit-config.yaml` |
| **Magic numbers** | `tax.py:60-65` has hardcoded rates (0.0275, 300, 1700, 0.06, 2160, 0.015) instead of referencing `constants.py` |
| **Inconsistent `Optional`** | Mix of `Optional[X]` and `X | None` styles possible across files |
| **Duplicate dependencies** | `requirements.txt` lists `fastapi` and `uvicorn` twice each (lines 5/8 and 6/9) |
| **No `pyproject.toml`** | Still using bare `requirements.txt` — no modern Python packaging |

---

## 7. Feature Completeness

### Fully Implemented

| Feature | Module | Notes |
|---|---|---|
| Core agent (LLM chat) | `agent.py` | Works end-to-end via Ollama |
| CLI interface | `main.py` | Full interactive UI with commands, colors, report generation |
| Web interface | `web/app.py` + `web/index.html` | FastAPI + polished SPA with dark mode, A11y, responsive |
| Budget analysis | `services/budget.py` | 50/30/20 rule adapted for Kenya |
| Tax calculator | `services/tax.py` | PAYE, SHIF, NSSF, Housing Levy (Finance Act 2023) |
| Investment recommendations | `services/investment.py` | Risk-tiered allocation |
| Emergency fund calculator | `services/emergency.py` | Target + savings strategies |
| HTML report generation | `templates/html.py` | Styled, print-ready with dark mode, disclaimers |
| Configuration system | `config/` | INI + env overrides, model aliases, singleton |
| Web accessibility | `web/index.html` | ARIA labels, keyboard nav, skip links, contrast |
| Web security (client) | `web/index.html` | DOMPurify for XSS protection |

### Incomplete / Placeholder

| Feature | Status | Detail |
|---|---|---|
| **User profiles** | 🔴 Dead code | `UserProfile` defined but never wired into agent or prompts |
| **Streaming responses** | 🟡 Half-built | Backend returns single JSON; frontend has `stream()` logic; `sse-starlette` installed |
| **Session persistence** | 🔴 Missing | In-memory only; no database or file-based storage |
| **Per-user sessions** | 🔴 Missing | Global singleton; no multi-user support |
| **Retirement planning service** | 🟡 LLM-only | No dedicated `services/retirement.py`; relies on conversation |
| **Savings strategies service** | 🟡 LLM-only | No dedicated `services/savings.py`; relies on conversation |
| **Input validation** | 🔴 Missing | No length/type checks on `chat()` input |
| **PDF/CSV export** | 🔴 Missing | HTML only |
| **i18n (Swahili)** | 🔴 Missing | Listed in ROADMAP as planned |
| **Live market data** | 🔴 Missing | Listed in ROADMAP as planned |

---

## 8. Test Coverage

**Current state: Zero tests.**

No `tests/` directory, no `test_*.py` files, no `pytest.ini`, no `conftest.py`, no test configuration of any kind.

### Critical Test Gaps

| Area | Risk Without Tests | Priority |
|---|---|---|
| Tax calculations | Wrong PAYE/SHIF/NSSF amounts → incorrect financial advice | HIGH |
| Budget analysis | Incorrect 50/30/20 splits → misleading recommendations | HIGH |
| Investment allocation | Wrong risk-tier allocations → potential financial harm | HIGH |
| Emergency fund logic | Incorrect target calculations | MEDIUM |
| Agent chat flow | LLM integration failures go undetected | MEDIUM |
| HTML report generation | XSS regressions | HIGH |
| Web API endpoints | Broken routes, missing validation | MEDIUM |
| Config loading | Wrong model/URL parsing | LOW |

### Recommended Test Stack

- `pytest` — test runner
- `pytest-asyncio` — for async FastAPI endpoint tests
- `httpx` — for FastAPI `TestClient`
- `pytest-cov` — coverage reporting

---

## 9. Infrastructure & DevOps

### Missing

| Item | Impact |
|---|---|
| **CI/CD pipeline** | No automated testing, linting, or deployment. Every check is manual. |
| **Docker / docker-compose** | No containerization. Setup requires manual Python + Ollama install. |
| **Makefile** | No standardized commands for setup, test, lint, run. |
| **pyproject.toml** | No modern Python packaging. Using bare `requirements.txt`. |
| **Pre-commit hooks** | No automated code quality enforcement on commit. |
| **Environment management** | No `direnv`, no `pyenv` config. `.env` exists but is gitignored properly. |
| **Logging** | No structured logging. Uses `print()` statements throughout. |

### Present

| Item | Detail |
|---|---|
| `.gitignore` | ✅ Comprehensive (Python, venvs, IDEs, output, secrets, `config.ini`) |
| `.env` pattern | ✅ `config.ini.example` + `.env` with gitignore |
| `start_web.sh` | ✅ Shell launcher for web UI |
| `.claude/settings.local.json` | ✅ Claude Code permission allowlist |

---

## 10. Dependency Audit

### requirements.txt

| Package | Version | Issue |
|---|---|---|
| `ollama` | >=0.4.0 | ✅ |
| `python-dotenv` | >=1.0.0 | ✅ |
| `colorama` | >=0.4.6 | ✅ |
| `markdown` | >=3.5.0 | ✅ |
| `fastapi` | >=0.109.0 | ⚠️ **Listed twice** (lines 5 and 8) |
| `uvicorn` | >=0.27.0 | ⚠️ **Listed twice** (lines 6 and 9) |
| `sse-starlette` | >=2.0.0 | ⚠️ Installed but not used in any backend code |
| `python-multipart` | >=0.0.6 | ✅ |

### Missing Dev Dependencies

- `pytest`, `pytest-asyncio`, `pytest-cov`, `httpx`
- `ruff` or `flake8` + `black` + `isort`
- `mypy`
- `pre-commit`

### Potential Vulnerability Concerns

- No `pip-audit` or `safety` integration to scan for known CVEs in dependencies.
- No version pinning — all dependencies use `>=` which allows breaking changes.

---

## 11. Prioritized Recommendations

### CRITICAL — Do Immediately

1. **Add test suite** — At minimum: unit tests for `services/tax.py`, `services/budget.py`, `services/investment.py`, `services/emergency.py`. These are pure functions with no external dependencies and carry the highest risk of silent calculation errors.
2. **Harden XSS protection** — Replace regex-based HTML sanitization in `templates/html.py` with `bleach` or `nh3`. Regex-based sanitization is a known anti-pattern.

### HIGH — Do Within 1 Week

3. **Wire `UserProfile` into agent** — The data model exists but is dead code. Inject profile fields into the system prompt so the LLM can give personalized advice.
4. **Implement SSE streaming** — The frontend and dependency are ready. Wire `sse-starlette` into `/api/chat` to enable the "typing" effect.
5. **Add input validation** — Validate `chat()` message length and type in both `agent.py` and the web API.
6. **Deduplicate `requirements.txt`** — Remove duplicate `fastapi` and `uvicorn` entries.
7. **Sanitize error responses** — Replace `detail=str(e)` with generic error messages in `web/app.py` to prevent information leakage.

### MEDIUM — Do Within 1 Month

8. **Refactor `main.py`** — Extract the monolithic `main()` into a `CLIHandler` class with command methods.
9. **Extract CSS from `templates/html.py`** — Move inline CSS to a static file or template engine. Reduce the 804-line file to a manageable size.
10. **Add modern Python packaging** — Create `pyproject.toml` with project metadata, dependencies, and dev tool configs (ruff, mypy, pytest).
11. **Add linting and formatting** — Configure `ruff` (replaces flake8 + isort + black) and `mypy`. Add `pre-commit` hooks.
12. **Restrict CORS** — Change `allow_origins=["*"]` to `["http://localhost:8000"]` or make it configurable.
13. **Add structured logging** — Replace `print()` calls with Python `logging` module.

### LOW — Schedule as Time Permits

14. **Create `services/retirement.py`** — Dedicated retirement planning module instead of relying on LLM conversation.
15. **Create `services/savings.py`** — Dedicated savings strategies module.
16. **Add per-user session management** — Replace global `SessionState` with session-scoped state (e.g., UUID-keyed dict or database).
17. **Add CI/CD** — GitHub Actions for lint + test on push/PR.
18. **Add Docker** — `Dockerfile` + `docker-compose.yml` for one-command setup with Ollama.
19. **Pin dependency versions** — Use `==` or `~=` instead of `>=` to prevent breaking changes.
20. **Move magic numbers to constants** — Tax rates in `tax.py` (0.0275, 0.06, 0.015, etc.) should reference `constants.py`.
21. **Close stale ROADMAP entries** — `config/loader.py` duplicate and `os.system` references no longer exist in the codebase.

---

## 12. File-by-File Risk Summary

| File | Risk Level | Key Concern |
|---|---|---|
| `templates/html.py` | 🔴 Critical | XSS sanitization via regex; 804 lines of mixed Python + CSS |
| `agent.py` | 🟠 High | No input validation; `UserProfile` imported but unused |
| `web/app.py` | 🟠 High | Global session state; CORS wildcard; error info leakage |
| `main.py` | 🟡 Medium | Monolithic function; no command abstraction |
| `services/tax.py` | 🟡 Medium | Magic numbers; zero test coverage for financial calculations |
| `services/budget.py` | 🟡 Medium | Zero test coverage |
| `services/investment.py` | 🟡 Medium | Zero test coverage |
| `services/emergency.py` | 🟡 Medium | Zero test coverage |
| `prompts/system.py` | 🟢 Low | Static prompt; no profile injection |
| `config/settings.py` | 🟢 Low | Well-structured; minor duplication with `.env` |
| `config/constants.py` | 🟢 Low | Well-centralized; referenced by services |
| `models/user.py` | 🟠 High | Dead code — defined but never used |
| `utils/display.py` | 🟢 Low | Pure presentation; no logic risk |
| `web/index.html` | 🟡 Medium | Large file (2,158 lines); streaming code is dead; otherwise well-built |
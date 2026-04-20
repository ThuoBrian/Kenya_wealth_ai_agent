# Kenya Wealth Agent - Project Master Roadmap

> **Project Stage: Development** — Not production-grade. This is a well-structured prototype with 14 critical/high issues that must be resolved before any deployment beyond single-user localhost.

## Path to Production

| Phase | Focus | Key Deliverables |
| :--- | :--- | :--- |
| **1. Security Hardening** | Block everything else | Fix XSS, session isolation, CSP headers, input validation, CORS |
| **2. Reliability & Observability** | Production fundamentals | Logging, auth, history limits, API timeout/retry, rate limiting |
| **3. Correctness & Quality** | Business logic trust | Test suite, tax bracket fix, investment validation, dead code removal |
| **4. Production Infrastructure** | Deployment readiness | Docker, CI/CD, persistence, health checks, CLI refactor |

---

## Project Health Dashboard

| Category | Status | Open Issues | Priority Focus |
| :--- | :--- | :--- | :--- |
| **Security** | Critical | 14 | XSS, shared sessions, no headers, CORS |
| **Architecture** | Needs Work | 5 | No persistence, no Docker, no CI/CD |
| **UI/UX** | Stable/Improving | 7 | Streaming backend |
| **Core Logic** | Needs Work | 8 | Tax bracket gaps, dead model code, untested |

---

## Technical Debt & Security (The "Fix" List)

### CRITICAL - Blocks Any Non-Localhost Deployment

| Issue | File | Impact | Required Fix | Status |
| :--- | :--- | :--- | :--- | :--- |
| **XSS via innerHTML** when DOMPurify CDN fails | `web/index.html` render() | Script injection in every user's browser | Make DOMPurify mandatory (fail closed), add CSP | [ ] PENDING |
| **No security headers** (no CSP, X-Frame-Options, X-Content-Type-Options) | `web/app.py` | No defense-in-depth against XSS, clickjacking, MIME confusion | Add security headers middleware | [ ] PENDING |
| **Global shared session** — all users see same conversation | `web/app.py:53` SessionState | Data leakage between users; one reset wipes everyone | Per-user session isolation (session ID) | [ ] PENDING |
| **Conversation history corrupted** on API failure — user message stays with no assistant reply | `agent.py` chat() | All subsequent LLM calls receive broken context | Only append user message after successful API call | [ ] PENDING |
| **Timestamp key leaked** into Ollama API messages | `agent.py` chat() | Non-standard keys may break with Ollama updates | Strip `timestamp` before sending to API | [ ] PENDING |
| **CORS: `allow_origins=["*"]` + `allow_credentials=True`** | `web/app.py:36-42` | Any website can make cross-origin requests | Restrict to localhost origins, remove wildcard+credentials | [ ] PENDING |
| **No input validation** — negative salaries, NaN, megabyte messages accepted | `web/app.py`, services/ | Nonsensical financial outputs; DoS vector | Add Pydantic constraints (positive numbers, max length) | [ ] PENDING |

### HIGH - Fix Before Production

| Issue | File | Impact | Required Fix | Status |
| :--- | :--- | :--- | :--- | :--- |
| **No authentication** | `web/app.py` | Anyone who reaches server has full access | Add API key auth (configurable in config.ini) | [ ] PENDING |
| **Zero test coverage** (no `tests/` directory) | project root | Financial calculations are untested liabilities | Create pytest suite starting with tax + budget | [ ] PENDING |
| **No logging** — only `print()` statements | all files | Zero observability in production | Replace all `print()` with `logging` module | [ ] PENDING |
| **`/api/history` always returns `[]`** | `web/app.py` | History endpoint reads from empty `session.messages` | Read from agent's `conversation_history` | [ ] PENDING |
| **Toast XSS** — server error messages interpolated into innerHTML | `web/index.html` toast() | Server errors with HTML execute as scripts | Escape toast message content | [ ] PENDING |
| **CDN scripts without SRI hashes** | `web/index.html` | Compromised CDN bypasses XSS defense | Add `integrity` + `crossorigin` attributes | [ ] PENDING |
| **Error responses expose internals** | `web/app.py` lines 151,189,200,222 | File paths, connection details leaked to client | Return generic errors, log details server-side | [ ] PENDING |

### MEDIUM - Fix Within Development Cycle

| Issue | File | Impact | Required Fix | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Tax bracket gaps** at float boundaries (e.g., 24000.50 falls through) | `config/constants.py` | Fractional salary amounts untaxed at bracket edges | Use `>=`/`<` instead of integer boundaries | [ ] PENDING |
| **Unknown `risk_tolerance` silently defaults to aggressive** | `services/investment.py` | Typos produce dangerous aggressive recommendations | Validate against enum, reject unknown values | [ ] PENDING |
| **Short timeline completely overrides risk profile** | `services/investment.py` | Aggressive investor gets same rec as conservative | Merge timeline constraints with risk profile | [ ] PENDING |
| **NSSF Tier II not implemented** | `services/tax.py` | Understates NSSF for earners above KES 36,000 | Implement Tier II contribution calculation | [ ] PENDING |
| **Dead model code** — `models/user.py` imported but never used | `models/user.py`, `agent.py` | Misleading codebase; `RiskTolerance` enum ignored | Wire into agent flow or remove | [ ] PENDING |
| **Unbounded conversation history** — no memory limit | `agent.py` | Quadratic token growth; OOM on long sessions | Add max message cap, context window pruning | [ ] PENDING |
| **Budget unit inconsistency** — savings_rate decimal vs expense_percentages whole numbers | `services/budget.py` | Confusing API for callers | Standardize to consistent unit (decimal or percentage) | [ ] PENDING |
| **`requirements.txt`** duplicates, unused deps, unpinned versions | `requirements.txt` | Silent breaking changes; bloated install | Pin versions, remove `python-dotenv`, `sse-starlette`, dupes | [ ] PENDING |
| **Monolithic `main()`** — 150-line function | `main.py` | Low testability and maintainability | Extract to `CLIHandler` class | [ ] PENDING |
| **`config.ini` tracked in git** despite gitignore | `.gitignore`, `config.ini` | Developer-specific values in repo | Remove from git tracking, enforce gitignore | [ ] PENDING |

### LOW - Schedule as Time Permits

| Issue | Impact | Action | Status |
| :--- | :--- | :--- | :--- |
| **Dead streaming code** in frontend | Unreachable `stream()` function | Remove or implement SSE backend | [ ] PENDING |
| **No insurance relief** in tax calculator | Missed KES 255/month relief | Add SHIF relief calculation | [ ] PENDING |
| **No compound growth** in emergency fund | Overstates monthly savings needed | Model interest on savings | [ ] PENDING |
| **Magic numbers** in budget.py | Readability | Move thresholds to constants | [ ] PENDING |
| **Type hinting** incomplete | DX/Stability | Standardize `Optional` and type hints | [ ] PENDING |

---

## Architecture Gaps (Cross-Cutting)

These are systemic gaps that affect the entire project, not individual files.

| Gap | Current State | Target State |
| :--- | :--- | :--- |
| **No persistence** | All state in-memory; restart clears history | SQLite for conversation history + user profiles |
| **No containerization** | Manual setup, no Docker | Dockerfile + docker-compose.yml |
| **No CI/CD** | No automated testing or deployment | GitHub Actions: lint + test + build |
| **No rate limiting** | Unlimited API requests | Middleware with configurable limits |
| **Models disconnected from flow** | `UserProfile` exists but never instantiated | Wire profile into agent + system prompt |
| **No health checks** | No Ollama connectivity monitoring | `/health` endpoint with dependency checks |

---

## User Experience & Interface (The "Polish" List)

### Implemented
- **Layout Fix**: `flex-shrink: 0` on sidebar prevents disappearing.
- **Interactivity**: Collapsible sidebar with `localStorage` persistence.
- **Navigation**: "Jump to Bottom" button for long conversations.
- **Accessibility**: ARIA labels, keyboard navigation, and contrast improvements.
- **Performance**: Message virtualization (max 50 visible) to prevent DOM lag.

### Planned Improvements
- [ ] **Backend Streaming**: Implement true server-sent events for "typing" effect.
- [ ] **Offline Support**: Service workers for basic offline access.
- [ ] **Theming**: Formal Light/Dark mode toggle.
- [ ] **i18n**: Support for Swahili and other local languages.
- [ ] **User Preferences**: Persistent settings for risk tolerance and goals.
- [ ] **Export Download**: `/api/export` should return downloadable file, not filesystem path.
- [ ] **iOS Zoom Fix**: Increase input font-size to 16px to prevent auto-zoom on focus.
- [ ] **Dark Mode FOUC**: Apply theme via `localStorage` before render, not on DOMContentLoaded.

---

## Feature Evolution (The "Growth" List)

- [ ] **Persistent Profiles**: Migrate from session-based memory to a database (SQLite/PostgreSQL) to remember users.
- [ ] **Real-time Market Data**: Integrate with NSE (Nairobi Securities Exchange) API for live stock/bond prices.
- [ ] **Multi-Agent Orchestration**: Separate the "Tax Specialist" from the "Investment Expert" using specialized sub-agents.
- [ ] **Export Formats**: Add PDF and CSV export options for financial reports.
- [ ] **Prompt Personalization**: Inject `UserProfile` into system prompt for tailored advice.
- [ ] **Conversation Context Management**: Smart context pruning to stay within model token limits.

---

## Archive Reference
The following files have been deprecated and moved to `.archive/`:
- `TODO_SECURITY.md`
- `TODO_SECURITY_FIXES.txt`
- `UI_IMPROVEMENTS.md`
- `IMPROVEMENTS_SUMMARY.md`
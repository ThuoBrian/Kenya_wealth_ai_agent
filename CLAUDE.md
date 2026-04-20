# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kenya Wealth & Finance Agent — an AI-powered financial advisor for the Kenyan market. It provides budgeting, investing, tax, and emergency-fund guidance via natural-language conversation, using locally-run LLMs through Ollama. All financial logic is Kenya-specific (PAYE tax brackets, SHIF/NSSF deductions, MPesa, SACCOs, NSE, M-Akiba).

## Running

```bash
# CLI (interactive REPL)
python main.py

# Web UI (FastAPI on localhost:8000)
./start_web.sh
# or: python -m uvicorn web.app:app --host 127.0.0.1 --port 8000 --reload
```

**Prerequisites:** Ollama must be running at `http://localhost:11434` with a pulled model (`ollama pull glm-5:cloud`). Python 3.10+ required.

**Setup:**
```bash
pip install -r requirements.txt
cp config.ini.example config.ini   # config.ini is gitignored
```

There is no test suite, linter, or formatter configured. `requirements.txt` has duplicate entries for `fastapi` and `uvicorn` and lists unused packages (`python-dotenv`, `sse-starlette`).

## Architecture

**Dual interface, single agent core.** Both `main.py` (CLI REPL) and `web/app.py` (FastAPI REST API) instantiate the same `KenyaWealthAgent` class from `agent.py`, which orchestrates LLM calls via `ollama.Client`.

```
main.py ──┐
           ├──> agent.py (KenyaWealthAgent) ──> ollama.Client
web/app.py ┘         │
                     ├── config/settings.py (singleton Config from config.ini + env vars)
                     ├── config/constants.py (PAYE brackets, investment options, Kenya benchmarks)
                     ├── prompts/system.py (LLM system prompt)
                     ├── services/tax.py, budget.py, investment.py, emergency.py
                     ├── models/user.py (FinancialGoal, RiskTolerance, UserProfile)
                     └── templates/html.py (HTML report generation from conversation history)
```

**Data flow:** User message → `agent.chat()` appends to `conversation_history` (in-memory list of dicts), sends full history + system prompt to Ollama, returns response. On exit (CLI) or export (web), `templates/html.py` renders the history as a styled, printable HTML page saved to `output/`.

**Configuration priority:** Environment variable > `config.ini` > hardcoded defaults. The `Config` class is lazily initialized as a global singleton via `get_config()`.

**Web UI** (`web/index.html`) is a self-contained SPA (~74KB) with inline CSS/JS. It uses CDN-loaded DOMPurify and marked.js. The server has a `/api/export` endpoint that triggers `save_html_report()`.

## Key Design Decisions

- **Session state is entirely in-memory** — restarting the process clears conversation history. No database or file persistence.
- **User content is `html.escape()`d** in HTML reports; LLM markdown content has raw HTML tags stripped via regex before markdown conversion (`templates/html.py:_HTML_TAG_RE`). This is a mitigation, not a full sanitizer.
- **Tax calculation** (`services/tax.py`) applies progressive PAYE brackets from `config/constants.py` then subtracts personal relief (KES 2,400/month). Deductions are computed separately — NSSF does not reduce taxable income.
- **The `models/user.py` enums and dataclass** (`FinancialGoal`, `RiskTolerance`, `UserProfile`) exist but are not wired into the agent chat flow. Investment and budget services accept raw parameters.

## Known Issues (from ROADMAP.md)

- XSS: LLM markdown sanitization is regex-based, not a full sanitizer
- No input validation on `agent.chat()`
- `main()` in `main.py` is monolithic — should be extracted to a `CLIHandler` class
- `requirements.txt` has duplicate entries and unused dependencies
# Kenya Wealth & Finance Agent

An AI-powered financial advisor specifically engineered for the Kenyan market.
It provides personalized, context-aware guidance on budgeting, saving, investing,
and tax planning, integrating local financial instruments and regulatory
frameworks.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)

---

## 🎯 Core Value Proposition

Most financial AI models provide generic Western advice. The **Kenya Wealth Agent**
is "Kenya-Aware," meaning it understands:

- **Mobile Money Ecosystem**: MPesa, M-Shwari, Fuliza, and KCB MPesa.
- **Community Finance**: SACCO structures, dividends, and Chama dynamics.
- **Government Securities**: Treasury Bills, M-Akiba bonds, and the DhowCSD platform.
- **Local Tax Laws**: Current PAYE brackets, SHIF, NSSF, and the Housing Levy.
- **Market Context**: NSE (Nairobi Securities Exchange) equities and Kenyan
  real estate hotspots.

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🎯 Budget Analysis** | Personalized spending plans using a Kenyan-adapted 50/30/20 rule. |
| **📈 Investment Roadmap** | Risk-tiered advice ranging from MMFs to NSE stocks and land banking. |
| **📊 Tax Calculator** | Precise calculations for PAYE, SHIF, NSSF, and Housing Levy. |
| **🛡️ Emergency Planning** | Dynamic targets for 6-month emergency funds based on local costs. |
| **💬 Conversational AI** | Natural language interface powered by local LLMs via Ollama with streaming responses. |
| **📄 Session Reporting** | Export a styled HTML financial report at any time. |

## 🚀 Quick Start

### 1. Prerequisites

- Install [Ollama](https://ollama.ai)
- Python 3.10+

### 2. Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/kenya-wealth-agent.git
cd kenya-wealth-agent

# Install the package and development dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Pull a recommended model
ollama pull nemotron-3-super:cloud
```

### 3. Execution

```bash
# Start the web interface
./start_web.sh

# Or use the CLI
kenya-wealth-agent web --host 127.0.0.1 --port 8000
kenya-wealth-agent chat
kenya-wealth-agent tax --gross-salary 100000
kenya-wealth-agent budget --income 200000 --expenses '{"rent": 50000}'
```

Open the web UI at [http://localhost:8000](http://localhost:8000).

## ⚙️ Configuration

Customize the agent via `config.ini` or environment variables prefixed with
`KWA_`:

```ini
[ollama]
model = nemotron-3-super:cloud
base_url = http://localhost:11434

[agent]
developer_name = Brian Thuo

[output]
output_dir = output
report_filename = kenya_wealth_advice.html
```

Environment variables override `config.ini`, e.g. `KWA_MODEL=llama3.1`.

## 🏗 Architecture

The project follows **Clean Architecture / Ports & Adapters** so that business
logic, infrastructure, and interface concerns are separated:

```
src/kenya_wealth_agent/
├── domain/          # Pure business logic and Pydantic models
├── application/   # Orchestration services and ports (protocols)
├── adapters/        # Concrete implementations: Ollama, in-memory sessions, HTML reports
├── infrastructure/  # Cross-cutting concerns such as logging
└── interfaces/      # HTTP (FastAPI) and CLI adapters
```

Key design decisions are recorded as Architecture Decision Records (ADRs) in
`docs/architecture/`.

## 🛠 Project Structure

- `src/kenya_wealth_agent/interfaces/web/app.py`: FastAPI application with SSE streaming chat.
- `src/kenya_wealth_agent/interfaces/cli/app.py`: CLI entry point (`kenya-wealth-agent`).
- `src/kenya_wealth_agent/adapters/llm/ollama_client.py`: Async Ollama LLM adapter.
- `src/kenya_wealth_agent/adapters/persistence/memory_session_repo.py`: Per-session in-memory history.
- `src/kenya_wealth_agent/adapters/rendering/html_report.py`: Sanitized HTML report renderer.
- `tests/`: Comprehensive pytest suite with 80%+ coverage.
- `.archive/legacy/`: Original monolithic modules preserved for reference.

## 🧪 Development

```bash
# Run all checks
make lint        # ruff check
make format      # ruff format --check
make type        # mypy src/kenya_wealth_agent
make test        # pytest
make test-cov    # pytest with coverage

# Run pre-commit hooks manually
make pre-commit
```

## 🔒 Security & Hardening

- **HTML sanitization**: Assistant markdown is rendered and sanitized with `nh3`
  using a strict allow-list; user content is escaped with `html.escape`.
- **Security headers**: The web app attaches `X-Content-Type-Options`,
  `X-Frame-Options`, `Referrer-Policy`, and `Permissions-Policy` to every
  response.
- **Rate limiting**: `slowapi` limits `/api/chat` to 10 requests per minute per IP
  and applies a default 60/minute global limit. Disable with
  `KWA_ENABLE_RATE_LIMITING=false`.
- **Input validation**: Pydantic validates all request bodies; chat messages are
  limited to 4,000 characters.
- **Safe errors**: Unhandled exceptions are logged server-side and a generic
  "Internal server error" is returned to clients.

## 🤝 Contributor Guide

1. Fork the repository and create a feature branch.
2. Install in editable mode with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```
3. Make changes following the Clean Architecture layers:
   - Pure calculations and models belong in `domain/`.
   - Orchestration and ports belong in `application/`.
   - Concrete I/O implementations belong in `adapters/`.
   - HTTP/CLI wiring belongs in `interfaces/`.
4. Ensure the quality gate passes before committing:
   ```bash
   ruff check .
   ruff format --check .
   mypy src/kenya_wealth_agent
   pytest -q
   ```
5. Write or update tests, especially for any new domain calculation.

## 🐳 Docker

Build and run locally with Docker:

```bash
docker build -t kenya-wealth-agent .
docker run -p 8000:8000 -e KWA_BASE_URL=http://host.docker.internal:11434 kenya-wealth-agent
```

Or use Docker Compose (assumes Ollama is reachable from the container):

```bash
docker compose up
```

## ⚠️ Disclaimer

This tool provides **educational information only**. It is not a licensed
financial advisor. Always consult with a certified professional (CPA, CFA)
before making significant investment decisions.

## 👤 Author

Developed by **Brian Thuo**

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

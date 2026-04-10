# 🇰🇪 Kenya Wealth & Finance Agent

An AI-powered financial advisor specifically engineered for the Kenyan market. This agent provides personalized, context-aware guidance on budgeting, saving, investing, and tax planning, integrating local financial instruments and regulatory frameworks.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)

---

## 🎯 Core Value Proposition
Most financial AI models provide generic Western advice. The **Kenya Wealth Agent** is "Kenya-Aware," meaning it understands:
- **Mobile Money Ecosystem**: MPesa, M-Shwari, Fuliza, and KCB MPesa.
- **Community Finance**: SACCO structures, dividends, and Chama dynamics.
- **Government Securities**: Treasury Bills, M-Akiba bonds, and the DhowCSD platform.
- **Local Tax Laws**: Current PAYE brackets, SHIF (NHIF), NSSF, and the Housing Levy.
- **Market Context**: NSE (Nairobi Securities Exchange) equities and Kenyan real estate hotspots.

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| **🎯 Budget Analysis** | Personalized spending plans using a Kenyan-adapted 50/30/20 rule. |
| **📈 Investment Roadmap** | Risk-tiered advice ranging from MMFs to NSE stocks and land banking. |
| **📊 Tax Calculator** | Precise calculations for PAYE, SHIF, NSSF, and Housing Levy. |
| **🛡️ Emergency Planning** | Dynamic targets for 6-month emergency funds based on local costs. |
| **💬 Conversational AI** | Natural language interface powered by local LLMs via Ollama. |
| **📄 Session Reporting** | Automatically generates a styled HTML financial report upon exit. |

## 🚀 Quick Start

### 1. Prerequisites
- Install [Ollama](https://ollama.ai)
- Python 3.10+

### 2. Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/kenya-wealth-agent.git
cd kenya-wealth-agent

# Install dependencies
pip install -r requirements.txt

# Pull the recommended model
ollama pull glm-5:cloud
```

### 3. Execution
```bash
# Run the interactive CLI
python main.py

# Or start the web interface
./start_web.sh
```

## ⚙️ Configuration
Customize the agent via `config.ini`:
```ini
[ollama]
model = glm-5:cloud              # Supported: llama3.1, mistral, qwen, nemotron
base_url = http://localhost:11434

[agent]
developer_name = Brian Thuo
```

## 🛠 Project Structure
- `main.py`: CLI Entry point.
- `agent.py`: LLM orchestration and conversation management.
- `services/`: Modular logic for Tax, Budget, Investment, and Emergency funds.
- `web/`: Flask-based web interface.
- `templates/`: HTML report generation logic.
- `ROADMAP.md`: Project health and future evolution tracker.

## ⚠️ Disclaimer
This tool provides **educational information only**. It is not a licensed financial advisor. Always consult with a certified professional (CPA, CFA) before making significant investment decisions.

## 👤 Author
Developed by **Brian Thuo**

## 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

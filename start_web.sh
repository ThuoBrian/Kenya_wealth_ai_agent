#!/bin/bash
# Kenya Wealth Agent - Web UI Launcher
# Starts the local web server for the interactive UI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         🇰🇪 KENYA WEALTH & FINANCE AGENT                 ║"
echo "║              Web UI - Local Server                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Creating one..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Always ensure requirements are up to date
echo "📦 Checking dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Check if Ollama is running
echo "🔍 Checking Ollama connectivity..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "⚠️  Warning: Ollama server is not responding at http://localhost:11434"
    echo "   Please run 'ollama serve' in another terminal for the agent to work."
    echo ""
else
    echo "✅ Ollama is online and reachable."
fi

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is already in use. Attempting to clear it..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

echo "📋 Starting web server..."
echo ""
echo "   🌐 Open your browser to: http://localhost:8000"
echo ""
echo "   💡 Quick Tips:"
echo "      - Press Ctrl+C to stop the server"
echo "      - The server runs locally - no internet required"
echo "      - Your conversation data stays on your machine"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo ""

# Start the server
exec python3 -m uvicorn web.app:app --host 127.0.0.1 --port 8000 --reload

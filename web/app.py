"""
Kenya Wealth Agent - Web Application

Local-first interactive web UI for the financial advisor.
Runs entirely on your machine - no external hosting required.
"""

import os
import sys
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import KenyaWealthAgent
from config import get_config

USER_INITIALS = os.getenv("USER_INITIALS", "BT")

# Initialize FastAPI app
app = FastAPI(
    title="Kenya Wealth Agent",
    description="Personal Financial Advisor for the Kenyan Market",
    version="1.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance (lazy initialized)
_agent: Optional[KenyaWealthAgent] = None

# Session state
class SessionState:
    def __init__(self):
        self.messages: List[Dict[str, str]] = []
        self.started_at: Optional[datetime] = None

session = SessionState()


def get_agent() -> KenyaWealthAgent:
    """Get or create the agent instance."""
    global _agent
    if _agent is None:
        config = get_config()
        _agent = KenyaWealthAgent(model=config.model, base_url=config.base_url)
    return _agent


# ============== API Models ==============

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    timestamp: str


class Message(BaseModel):
    role: str
    content: str
    timestamp: str


class ConversationHistory(BaseModel):
    messages: List[Message]
    started_at: Optional[str] = None


class BudgetRequest(BaseModel):
    income: float
    expenses: Dict[str, float]


class TaxRequest(BaseModel):
    gross_salary: float


# ============== Routes ==============

@app.get("/")
async def root():
    """Serve the main web interface."""
    return FileResponse(Path(__file__).parent / "index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@app.get("/api/status")
async def get_status():
    """Get current agent status."""
    try:
        agent = get_agent()
        # Test connection
        agent.client.list()
        return {
            "connected": True,
            "model": agent.model,
            "base_url": agent.base_url,
            "user_initials": USER_INITIALS
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get a response."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        agent = get_agent()

        # Initialize session if first message
        if session.started_at is None:
            session.started_at = datetime.now()

        # Get response from agent
        response = agent.chat(request.message)

        return ChatResponse(
            response=response,
            timestamp=datetime.now().strftime("%H:%M")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history", response_model=ConversationHistory)
async def get_history():
    """Get conversation history."""
    messages = [
        Message(
            role=msg["role"],
            content=msg["content"],
            timestamp=datetime.now().strftime("%H:%M")
        )
        for msg in session.messages
    ]
    return ConversationHistory(
        messages=messages,
        started_at=session.started_at.isoformat() if session.started_at else None
    )


@app.post("/api/reset")
async def reset_conversation():
    """Reset the conversation."""
    agent = get_agent()
    agent.reset_conversation()
    session.messages = []
    session.started_at = None
    return {"status": "ok", "message": "Conversation reset"}


@app.post("/api/budget")
async def analyze_budget(request: BudgetRequest):
    """Analyze budget and get recommendations."""
    try:
        agent = get_agent()
        result = agent.analyze_budget(request.income, request.expenses)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tax")
async def calculate_tax(request: TaxRequest):
    """Calculate PAYE tax."""
    try:
        agent = get_agent()
        result = agent.calculate_tax(request.gross_salary)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export")
async def export_conversation():
    """Export conversation as HTML."""
    try:
        agent = get_agent()
        from templates.html import save_html_report

        report_path = save_html_report(
            agent.get_conversation_history(),
            session.started_at
        )

        return {
            "status": "ok",
            "path": report_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Main Entry Point ==============

def main():
    """Run the web application."""
    import uvicorn

    print("\n" + "=" * 60)
    print("  🇰🇪 KENYA WEALTH & FINANCE AGENT - WEB UI")
    print("=" * 60)
    print("\n  Starting local server...")
    print("  Open your browser to: http://localhost:8000")
    print("\n  Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()

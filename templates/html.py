"""
HTML template generation for Kenya Wealth Agent.

This module handles generating HTML output files from
conversation history.
"""

import os
from datetime import datetime
from typing import List, Dict, Optional

import markdown

from config.settings import get_config


# ── Allowed HTML tags for DOMPurify-equivalent server-side safety ─────────────
_MD_EXTENSIONS = ["tables", "fenced_code", "nl2br", "sane_lists"]


def markdown_to_html(text: str) -> str:
    """Convert markdown text to safe HTML.

    Uses the `markdown` library with common extensions.
    Output is NOT further sanitized here — caller is responsible
    for ensuring `text` originates from the trusted AI response,
    not raw user input.

    Args:
        text: Markdown formatted text

    Returns:
        HTML formatted text
    """
    md = markdown.Markdown(extensions=_MD_EXTENSIONS)
    return md.convert(text)


def _format_duration(session_start: datetime, session_end: datetime) -> str:
    """Return a human-readable duration string."""
    total_seconds = max(0, int((session_end - session_start).total_seconds()))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    return f"{minutes}m {seconds}s"


def generate_conversation_html(
    conversation_history: List[Dict[str, str]],
    session_start: Optional[datetime] = None,
) -> str:
    """Generate HTML for conversation messages.

    Args:
        conversation_history: List of message dicts with 'role' and 'content'.
        session_start: Optional session start time (unused currently,
            reserved for per-message relative timestamps).

    Returns:
        HTML string for the conversation section.
    """
    parts: List[str] = []

    for i, msg in enumerate(conversation_history):
        role = msg.get("role", "")
        raw_content = msg.get("content", "")
        timestamp = datetime.now().strftime("%H:%M")

        if role == "user":
            # Escape user content — do NOT render as markdown to prevent injection
            safe_content = (
                raw_content
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br>")
            )
            parts.append(f"""
            <div class="msg-row user" id="msg-{i}">
              <div class="msg-body">
                <div class="msg-meta">
                  <span class="msg-label user-label">You</span>
                  <span class="msg-time">{timestamp}</span>
                </div>
                <div class="msg-content">{safe_content}</div>
              </div>
            </div>""")

        elif role == "assistant":
            content_html = markdown_to_html(raw_content)
            parts.append(f"""
            <div class="msg-row assistant" id="msg-{i}">
              <div class="msg-avatar" aria-hidden="true">KW</div>
              <div class="msg-body">
                <div class="msg-meta">
                  <span class="msg-label ai-label">Financial Advisor</span>
                  <span class="msg-time">{timestamp}</span>
                </div>
                <div class="msg-content">{content_html}</div>
                <div class="disclaimer" role="note">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
                    stroke="#d97706" stroke-width="2" stroke-linecap="round"
                    stroke-linejoin="round" aria-hidden="true">
                    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94
                             a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                  AI-generated guidance. Always verify with a licensed financial
                  advisor before making financial decisions.
                </div>
              </div>
            </div>""")

    return "\n".join(parts)


def generate_final_report(
    conversation_history: List[Dict[str, str]],
    session_start: Optional[datetime] = None,
) -> str:
    """Generate a final HTML report from conversation history.

    Creates a clean, print-friendly HTML page displaying the complete
    conversation between user and financial advisor.

    Args:
        conversation_history: List of message dicts with 'role' and 'content'.
        session_start: When the session started.

    Returns:
        Complete HTML string for the conversation report page.
    """
    config = get_config()
    developer_name = config.developer_name
    app_version = config.version

    if session_start is None:
        session_start = datetime.now()

    session_end = datetime.now()
    duration_str = _format_duration(session_start, session_end)

    total_messages = len(
        [m for m in conversation_history if m.get("role") in ("user", "assistant")]
    )
    user_messages = len([m for m in conversation_history if m.get("role") == "user"])
    ai_messages = len([m for m in conversation_history if m.get("role") == "assistant"])

    conversation_html = generate_conversation_html(conversation_history, session_start)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Kenya Wealth Agent — Session Report</title>
  <style>
    /* ── Reset & base ────────────────────────────────────────── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ font-size: 17px; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
                   'Helvetica Neue', Arial, sans-serif;
      background: #f8fafc;
      color: #1a1a2e;
      line-height: 1.7;
      padding: 32px 16px 64px;
    }}

    /* ── Layout ──────────────────────────────────────────────── */
    .page {{ max-width: 880px; margin: 0 auto; }}

    /* ── Header ──────────────────────────────────────────────── */
    .report-header {{
      background: #ffffff;
      border: 1px solid rgba(0,0,0,0.12);
      border-radius: 16px;
      padding: 28px 32px;
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      flex-wrap: wrap;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    .header-brand {{ display: flex; align-items: center; gap: 14px; }}
    .brand-mark {{
      width: 48px; height: 48px;
      background: linear-gradient(135deg, #00955a 0%, #007344 100%);
      border-radius: 12px;
      display: flex; align-items: center; justify-content: center;
    }}
    .brand-mark svg {{ width: 24px; height: 24px; }}
    .brand-name {{
      font-size: 1.2rem;
      font-weight: 600;
      color: #111827;
    }}
    .brand-sub {{
      font-size: 0.85rem;
      color: #4b5563;
      margin-top: 3px;
    }}
    .report-badge {{
      display: inline-flex; align-items: center; gap: 7px;
      padding: 7px 14px;
      background: #e8f5ee;
      border-radius: 999px;
      font-size: 0.82rem;
      font-weight: 500;
      color: #1a5c38;
    }}
    .report-badge svg {{ width: 13px; height: 13px; }}

    /* ── Stats ───────────────────────────────────────────────── */
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 14px;
      margin-bottom: 28px;
    }}
    .stat {{
      background: #ffffff;
      border: 1px solid rgba(0,0,0,0.12);
      border-radius: 12px;
      padding: 18px 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    .stat-value {{
      font-size: 1.4rem;
      font-weight: 600;
      color: #111827;
      margin-bottom: 4px;
    }}
    .stat-label {{
      font-size: 0.78rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.07em;
      color: #6b7280;
    }}

    /* ── Conversation ────────────────────────────────────────── */
    .conversation {{ display: flex; flex-direction: column; gap: 18px; }}

    .msg-row {{
      display: flex;
      gap: 12px;
      align-items: flex-start;
    }}
    .msg-row.user {{ flex-direction: row-reverse; }}

    .msg-avatar {{
      width: 36px; height: 36px; border-radius: 50%;
      background: #e8f5ee;
      color: #1a5c38;
      display: flex; align-items: center; justify-content: center;
      font-size: 12px; font-weight: 600;
      flex-shrink: 0;
      margin-top: 2px;
    }}

    .msg-body {{
      max-width: min(76%, 660px);
      display: flex;
      flex-direction: column;
      gap: 5px;
    }}
    .msg-row.user .msg-body {{ align-items: flex-end; }}

    .msg-meta {{
      display: flex; align-items: center; gap: 10px;
      flex-wrap: wrap;
    }}
    .msg-row.user .msg-meta {{ flex-direction: row-reverse; }}

    .msg-label {{
      font-size: 0.76rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}
    .user-label {{ color: #1d4ed8; }}
    .ai-label   {{ color: #1a5c38; }}

    .msg-time {{
      font-size: 0.74rem;
      color: #6b7280;
      font-weight: 500;
    }}

    .msg-content {{
      background: #ffffff;
      border: 1.5px solid rgba(0,0,0,0.12);
      border-radius: 16px;
      padding: 14px 18px;
      font-size: 0.95rem;
      line-height: 1.8;
      color: #1f2937;
      word-wrap: break-word;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .msg-row.user .msg-content {{
      background: linear-gradient(135deg, #00955a 0%, #007a4d 100%);
      color: #ffffff;
      border-color: transparent;
      border-bottom-right-radius: 4px;
    }}
    .msg-row.assistant .msg-content {{
      border-bottom-left-radius: 4px;
    }}

    /* markdown content inside assistant bubbles */
    .msg-content p           {{ margin-bottom: 0.65em; }}
    .msg-content p:last-child{{ margin-bottom: 0; }}
    .msg-content strong      {{ font-weight: 600; }}
    .msg-content h2, .msg-content h3, .msg-content h4 {{
      margin: 0.85em 0 0.4em;
      font-weight: 600;
      color: #111827;
    }}
    .msg-content h2 {{ font-size: 1.15em; }}
    .msg-content h3 {{
      font-size: 1em;
      border-bottom: 1px solid rgba(0,0,0,0.1);
      padding-bottom: 0.25em;
    }}
    .msg-content ul, .msg-content ol {{
      margin: 0.5em 0; padding-left: 1.5em;
    }}
    .msg-content li {{ margin: 0.25em 0; }}
    .msg-content table {{
      width: 100%; border-collapse: collapse;
      margin: 0.8em 0; font-size: 0.9em;
      border-radius: 8px; overflow: hidden;
    }}
    .msg-content th, .msg-content td {{
      padding: 10px 14px;
      border: 1px solid rgba(0,0,0,0.1);
      text-align: left;
    }}
    .msg-content th {{
      background: #007344;
      color: #ffffff;
      font-weight: 600;
    }}
    .msg-content tr:nth-child(even) td {{ background: #f9fafb; }}
    .msg-content code {{
      background: rgba(0,0,0,0.07);
      padding: 2px 6px; border-radius: 4px;
      font-size: 0.88em; font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
      color: #be185d;
    }}
    .msg-content pre {{
      background: #1e293b; color: #e2e8f0;
      padding: 14px 16px; border-radius: 8px;
      overflow-x: auto; margin: 0.7em 0; font-size: 0.88em;
      border: 1px solid rgba(0,0,0,0.15);
    }}
    .msg-content pre code {{ background: none; color: inherit; padding: 0; }}
    .msg-content blockquote {{
      border-left: 4px solid #00955a;
      padding: 0.5em 1em;
      background: #e8f5ee;
      border-radius: 0 8px 8px 0;
      margin: 0.7em 0;
      color: #1a5c38;
    }}
    .msg-content hr {{
      border: none; border-top: 1px solid rgba(0,0,0,0.1);
      margin: 1.2em 0;
    }}
    .msg-content a {{ color: #00955a; text-decoration: underline; }}

    /* ── Disclaimer ──────────────────────────────────────────── */
    .disclaimer {{
      display: flex; align-items: flex-start; gap: 8px;
      padding: 10px 14px;
      background: #fffbeb;
      border: 1.5px solid #d97706;
      border-radius: 10px;
      font-size: 0.82rem;
      line-height: 1.5;
      color: #78350f;
      margin-top: 6px;
      max-width: min(76%, 660px);
    }}
    .disclaimer svg {{ flex-shrink: 0; margin-top: 2px; }}

    /* ── Footer ──────────────────────────────────────────────── */
    .report-footer {{
      margin-top: 48px;
      padding-top: 28px;
      border-top: 1px solid rgba(0,0,0,0.1);
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      flex-wrap: wrap;
      gap: 16px;
    }}
    .footer-left {{ font-size: 0.85rem; color: #4b5563; }}
    .footer-left strong {{ color: #111827; }}
    .footer-right {{ font-size: 0.8rem; color: #6b7280; text-align: right; }}

    /* ── Print ───────────────────────────────────────────────── */
    @media print {{
      body {{ background: #fff; padding: 0; }}
      .report-header, .stat, .msg-content {{ box-shadow: none; }}
      .msg-row.user .msg-content {{
        background: #e8f5ee !important;
        color: #111827 !important;
        -webkit-print-color-adjust: exact;
      }}
    }}

    /* ── Responsive ──────────────────────────────────────────── */
    @media (max-width: 600px) {{
      .report-header {{ padding: 22px 18px; }}
      .msg-body {{ max-width: 92%; }}
      .disclaimer {{ max-width: 92%; }}
      body {{ padding: 16px 12px 48px; }}
    }}

    /* ── Dark Mode Support ───────────────────────────────────── */
    @media (prefers-color-scheme: dark) {{
      body {{
        background: #0f1419;
        color: #f0f2f5;
      }}
      .report-header, .stat, .msg-content {{
        background: #1a2027;
        border-color: rgba(255,255,255,0.12);
      }}
      .brand-name, .stat-value {{
        color: #f0f2f5;
      }}
      .brand-sub, .stat-label, .msg-time, .footer-right {{
        color: #9ca3af;
      }}
      .footer-left {{
        color: #9ca3af;
      }}
      .footer-left strong {{
        color: #f0f2f5;
      }}
      .msg-content {{
        color: #e5e7eb;
      }}
      .msg-content h2, .msg-content h3, .msg-content h4 {{
        color: #f0f2f5;
      }}
      .msg-content h3 {{
        border-color: rgba(255,255,255,0.15);
      }}
      .msg-content th {{
        background: #007344;
      }}
      .msg-content tr:nth-child(even) td {{
        background: #252d38;
      }}
      .msg-content code {{
        background: rgba(255,255,255,0.1);
      }}
      .msg-content pre {{
        background: #0d1117;
        border-color: rgba(255,255,255,0.15);
      }}
      .msg-content blockquote {{
        background: #1a3d2e;
      }}
      .msg-content hr {{
        border-color: rgba(255,255,255,0.15);
      }}
      .disclaimer {{
        background: #3d2f1a;
        border-color: #d97706;
      }}
      .report-footer {{
        border-color: rgba(255,255,255,0.1);
      }}
    }}
  </style>
</head>
<body>
  <div class="page">

    <!-- Header -->
    <header class="report-header">
      <div class="header-brand">
        <div class="brand-mark">
          <svg viewBox="0 0 24 24" fill="none" stroke="#fff"
            stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 17l4-8 4 5 3-3 4 6"/>
          </svg>
        </div>
        <div>
          <div class="brand-name">Kenya Wealth Agent</div>
          <div class="brand-sub">Financial Advice Session Report</div>
        </div>
      </div>
      <div class="report-badge">
        <svg viewBox="0 0 24 24" fill="none" stroke="#1a5c38"
          stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
        </svg>
        Session export
      </div>
    </header>

    <!-- Stats -->
    <div class="stats" role="region" aria-label="Session statistics">
      <div class="stat">
        <div class="stat-value">{session_start.strftime('%d %b %Y')}</div>
        <div class="stat-label">Session date</div>
      </div>
      <div class="stat">
        <div class="stat-value">{session_start.strftime('%H:%M')}</div>
        <div class="stat-label">Start time</div>
      </div>
      <div class="stat">
        <div class="stat-value">{duration_str}</div>
        <div class="stat-label">Duration</div>
      </div>
      <div class="stat">
        <div class="stat-value">{total_messages}</div>
        <div class="stat-label">Total messages</div>
      </div>
      <div class="stat">
        <div class="stat-value">{user_messages} / {ai_messages}</div>
        <div class="stat-label">Questions / answers</div>
      </div>
    </div>

    <!-- Conversation -->
    <main class="conversation" role="main" aria-label="Conversation transcript">
      {conversation_html}
    </main>

    <!-- Footer -->
    <footer class="report-footer">
      <div class="footer-left">
        Engineered by <strong>{developer_name}</strong> ·
        Kenya Wealth Agent v{app_version}
      </div>
      <div class="footer-right">
        {session_end.strftime('%d %b %Y at %H:%M:%S')}
      </div>
    </footer>

  </div>
</body>
</html>"""


def save_html_report(
    conversation_history: List[Dict[str, str]],
    session_start: Optional[datetime] = None,
    output_path: Optional[str] = None,
) -> str:
    """Generate and save HTML report to file.

    Args:
        conversation_history: List of message dicts with 'role' and 'content'.
        session_start: When the session started.
        output_path: Custom output path (defaults to config output_dir).

    Returns:
        Absolute path to the saved HTML file.
    """
    config = get_config()

    if session_start is None:
        session_start = datetime.now()

    html_content = generate_final_report(conversation_history, session_start)

    if output_path is None:
        output_dir = config.output_dir
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, config.report_filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return os.path.abspath(output_path)


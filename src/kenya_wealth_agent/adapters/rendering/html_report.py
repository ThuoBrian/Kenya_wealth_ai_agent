"""HTML report renderer for Kenya Wealth Agent.

Renders a conversation history into a styled, print-friendly HTML report.
Security choices:
- User content is escaped with ``html.escape`` and never interpreted as markdown.
- Assistant markdown is rendered to HTML and then sanitized with ``nh3`` using a
  strict allow-list of tags and attributes.
"""

import html
import re
from datetime import datetime
from importlib.resources import files

import markdown
import nh3
import structlog

from kenya_wealth_agent.application.ports import ReportRenderer
from kenya_wealth_agent.config.settings import get_settings

logger = structlog.get_logger()

# Allowed markdown extensions.  We intentionally keep the set small to reduce
# the attack surface of the markdown renderer before nh3 runs.
_MD_EXTENSIONS = ["tables", "fenced_code", "nl2br", "sane_lists"]

# Tags and attributes allowed through nh3 for assistant markdown content.
_ALLOWED_TAGS = {
    "p",
    "br",
    "strong",
    "em",
    "b",
    "i",
    "u",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "a",
    "blockquote",
    "code",
    "pre",
    "hr",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
}
_ALLOWED_ATTRIBUTES: dict[str, set[str]] = {"a": {"href", "title"}}

_HTML_TAG_RE = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?>", re.DOTALL)


def _parse_timestamp(msg: dict[str, str]) -> str:
    """Return a formatted HH:MM string for a message."""
    raw = msg.get("timestamp", "")
    if raw:
        try:
            return datetime.fromisoformat(raw).strftime("%H:%M")
        except (ValueError, TypeError):
            pass
    return datetime.now().strftime("%H:%M")


def _markdown_to_html(text: str) -> str:
    """Convert markdown text to safe HTML.

    Raw HTML tags in the LLM output are escaped before markdown rendering so
    that the markdown library cannot pass through injected tags.  The rendered
    HTML is then sanitized by ``nh3``.
    """
    safe_text = _HTML_TAG_RE.sub(lambda m: html.escape(m.group(0)), text)
    md = markdown.Markdown(extensions=_MD_EXTENSIONS)  # type: ignore[no-untyped-call]
    rendered = md.convert(safe_text)
    return nh3.clean(
        rendered,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        url_schemes={"http", "https", "mailto"},
    )


def _format_duration(session_start: datetime, session_end: datetime) -> str:
    """Return a human-readable duration string."""
    total_seconds = max(0, int((session_end - session_start).total_seconds()))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    return f"{minutes}m {seconds}s"


def _load_css() -> str:
    """Load the embedded stylesheet."""
    css_path = files("kenya_wealth_agent.adapters.rendering.static") / "report.css"
    return css_path.read_text(encoding="utf-8")


def _render_conversation(messages: list[dict[str, str]]) -> str:
    """Render the conversation body HTML."""
    copy_icon = (
        '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"'
        ' stroke="currentColor" stroke-width="2" stroke-linecap="round"'
        ' stroke-linejoin="round" aria-hidden="true">'
        '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>'
        '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'
        "</svg>"
    )

    parts: list[str] = []
    for i, msg in enumerate(messages):
        role = msg.get("role", "")
        raw_content = msg.get("content", "")
        timestamp = _parse_timestamp(msg)

        if role == "user":
            safe_content = html.escape(raw_content).replace("\n", "<br>")
            parts.append(f"""
            <div class="msg-row user" id="msg-{i}">
              <div class="msg-avatar" aria-hidden="true">You</div>
              <div class="msg-body">
                <div class="msg-meta">
                  <span class="msg-label user-label">You</span>
                  <span class="msg-time">{timestamp}</span>
                  <button class="copy-btn" aria-label="Copy message"
                    onclick="copyMsg(this)">{copy_icon}</button>
                </div>
                <div class="msg-content">{safe_content}</div>
              </div>
            </div>""")
        elif role == "assistant":
            content_html = _markdown_to_html(raw_content)
            parts.append(f"""
            <div class="msg-row assistant" id="msg-{i}">
              <div class="msg-avatar" aria-hidden="true">KW</div>
              <div class="msg-body">
                <div class="msg-meta">
                  <span class="msg-label ai-label">Financial Advisor</span>
                  <span class="msg-time">{timestamp}</span>
                  <button class="copy-btn" aria-label="Copy message"
                    onclick="copyMsg(this)">{copy_icon}</button>
                </div>
                <div class="msg-content">{content_html}</div>
              </div>
            </div>""")

    return "\n".join(parts)


def _derive_title(messages: list[dict[str, str]]) -> str:
    """Use the first user message (truncated) as the session title."""
    first_user = next(
        (m.get("content", "") for m in messages if m.get("role") == "user"),
        None,
    )
    if first_user:
        raw_title = first_user[:60].strip()
        suffix = "..." if len(first_user) > 60 else ""
        return html.escape(raw_title + suffix)
    return "Financial Advice Session"


class HTMLReportRenderer(ReportRenderer):
    """Render a conversation history as a styled HTML report."""

    def __init__(self, css_override: str | None = None):
        """Initialize the renderer.

        Args:
            css_override: Optional custom CSS to embed instead of the default.
        """
        self.css = css_override or _load_css()

    def render(
        self,
        messages: list[dict[str, str]],
        session_start: datetime | None = None,
    ) -> str:
        """Render the report.

        Args:
            messages: Conversation history with ``role`` and ``content`` keys.
            session_start: Optional session start time for metadata.

        Returns:
            Complete HTML document as a string.
        """
        settings = get_settings()
        developer_name = html.escape(settings.developer_name)
        app_version = html.escape(settings.version)
        model_display = html.escape(settings.model)

        session_title = _derive_title(messages)
        now = datetime.now()
        start = session_start or now
        duration_str = _format_duration(start, now)

        total_messages = sum(1 for m in messages if m.get("role") in ("user", "assistant"))
        user_messages = sum(1 for m in messages if m.get("role") == "user")
        ai_messages = total_messages - user_messages

        conversation_html = _render_conversation(messages)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{session_title} — Kenya Wealth Agent</title>
  <style>
{self.css}
  </style>
</head>
<body>
  <div class="page">
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
      <div class="header-actions">
        <div class="report-badge">
          <svg viewBox="0 0 24 24" fill="none" stroke="#1a5c38"
            stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          Session export
        </div>
        <button class="print-btn" onclick="window.print()" aria-label="Print or save as PDF">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" stroke-width="2" stroke-linecap="round"
            stroke-linejoin="round" aria-hidden="true">
            <polyline points="6 9 6 2 18 2 18 9"/>
            <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/>
            <rect x="6" y="14" width="12" height="8"/>
          </svg>
          Print / PDF
        </button>
      </div>
    </header>

    <p class="session-title">{session_title}</p>

    <div class="stats" role="region" aria-label="Session statistics">
      <div class="stat">
        <div class="stat-value">{start.strftime("%d %b %Y")}</div>
        <div class="stat-label">Session date</div>
      </div>
      <div class="stat">
        <div class="stat-value">{start.strftime("%H:%M")}</div>
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
      <div class="stat">
        <div class="stat-value model-stat-value">{model_display}</div>
        <div class="stat-label">AI model</div>
      </div>
    </div>

    <div class="disclaimer-banner" role="note">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none"
        stroke="#d97706" stroke-width="2" stroke-linecap="round"
        stroke-linejoin="round" aria-hidden="true">
        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
      <span>AI-generated guidance. Always verify with a licensed financial advisor
        before making financial decisions.</span>
    </div>

    <main class="conversation" role="main" aria-label="Conversation transcript">
      {conversation_html}
    </main>

    <footer class="report-footer">
      <div class="footer-left">
        Engineered by <strong>{developer_name}</strong> ·
        Kenya Wealth Agent v{app_version}
      </div>
      <div class="footer-right">
        {now.strftime("%d %b %Y at %H:%M:%S")}
      </div>
    </footer>
  </div>

  <button id="back-to-top" aria-label="Back to top"
    onclick="window.scrollTo({{top:0,behavior:'smooth'}})">
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" stroke-width="2.5" stroke-linecap="round"
      stroke-linejoin="round" aria-hidden="true">
      <polyline points="18 15 12 9 6 15"/>
    </svg>
  </button>

  <script>
    function copyMsg(btn) {{
      var content = btn.closest('.msg-body').querySelector('.msg-content');
      navigator.clipboard.writeText(content.innerText).then(function() {{
        btn.setAttribute('data-copied', '');
        setTimeout(function() {{ btn.removeAttribute('data-copied'); }}, 2000);
      }});
    }}

    var _btt = document.getElementById('back-to-top');
    window.addEventListener('scroll', function() {{
      _btt.classList.toggle('visible', window.scrollY > 300);
    }});
  </script>
</body>
</html>"""

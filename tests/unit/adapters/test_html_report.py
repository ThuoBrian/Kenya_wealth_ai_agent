"""Tests for the HTML report renderer."""

from kenya_wealth_agent.adapters.rendering.html_report import HTMLReportRenderer


def test_render_basic_report():
    renderer = HTMLReportRenderer()
    html = renderer.render([{"role": "user", "content": "Hello"}])
    assert "<!DOCTYPE html>" in html
    assert "Kenya Wealth Agent" in html
    assert "Hello" in html


def test_user_script_is_escaped():
    renderer = HTMLReportRenderer()
    malicious = "<script>alert('xss')</script>"
    html = renderer.render([{"role": "user", "content": malicious}])
    # The malicious payload must be escaped, not executed.
    assert "alert('xss')" not in html
    assert "&lt;script&gt;" in html


def test_assistant_markdown_is_sanitized():
    renderer = HTMLReportRenderer()
    malicious = "Hello <script>alert('xss')</script> **bold**"
    html = renderer.render([{"role": "assistant", "content": malicious}])
    # The literal malicious tag must not survive as HTML; markdown bold should render.
    assert "<script>alert('xss')</script>" not in html
    assert "<strong>bold</strong>" in html


def test_title_from_first_user_message():
    renderer = HTMLReportRenderer()
    html = renderer.render([{"role": "user", "content": "How do I budget?"}])
    assert "How do I budget?" in html

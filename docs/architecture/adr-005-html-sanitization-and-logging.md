# ADR-005: HTML Sanitization and Structured Logging

## Status

Accepted

## Context

The assistant generates markdown that is rendered in the browser. User messages
are also displayed. Both need to be safe from XSS and injection. At the same time,
the application needs consistent, queryable logs for local debugging and future
operational visibility.

## Decision

- Use `nh3` with a strict allow-list to sanitize rendered assistant markdown.
- Escape user content with `html.escape` before embedding it in the HTML report.
- Use `structlog` with a console renderer in development and a JSON-ready
  processor chain so the same configuration can support future aggregation.

## Consequences

- Malicious payloads such as `<script>` tags are neutralized before reaching
  the browser.
- Logging is structured and consistent across the domain, adapters, and
  interfaces.

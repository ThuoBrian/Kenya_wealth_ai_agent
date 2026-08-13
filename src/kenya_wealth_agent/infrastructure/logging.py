"""Structured logging configuration for Kenya Wealth Agent."""

import logging
import sys

import structlog


def configure_logging(log_level: str = "INFO", structured: bool = True) -> None:
    """Configure the application's logging.

    When ``structured`` is True, both the standard library ``logging`` and
    ``structlog`` emit JSON-ish key/value logs suitable for local development and
    future log aggregation.  When False, plain text logs are emitted.

    Args:
        log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        structured: Whether to enable structlog processors.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    if structured:
        shared_processors: list[structlog.types.Processor] = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ExtraAdder(),
        ]

        structlog.configure(
            processors=[
                *shared_processors,
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            cache_logger_on_first_use=True,
        )

        formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processor=structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty()),
        )
    else:
        logging.basicConfig(
            level=level,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        return

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Quiet down noisy third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

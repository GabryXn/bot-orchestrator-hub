
import logging
import sys
import structlog
from src.core.config import LOG_LEVEL

def configure_logging() -> None:
    """Configure structlog for JSON structured logging."""
    # Determine if we're in production (Cloud Run sets this)
    is_production = "K_SERVICE" in __import__("os").environ

    # Configure processors
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if is_production:
        # JSON output for Cloud Run logs
        shared_processors.append(structlog.processors.JSONRenderer())
    else:
        # Pretty console output for development
        shared_processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, LOG_LEVEL, logging.INFO),
    )

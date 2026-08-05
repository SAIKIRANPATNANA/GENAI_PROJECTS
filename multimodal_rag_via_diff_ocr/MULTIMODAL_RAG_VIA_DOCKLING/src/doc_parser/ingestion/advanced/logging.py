"""Structured logging with structlog and Prefect integration."""

import structlog
from structlog.processors import JSONRenderer, TimeStamper, add_log_level


structlog.configure(
    processors=[
        add_log_level,
        TimeStamper(fmt="iso"),
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


def get_logger(name: str):
    """Return a structured logger instance."""
    return structlog.get_logger(name)

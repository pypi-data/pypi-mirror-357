"""
Configuration utilities for setting up logging with the Cobli JSON formatter.
"""

import os
import logging
from typing import Optional

from .formatter import JsonFormatter


def configure_logging(
    service_name: Optional[str] = None,
    version: Optional[str] = None,
    log_level: Optional[str] = None,
    logger_name: Optional[str] = None,
    propagate: bool = False,
    handler: Optional[logging.Handler] = None,
) -> logging.Logger:
    """
    Configure a logger with the Cobli JSON formatter.

    Args:
        service_name: Service name (defaults to DD_SERVICE env var)
        version: Service version (defaults to DD_VERSION env var)
        log_level: Logging level (defaults to LOG_LEVEL env var or "INFO")
        logger_name: Logger name (defaults to service_name or DD_SERVICE)
        propagate: Whether to propagate to parent loggers
        handler: Custom handler (defaults to StreamHandler)

    Returns:
        Configured logger instance
    """
    # Determine service name and logger name
    effective_service_name = service_name or os.environ.get("DD_SERVICE")
    effective_logger_name = logger_name or effective_service_name

    # Get or create logger
    logger = logging.getLogger(effective_logger_name)

    # Determine log level
    effective_log_level = (log_level or os.environ.get("LOG_LEVEL", "INFO")).upper()
    logger.setLevel(effective_log_level)

    # Remove any existing handlers to avoid duplicates
    for existing_handler in list(logger.handlers):
        logger.removeHandler(existing_handler)

    # Create and configure handler
    if handler is None:
        handler = logging.StreamHandler()

    handler.setLevel(effective_log_level)
    handler.setFormatter(
        JsonFormatter(service_name=effective_service_name, version=version)
    )

    # Add handler to logger
    logger.addHandler(handler)

    # Set propagation behavior
    # Prevent propagation if this is a named logger to avoid duplicate logs
    if logger.name != "root":
        logger.propagate = propagate

    return logger


def get_logger(
    service_name: Optional[str] = None,
    version: Optional[str] = None,
    log_level: Optional[str] = None,
    logger_name: Optional[str] = None,
) -> logging.Logger:
    """
    Get a pre-configured logger with the Cobli JSON formatter.

    This is a convenience function that calls configure_logging with sensible defaults.

    Args:
        service_name: Service name (defaults to DD_SERVICE env var)
        version: Service version (defaults to DD_VERSION env var)
        log_level: Logging level (defaults to LOG_LEVEL env var or "INFO")
        logger_name: Logger name (defaults to service_name or DD_SERVICE)

    Returns:
        Configured logger instance
    """
    return configure_logging(
        service_name=service_name,
        version=version,
        log_level=log_level,
        logger_name=logger_name,
        propagate=False,
    )


def get_formatter(
    service_name: Optional[str] = None, version: Optional[str] = None
) -> JsonFormatter:
    """
    Get a JsonFormatter instance.

    Args:
        service_name: Service name (defaults to DD_SERVICE env var)
        version: Service version (defaults to DD_VERSION env var)

    Returns:
        JsonFormatter instance
    """
    return JsonFormatter(service_name=service_name, version=version)

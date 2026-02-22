"""Logging configuration and utilities for the application."""

import logging
import sys
from typing import Any

from app.core.config import settings

# Sensitive fields that should be masked in logs
SENSITIVE_FIELDS = {
    "password",
    "hashed_password",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "api_key",
    "authorization",
    "cookie",
    "session",
    "csrf_token",
    "new_password",
    "current_password",
    "confirm_password",
}


def mask_sensitive_data(data: Any, depth: int = 0, max_depth: int = 5) -> Any:
    """
    Recursively mask sensitive data in dictionaries, lists, and objects.

    Args:
        data: The data to mask
        depth: Current recursion depth
        max_depth: Maximum recursion depth to prevent infinite loops

    Returns:
        Data with sensitive fields masked
    """
    if depth > max_depth:
        return "[MAX_DEPTH_REACHED]"

    if isinstance(data, dict):
        return {
            key: "***MASKED***"
            if key.lower() in SENSITIVE_FIELDS
            else mask_sensitive_data(value, depth + 1, max_depth)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [mask_sensitive_data(item, depth + 1, max_depth) for item in data]
    elif isinstance(data, tuple):
        return tuple(mask_sensitive_data(item, depth + 1, max_depth) for item in data)
    elif hasattr(data, "__dict__"):
        # Handle objects with __dict__ (like Pydantic models)
        return {
            key: "***MASKED***"
            if key.lower() in SENSITIVE_FIELDS
            else mask_sensitive_data(value, depth + 1, max_depth)
            for key, value in data.__dict__.items()
            if not key.startswith("_")
        }
    else:
        return data


def setup_logging() -> None:
    """
    Configure logging for the application.
    Sets up formatters, handlers, and log levels based on environment.
    """
    # Determine log level based on environment
    log_level = logging.INFO
    if settings.ENVIRONMENT == "local":
        log_level = logging.DEBUG
    elif settings.ENVIRONMENT == "production":
        log_level = logging.WARNING

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set specific log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)

    # Set our app logger to DEBUG in local environment
    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)

    logging.info(f"Logging configured for environment: {settings.ENVIRONMENT}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)

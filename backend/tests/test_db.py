"""Test database configuration.

This module provides a separate database engine for tests to avoid
wiping the main application database during test runs.

If POSTGRES_TEST_DB is configured in .env, tests will use that database.
Otherwise, tests will fall back to the main database (not recommended).
"""

import warnings
from sqlmodel import create_engine

from app.core.config import settings


def get_test_engine():
    """Get the database engine for tests.
    
    Uses POSTGRES_TEST_DB if configured, otherwise falls back to main DB
    with a warning.
    """
    if settings.SQLALCHEMY_TEST_DATABASE_URI:
        return create_engine(str(settings.SQLALCHEMY_TEST_DATABASE_URI))
    else:
        warnings.warn(
            "POSTGRES_TEST_DB not configured! Tests will use the main database. "
            "This may cause data loss. Set POSTGRES_TEST_DB in your .env file.",
            UserWarning,
            stacklevel=2,
        )
        from app.core.db import engine
        return engine


# Test engine - uses test database if configured
test_engine = get_test_engine()

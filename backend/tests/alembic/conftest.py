"""Conftest for alembic tests.

These tests don't require a database connection as they test
pure conversion logic.
"""

import pytest


@pytest.fixture(scope="session", autouse=True)
def db():
    """Override the db fixture to not require a database connection.
    
    The migration property tests verify conversion logic without
    needing an actual database.
    """
    yield None

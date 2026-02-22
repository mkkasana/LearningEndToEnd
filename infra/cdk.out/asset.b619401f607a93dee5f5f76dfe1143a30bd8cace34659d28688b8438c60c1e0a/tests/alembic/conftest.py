"""Conftest for alembic migration tests.

These tests don't require a database connection since they test
the migration logic conceptually.
"""

import pytest


# Override the db fixture to not require database connection
@pytest.fixture(scope="session")
def db():
    """Override db fixture - migration tests don't need database."""
    return None

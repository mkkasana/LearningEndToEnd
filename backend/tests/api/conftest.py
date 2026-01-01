"""Conftest for API tests.

Override the db fixture for tests that don't require database access.
"""

import pytest


@pytest.fixture(scope="session", autouse=False)
def db():
    """Override the db fixture to not auto-run for API property tests that don't need DB."""
    yield None

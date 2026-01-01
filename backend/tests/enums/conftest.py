"""Conftest for enum tests.

These tests don't require database access, so we override the db fixture
to prevent database initialization.
"""

import pytest


@pytest.fixture(scope="session", autouse=False)
def db():
    """Override the db fixture to not auto-run for enum tests."""
    yield None

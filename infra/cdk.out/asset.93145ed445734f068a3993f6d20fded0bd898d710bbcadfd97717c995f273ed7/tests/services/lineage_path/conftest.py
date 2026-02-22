"""Conftest for lineage path service tests.

Provides mock fixtures for unit tests that don't require database connection.
"""

from unittest.mock import MagicMock

import pytest
from sqlmodel import Session


@pytest.fixture
def mock_session() -> MagicMock:
    """Mock database session for isolated unit tests.

    Use this fixture when testing services/repositories in isolation
    without requiring a real database connection.
    """
    mock = MagicMock(spec=Session)
    # Configure common session methods
    mock.add = MagicMock()
    mock.commit = MagicMock()
    mock.refresh = MagicMock()
    mock.delete = MagicMock()
    mock.exec = MagicMock()
    mock.get = MagicMock()
    return mock

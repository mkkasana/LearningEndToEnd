"""Conftest for core module tests.

This conftest overrides the session-scoped db fixture to allow
tests to use in-memory SQLite instead of PostgreSQL.
"""

import pytest
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture(scope="session", autouse=False)
def db():
    """Override the global db fixture to not auto-use PostgreSQL."""
    # This fixture intentionally does nothing - tests in this module
    # use their own sqlite_session fixture instead
    pass


@pytest.fixture
def sqlite_session() -> Session:
    """Create an in-memory SQLite session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()

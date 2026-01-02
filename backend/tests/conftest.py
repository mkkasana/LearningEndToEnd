from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import init_db
from app.main import app
from app.api.deps import get_db
from app.models import Item, User
from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.db_models.person.person_religion import PersonReligion
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_metadata import PersonMetadata
from app.db_models.person.person_profession import PersonProfession
from app.db_models.profile_view_tracking import ProfileViewTracking
from app.db_models.support_ticket import SupportTicket
from tests.test_db import test_engine
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers
from tests.factories import UserFactory, PersonFactory


# Override the get_db dependency to use test database
def get_test_db() -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


# Apply the override globally
app.dependency_overrides[get_db] = get_test_db


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        init_db(session)
        yield session
        # Clean up in correct order (respecting foreign key constraints)
        # 1. Delete profile view tracking (references persons)
        session.execute(delete(ProfileViewTracking))
        # 2. Delete person relationships (references persons)
        session.execute(delete(PersonRelationship))
        # 3. Delete person religion (references persons)
        session.execute(delete(PersonReligion))
        # 4. Delete person address (references persons)
        session.execute(delete(PersonAddress))
        # 5. Delete person metadata (references persons)
        session.execute(delete(PersonMetadata))
        # 6. Delete person profession links (references persons)
        session.execute(delete(PersonProfession))
        # 7. Delete support tickets (references users)
        session.execute(delete(SupportTicket))
        # 8. Delete persons (references users)
        session.execute(delete(Person))
        # 9. Delete items (references users)
        session.execute(delete(Item))
        # 10. Finally delete users
        session.execute(delete(User))
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )


# ============================================================================
# Unit Test Fixtures (Mocked Dependencies)
# ============================================================================


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


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user for use in tests.

    This fixture creates a new user for each test that uses it.
    The user is automatically cleaned up at the end of the test session.
    """
    return UserFactory.create(db)


@pytest.fixture
def test_superuser(db: Session) -> User:
    """Create a test superuser for admin functionality tests."""
    return UserFactory.create_superuser(db)


@pytest.fixture
def test_person(db: Session, test_user: User) -> Person:
    """Create a test person linked to the test user.

    This fixture creates a person record associated with the test_user.
    """
    return PersonFactory.create_with_user(db, test_user)


@pytest.fixture
def auth_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Get authentication headers for a test user.

    Creates a new user and returns valid authentication headers.
    Use this for tests that need authenticated API access.
    """
    from tests.utils.user import user_authentication_headers

    user = UserFactory.create(db, password="testauth123")
    return user_authentication_headers(
        client=client,
        email=user.email,
        password="testauth123",
    )


@pytest.fixture
def admin_auth_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Get authentication headers for a superuser.

    Creates a new superuser and returns valid authentication headers.
    Use this for tests that need admin API access.
    """
    from tests.utils.user import user_authentication_headers

    user = UserFactory.create_superuser(db, password="adminauth123")
    return user_authentication_headers(
        client=client,
        email=user.email,
        password="adminauth123",
    )

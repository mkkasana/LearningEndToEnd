from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.config import settings
from app.core.db import engine, init_db
from app.main import app
from app.models import Item, User
from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.db_models.person.person_religion import PersonReligion
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_metadata import PersonMetadata
from app.db_models.person.person_profession import PersonProfession
from app.db_models.profile_view_tracking import ProfileViewTracking
from app.db_models.support_ticket import SupportTicket
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
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

"""Integration test fixtures.

This module provides fixtures specifically for integration tests that run
against a real database with seeded test data.

The fixtures here use the seeded data from init_seed scripts, providing
access to pre-existing users, persons, and relationships for testing.
"""

import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.db_models.user import User
from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.db_models.person.gender import Gender
from app.enums import GENDER_DATA, GenderEnum
from tests.test_db import test_engine


# ============================================================================
# Seeded Data Constants (from init_seed/seed_family.py)
# ============================================================================

# Test user from seed_family.py
SEED_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
SEED_USER_EMAIL = "testfamily@example.com"
SEED_USER_PASSWORD = "qweqweqwe"

# Seeded person IDs from seed_family.py
SEED_PERSON_IDS = {
    "dada_ji": uuid.UUID("82222222-2222-2222-2222-222222222202"),
    "dadi_ji": uuid.UUID("82222222-2222-2222-2222-222222222203"),
    "self": uuid.UUID("22222222-2222-2222-2222-222222222201"),
    "father": uuid.UUID("22222222-2222-2222-2222-222222222202"),
    "mother": uuid.UUID("22222222-2222-2222-2222-222222222203"),
    "spouse": uuid.UUID("22222222-2222-2222-2222-222222222204"),
    "son": uuid.UUID("22222222-2222-2222-2222-222222222205"),
    "daughter": uuid.UUID("22222222-2222-2222-2222-222222222206"),
}


# ============================================================================
# Database Session Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def integration_db() -> Generator[Session, None, None]:
    """Module-scoped database session for integration tests.

    This session is shared across all tests in a module and uses
    the seeded test data. No cleanup is performed to preserve
    the seeded data for other tests.
    """
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def integration_session(integration_db: Session) -> Generator[Session, None, None]:
    """Function-scoped session that rolls back after each test.

    Use this for tests that modify data but shouldn't persist changes.
    """
    # Start a nested transaction
    integration_db.begin_nested()
    yield integration_db
    # Rollback the nested transaction
    integration_db.rollback()


# ============================================================================
# Seeded User Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def seeded_user(integration_db: Session) -> User:
    """Get the seeded test user from the database.

    Returns the user created by seed_family.py with email testfamily@example.com.
    """
    user = integration_db.exec(
        select(User).where(User.id == SEED_USER_ID)
    ).first()
    if not user:
        pytest.skip("Seeded test user not found. Run seed_family.py first.")
    return user


@pytest.fixture(scope="module")
def seeded_user_auth_headers(client: TestClient) -> dict[str, str]:
    """Get authentication headers for the seeded test user.

    Uses the credentials from seed_family.py to authenticate.
    """
    from app.core.config import settings

    login_data = {
        "username": SEED_USER_EMAIL,
        "password": SEED_USER_PASSWORD,
    }
    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data=login_data,
    )
    if response.status_code != 200:
        pytest.skip(
            f"Could not authenticate seeded user. "
            f"Status: {response.status_code}. Run seed_family.py first."
        )
    tokens = response.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


# ============================================================================
# Seeded Person Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def seeded_self_person(integration_db: Session) -> Person:
    """Get the 'self' person from seeded data.

    This is the primary person linked to the seeded test user.
    """
    person = integration_db.exec(
        select(Person).where(Person.id == SEED_PERSON_IDS["self"])
    ).first()
    if not person:
        pytest.skip("Seeded 'self' person not found. Run seed_family.py first.")
    return person


@pytest.fixture(scope="module")
def seeded_father_person(integration_db: Session) -> Person:
    """Get the 'father' person from seeded data."""
    person = integration_db.exec(
        select(Person).where(Person.id == SEED_PERSON_IDS["father"])
    ).first()
    if not person:
        pytest.skip("Seeded 'father' person not found. Run seed_family.py first.")
    return person


@pytest.fixture(scope="module")
def seeded_mother_person(integration_db: Session) -> Person:
    """Get the 'mother' person from seeded data."""
    person = integration_db.exec(
        select(Person).where(Person.id == SEED_PERSON_IDS["mother"])
    ).first()
    if not person:
        pytest.skip("Seeded 'mother' person not found. Run seed_family.py first.")
    return person


@pytest.fixture(scope="module")
def seeded_spouse_person(integration_db: Session) -> Person:
    """Get the 'spouse' person from seeded data."""
    person = integration_db.exec(
        select(Person).where(Person.id == SEED_PERSON_IDS["spouse"])
    ).first()
    if not person:
        pytest.skip("Seeded 'spouse' person not found. Run seed_family.py first.")
    return person


@pytest.fixture(scope="module")
def seeded_family_persons(integration_db: Session) -> dict[str, Person]:
    """Get all seeded family persons as a dictionary.

    Returns a dict mapping person keys to Person objects.
    """
    persons = {}
    for key, person_id in SEED_PERSON_IDS.items():
        person = integration_db.exec(
            select(Person).where(Person.id == person_id)
        ).first()
        if person:
            persons[key] = person
    if not persons:
        pytest.skip("No seeded persons found. Run seed_family.py first.")
    return persons


# ============================================================================
# Gender Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def male_gender_id() -> uuid.UUID:
    """Get the male gender ID from enum data."""
    return GENDER_DATA[GenderEnum.MALE].id


@pytest.fixture(scope="module")
def female_gender_id() -> uuid.UUID:
    """Get the female gender ID from enum data."""
    return GENDER_DATA[GenderEnum.FEMALE].id


@pytest.fixture(scope="module")
def seeded_genders(integration_db: Session) -> dict[str, Gender]:
    """Get all seeded genders from the database."""
    genders = {}
    for gender_enum in GenderEnum:
        gender = integration_db.exec(
            select(Gender).where(Gender.code == gender_enum.value)
        ).first()
        if gender:
            genders[gender_enum.value] = gender
    if not genders:
        pytest.skip("No seeded genders found. Run seed_genders.py first.")
    return genders


# ============================================================================
# Relationship Fixtures
# ============================================================================


@pytest.fixture(scope="module")
def seeded_relationships(integration_db: Session) -> list[PersonRelationship]:
    """Get all seeded relationships for the 'self' person."""
    relationships = integration_db.exec(
        select(PersonRelationship).where(
            PersonRelationship.person_id == SEED_PERSON_IDS["self"]
        )
    ).all()
    if not relationships:
        pytest.skip("No seeded relationships found. Run seed_family.py first.")
    return list(relationships)


# ============================================================================
# Helper Fixtures
# ============================================================================


@pytest.fixture
def non_existent_uuid() -> uuid.UUID:
    """Generate a UUID that doesn't exist in the database.

    Useful for testing 404 responses.
    """
    return uuid.UUID("99999999-9999-9999-9999-999999999999")


@pytest.fixture
def invalid_uuid_string() -> str:
    """Return an invalid UUID string for testing validation errors."""
    return "not-a-valid-uuid"

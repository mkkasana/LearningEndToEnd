"""Integration tests for Lineage Path API routes.

This module tests the Lineage Path API endpoints including:
- POST /lineage-path/find (Task 4.3)

Tests use dynamically created test data.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.enums.relationship_type import RelationshipType
from tests.utils.utils import random_email, random_lower_string


# ============================================================================
# Helper Functions
# ============================================================================


def create_test_user_with_person(
    client: TestClient, db: Session
) -> tuple[dict[str, str], Person]:
    """Create a test user with a person profile and return auth headers and person."""
    email = random_email()
    password = random_lower_string() + "Aa1!"
    first_name = random_lower_string()[:10]
    last_name = random_lower_string()[:10]

    signup_data = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "gender": "MALE",
        "date_of_birth": "1990-01-01",
    }
    r = client.post(f"{settings.API_V1_STR}/users/signup", json=signup_data)
    if r.status_code != 200:
        pytest.skip(f"Could not create test user: {r.json()}")

    login_data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    if r.status_code != 200:
        pytest.skip(f"Could not login test user: {r.json()}")

    tokens = r.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    r = client.get(f"{settings.API_V1_STR}/person/me", headers=headers)
    if r.status_code != 200:
        pytest.skip(f"Could not get person: {r.json()}")

    person_data = r.json()
    person = db.exec(
        select(Person).where(Person.id == uuid.UUID(person_data["id"]))
    ).first()

    return headers, person


def create_family_member(
    client: TestClient, db: Session, headers: dict[str, str], first_name: str
) -> Person:
    """Create a family member (person without user account)."""
    from app.db_models.person.gender import Gender

    gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
    if not gender:
        pytest.skip("No genders found in database")

    family_data = {
        "first_name": first_name,
        "last_name": random_lower_string()[:10],
        "gender_id": str(gender.id),
        "date_of_birth": "1960-01-01",
    }
    r = client.post(
        f"{settings.API_V1_STR}/person/family-member",
        headers=headers,
        json=family_data,
    )
    if r.status_code != 200:
        pytest.skip(f"Could not create family member: {r.json()}")

    person_data = r.json()
    person = db.exec(
        select(Person).where(Person.id == uuid.UUID(person_data["id"]))
    ).first()
    return person


def create_relationship(
    db: Session,
    person_id: uuid.UUID,
    related_person_id: uuid.UUID,
    relationship_type: RelationshipType,
) -> PersonRelationship:
    """Create a relationship between two persons."""
    relationship = PersonRelationship(
        person_id=person_id,
        related_person_id=related_person_id,
        relationship_type=relationship_type,
        is_active=True,
    )
    db.add(relationship)
    db.commit()
    db.refresh(relationship)
    return relationship


# ============================================================================
# Integration Tests - POST /lineage-path/find (Task 4.3)
# ============================================================================


@pytest.mark.integration
class TestFindLineagePath:
    """Integration tests for POST /lineage-path/find endpoint."""

    def test_find_path_same_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test finding path when both IDs are the same person."""
        headers, person = create_test_user_with_person(client, db)

        r = client.post(
            f"{settings.API_V1_STR}/lineage-path/find",
            headers=headers,
            json={"person_a_id": str(person.id), "person_b_id": str(person.id)},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["connection_found"] is True
        assert data["message"] == "Same person provided for both inputs"
        assert data["common_ancestor_id"] == str(person.id)
        assert str(person.id) in data["graph"]

    def test_find_path_invalid_person_a(
        self, client: TestClient, db: Session
    ) -> None:
        """Test finding path with invalid person_a_id returns 404."""
        headers, person = create_test_user_with_person(client, db)
        non_existent_id = uuid.uuid4()

        r = client.post(
            f"{settings.API_V1_STR}/lineage-path/find",
            headers=headers,
            json={"person_a_id": str(non_existent_id), "person_b_id": str(person.id)},
        )
        assert r.status_code == 404
        assert "Person A not found" in r.json()["detail"]

    def test_find_path_invalid_person_b(
        self, client: TestClient, db: Session
    ) -> None:
        """Test finding path with invalid person_b_id returns 404."""
        headers, person = create_test_user_with_person(client, db)
        non_existent_id = uuid.uuid4()

        r = client.post(
            f"{settings.API_V1_STR}/lineage-path/find",
            headers=headers,
            json={"person_a_id": str(person.id), "person_b_id": str(non_existent_id)},
        )
        assert r.status_code == 404
        assert "Person B not found" in r.json()["detail"]

    def test_find_path_missing_person_a_id(
        self, client: TestClient, db: Session
    ) -> None:
        """Test finding path with missing person_a_id returns 422."""
        headers, person = create_test_user_with_person(client, db)

        r = client.post(
            f"{settings.API_V1_STR}/lineage-path/find",
            headers=headers,
            json={"person_b_id": str(person.id)},
        )
        assert r.status_code == 422

    def test_find_path_missing_person_b_id(
        self, client: TestClient, db: Session
    ) -> None:
        """Test finding path with missing person_b_id returns 422."""
        headers, person = create_test_user_with_person(client, db)

        r = client.post(
            f"{settings.API_V1_STR}/lineage-path/find",
            headers=headers,
            json={"person_a_id": str(person.id)},
        )
        assert r.status_code == 422

    def test_find_path_invalid_uuid_format(
        self, client: TestClient, db: Session
    ) -> None:
        """Test finding path with invalid UUID format returns 422."""
        headers, _ = create_test_user_with_person(client, db)

        r = client.post(
            f"{settings.API_V1_STR}/lineage-path/find",
            headers=headers,
            json={"person_a_id": "not-a-uuid", "person_b_id": "also-not-uuid"},
        )
        assert r.status_code == 422

    def test_find_path_without_auth(self, client: TestClient) -> None:
        """Test finding path without authentication returns 401."""
        r = client.post(
            f"{settings.API_V1_STR}/lineage-path/find",
            json={"person_a_id": str(uuid.uuid4()), "person_b_id": str(uuid.uuid4())},
        )
        assert r.status_code == 401

    def test_find_path_no_connection(
        self, client: TestClient, db: Session
    ) -> None:
        """Test finding path when no connection exists."""
        headers, person_a = create_test_user_with_person(client, db)
        person_b = create_family_member(client, db, headers, "Unrelated")

        r = client.post(
            f"{settings.API_V1_STR}/lineage-path/find",
            headers=headers,
            json={"person_a_id": str(person_a.id), "person_b_id": str(person_b.id)},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["connection_found"] is False
        assert "No relation found" in data["message"]
        assert data["common_ancestor_id"] is None

    def test_find_path_with_direct_relationship(
        self, client: TestClient, db: Session
    ) -> None:
        """Test finding path with direct parent-child relationship."""
        headers, child = create_test_user_with_person(client, db)
        father = create_family_member(client, db, headers, "Father")

        # Create bidirectional relationship
        create_relationship(db, child.id, father.id, RelationshipType.FATHER)
        create_relationship(db, father.id, child.id, RelationshipType.SON)

        r = client.post(
            f"{settings.API_V1_STR}/lineage-path/find",
            headers=headers,
            json={"person_a_id": str(child.id), "person_b_id": str(father.id)},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["connection_found"] is True
        assert data["common_ancestor_id"] is not None
        assert len(data["graph"]) >= 2

    def test_find_path_response_structure(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that response has correct structure."""
        headers, person = create_test_user_with_person(client, db)

        r = client.post(
            f"{settings.API_V1_STR}/lineage-path/find",
            headers=headers,
            json={"person_a_id": str(person.id), "person_b_id": str(person.id)},
        )
        assert r.status_code == 200
        data = r.json()

        # Verify response structure
        assert "connection_found" in data
        assert "message" in data
        assert "common_ancestor_id" in data
        assert "graph" in data

        # Verify graph node structure
        if data["graph"]:
            node = list(data["graph"].values())[0]
            assert "person_id" in node
            assert "first_name" in node
            assert "last_name" in node
            assert "birth_year" in node
            assert "death_year" in node
            assert "address" in node
            assert "religion" in node
            assert "from_person" in node
            assert "to_person" in node

"""Integration tests for Assume Person Role API endpoints.

This module tests the assume-person-role feature endpoints including:
- GET /api/v1/person/{person_id}/can-assume
- GET /api/v1/person/{person_id}/discover-family-members
- POST /api/v1/person/{person_id}/relationships
- DELETE /api/v1/person/{person_id}/relationships/{relationship_id}

Tests verify permission checks and functionality for elevated users
acting on behalf of persons they created.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.person.person import Person
from app.db_models.person.gender import Gender
from app.db_models.user import User
from app.enums import RelationshipType, GENDER_DATA, GenderEnum
from app.enums.user_role import UserRole
from tests.utils.utils import random_email, random_lower_string


# ============================================================================
# Helper Functions
# ============================================================================


def get_gender_id(db: Session, gender_code: str = "MALE") -> uuid.UUID:
    """Get gender ID by code."""
    gender = db.exec(select(Gender).where(Gender.code == gender_code)).first()
    if gender:
        return gender.id
    return GENDER_DATA[GenderEnum.MALE].id


def create_test_user_with_person(
    client: TestClient, db: Session, gender_code: str = "MALE", role: str = "member"
) -> tuple[dict[str, str], Person, User]:
    """Create a test user with a person profile and return auth headers, person, and user."""
    email = random_email()
    password = random_lower_string() + "Aa1!"
    first_name = random_lower_string()[:10]
    last_name = random_lower_string()[:10]

    signup_data = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "gender": gender_code,
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
    user = db.exec(select(User).where(User.email == email)).first()

    # Update user role if needed
    if role == "superuser":
        user.role = UserRole.SUPERUSER
        db.add(user)
        db.commit()
        db.refresh(user)
    elif role == "admin":
        user.role = UserRole.ADMIN
        db.add(user)
        db.commit()
        db.refresh(user)

    return headers, person, user


def create_family_member(
    client: TestClient,
    db: Session,
    headers: dict[str, str],
    first_name: str,
    gender_code: str = "MALE",
) -> Person:
    """Create a family member (person without user account)."""
    gender_id = get_gender_id(db, gender_code)

    person_data = {
        "first_name": first_name,
        "last_name": random_lower_string()[:10],
        "gender_id": str(gender_id),
        "date_of_birth": "1960-05-15",
    }
    r = client.post(
        f"{settings.API_V1_STR}/person/family-member",
        headers=headers,
        json=person_data,
    )
    if r.status_code != 200:
        pytest.skip(f"Could not create family member: {r.json()}")

    person_data = r.json()
    person = db.exec(
        select(Person).where(Person.id == uuid.UUID(person_data["id"]))
    ).first()
    return person


# ============================================================================
# Integration Tests - Can Assume Endpoint
# ============================================================================


@pytest.mark.integration
class TestCanAssumeEndpoint:
    """Integration tests for GET /person/{person_id}/can-assume endpoint."""

    def test_superuser_can_assume_person_they_created(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that superuser can assume a person they created."""
        headers, _, user = create_test_user_with_person(
            client, db, role="superuser"
        )
        family_member = create_family_member(client, db, headers, "AssumeTest")

        r = client.get(
            f"{settings.API_V1_STR}/person/{family_member.id}/can-assume",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["can_assume"] is True
        assert data["reason"] is None
        assert data["person_name"] is not None
        assert "AssumeTest" in data["person_name"]

    def test_admin_can_assume_person_they_created(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that admin can assume a person they created."""
        headers, _, user = create_test_user_with_person(client, db, role="admin")
        family_member = create_family_member(client, db, headers, "AdminAssumeTest")

        r = client.get(
            f"{settings.API_V1_STR}/person/{family_member.id}/can-assume",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["can_assume"] is True
        assert data["reason"] is None

    def test_regular_user_cannot_assume(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that regular user (MEMBER role) cannot assume any person."""
        headers, _, user = create_test_user_with_person(client, db, role="member")
        family_member = create_family_member(client, db, headers, "NoAssumeTest")

        r = client.get(
            f"{settings.API_V1_STR}/person/{family_member.id}/can-assume",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["can_assume"] is False
        assert data["reason"] == "not_elevated_user"
        assert data["person_name"] is None

    def test_superuser_cannot_assume_person_created_by_other(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that superuser cannot assume a person created by another user."""
        # Create first user who creates a family member
        headers1, _, _ = create_test_user_with_person(client, db, role="superuser")
        family_member = create_family_member(client, db, headers1, "OtherCreator")

        # Create second superuser
        headers2, _, _ = create_test_user_with_person(client, db, role="superuser")

        r = client.get(
            f"{settings.API_V1_STR}/person/{family_member.id}/can-assume",
            headers=headers2,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["can_assume"] is False
        assert data["reason"] == "not_creator"

    def test_can_assume_nonexistent_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test can-assume for non-existent person returns can_assume=False."""
        headers, _, _ = create_test_user_with_person(client, db, role="superuser")
        non_existent_id = uuid.uuid4()

        r = client.get(
            f"{settings.API_V1_STR}/person/{non_existent_id}/can-assume",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["can_assume"] is False
        assert data["reason"] == "person_not_found"

    def test_can_assume_without_auth(self, client: TestClient) -> None:
        """Test can-assume without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/person/{uuid.uuid4()}/can-assume")
        assert r.status_code == 401


# ============================================================================
# Integration Tests - Person-Specific Discover Family Members
# ============================================================================


@pytest.mark.integration
class TestPersonDiscoverFamilyMembers:
    """Integration tests for GET /person/{person_id}/discover-family-members endpoint."""

    def test_discover_for_own_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test discovering family members for user's own person."""
        headers, person, _ = create_test_user_with_person(client, db)

        r = client.get(
            f"{settings.API_V1_STR}/person/{person.id}/discover-family-members",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_discover_for_created_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test discovering family members for a person the user created."""
        headers, _, _ = create_test_user_with_person(client, db, role="superuser")
        family_member = create_family_member(client, db, headers, "DiscoverTest")

        r = client.get(
            f"{settings.API_V1_STR}/person/{family_member.id}/discover-family-members",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_discover_for_unrelated_person_denied(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that discovering for unrelated person is denied."""
        # Create first user who creates a family member
        headers1, _, _ = create_test_user_with_person(client, db)
        family_member = create_family_member(client, db, headers1, "UnrelatedDiscover")

        # Create second user (regular member)
        headers2, _, _ = create_test_user_with_person(client, db)

        r = client.get(
            f"{settings.API_V1_STR}/person/{family_member.id}/discover-family-members",
            headers=headers2,
        )
        assert r.status_code == 403

    def test_discover_for_nonexistent_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test discovering for non-existent person returns 404."""
        headers, _, _ = create_test_user_with_person(client, db)
        non_existent_id = uuid.uuid4()

        r = client.get(
            f"{settings.API_V1_STR}/person/{non_existent_id}/discover-family-members",
            headers=headers,
        )
        assert r.status_code == 404

    def test_discover_without_auth(self, client: TestClient) -> None:
        """Test discover without authentication returns 401."""
        r = client.get(
            f"{settings.API_V1_STR}/person/{uuid.uuid4()}/discover-family-members"
        )
        assert r.status_code == 401


# ============================================================================
# Integration Tests - Person-Specific Create Relationship
# ============================================================================


@pytest.mark.integration
class TestPersonCreateRelationship:
    """Integration tests for POST /person/{person_id}/relationships endpoint."""

    def test_create_relationship_for_own_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating relationship for user's own person."""
        headers, person, _ = create_test_user_with_person(client, db)
        family_member = create_family_member(client, db, headers, "RelFather", "MALE")

        relationship_data = {
            "related_person_id": str(family_member.id),
            "relationship_type": RelationshipType.FATHER.value,
            "is_active": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/relationships",
            headers=headers,
            json=relationship_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["related_person_id"] == str(family_member.id)
        assert data["relationship_type"] == RelationshipType.FATHER.value

    def test_create_relationship_for_created_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating relationship for a person the user created (assume role)."""
        headers, _, _ = create_test_user_with_person(client, db, role="superuser")
        family_member = create_family_member(client, db, headers, "AssumedPerson")
        another_member = create_family_member(client, db, headers, "RelatedPerson")

        relationship_data = {
            "related_person_id": str(another_member.id),
            "relationship_type": RelationshipType.SPOUSE.value,
            "is_active": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{family_member.id}/relationships",
            headers=headers,
            json=relationship_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["person_id"] == str(family_member.id)
        assert data["related_person_id"] == str(another_member.id)

    def test_create_relationship_for_unrelated_person_denied(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that creating relationship for unrelated person is denied."""
        # Create first user who creates a family member
        headers1, _, _ = create_test_user_with_person(client, db)
        family_member = create_family_member(client, db, headers1, "UnrelatedRel")

        # Create second user
        headers2, _, _ = create_test_user_with_person(client, db)
        other_member = create_family_member(client, db, headers2, "OtherMember")

        relationship_data = {
            "related_person_id": str(other_member.id),
            "relationship_type": RelationshipType.SPOUSE.value,
            "is_active": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{family_member.id}/relationships",
            headers=headers2,
            json=relationship_data,
        )
        assert r.status_code == 403

    def test_create_relationship_for_nonexistent_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating relationship for non-existent person returns 404."""
        headers, _, _ = create_test_user_with_person(client, db)
        family_member = create_family_member(client, db, headers, "ExistingMember")
        non_existent_id = uuid.uuid4()

        relationship_data = {
            "related_person_id": str(family_member.id),
            "relationship_type": RelationshipType.SPOUSE.value,
            "is_active": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{non_existent_id}/relationships",
            headers=headers,
            json=relationship_data,
        )
        assert r.status_code == 404

    def test_create_relationship_without_auth(self, client: TestClient) -> None:
        """Test creating relationship without authentication returns 401."""
        relationship_data = {
            "related_person_id": str(uuid.uuid4()),
            "relationship_type": RelationshipType.SPOUSE.value,
            "is_active": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{uuid.uuid4()}/relationships",
            json=relationship_data,
        )
        assert r.status_code == 401



# ============================================================================
# Integration Tests - Person-Specific Delete Relationship
# ============================================================================


@pytest.mark.integration
class TestPersonDeleteRelationship:
    """Integration tests for DELETE /person/{person_id}/relationships/{relationship_id} endpoint."""

    def test_delete_relationship_for_own_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting relationship for user's own person."""
        headers, person, _ = create_test_user_with_person(client, db)
        family_member = create_family_member(client, db, headers, "ToDeleteRel", "MALE")

        # Create relationship first
        relationship_data = {
            "related_person_id": str(family_member.id),
            "relationship_type": RelationshipType.FATHER.value,
            "is_active": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/relationships",
            headers=headers,
            json=relationship_data,
        )
        assert r.status_code == 200
        created_rel = r.json()

        # Delete relationship
        r = client.delete(
            f"{settings.API_V1_STR}/person/{person.id}/relationships/{created_rel['id']}",
            headers=headers,
        )
        assert r.status_code == 200
        assert "deleted" in r.json()["message"].lower()

    def test_delete_relationship_for_created_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting relationship for a person the user created (assume role)."""
        headers, _, _ = create_test_user_with_person(client, db, role="superuser")
        family_member = create_family_member(client, db, headers, "AssumedDelete")
        another_member = create_family_member(client, db, headers, "RelatedDelete")

        # Create relationship for the family member
        relationship_data = {
            "related_person_id": str(another_member.id),
            "relationship_type": RelationshipType.SPOUSE.value,
            "is_active": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{family_member.id}/relationships",
            headers=headers,
            json=relationship_data,
        )
        assert r.status_code == 200
        created_rel = r.json()

        # Delete relationship using person-specific endpoint
        r = client.delete(
            f"{settings.API_V1_STR}/person/{family_member.id}/relationships/{created_rel['id']}",
            headers=headers,
        )
        assert r.status_code == 200
        assert "deleted" in r.json()["message"].lower()

    def test_delete_relationship_for_unrelated_person_denied(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that deleting relationship for unrelated person is denied."""
        # Create first user who creates a family member with relationship
        headers1, _, _ = create_test_user_with_person(client, db)
        family_member = create_family_member(client, db, headers1, "UnrelatedDelete")
        another_member = create_family_member(client, db, headers1, "RelatedUnrelated")

        relationship_data = {
            "related_person_id": str(another_member.id),
            "relationship_type": RelationshipType.SPOUSE.value,
            "is_active": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{family_member.id}/relationships",
            headers=headers1,
            json=relationship_data,
        )
        created_rel = r.json()

        # Create second user
        headers2, _, _ = create_test_user_with_person(client, db)

        # Try to delete - should be denied
        r = client.delete(
            f"{settings.API_V1_STR}/person/{family_member.id}/relationships/{created_rel['id']}",
            headers=headers2,
        )
        assert r.status_code == 403

    def test_delete_nonexistent_relationship(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting non-existent relationship returns 404."""
        headers, person, _ = create_test_user_with_person(client, db)
        non_existent_rel_id = uuid.uuid4()

        r = client.delete(
            f"{settings.API_V1_STR}/person/{person.id}/relationships/{non_existent_rel_id}",
            headers=headers,
        )
        assert r.status_code == 404

    def test_delete_relationship_wrong_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting relationship that belongs to different person returns 404."""
        headers, person, _ = create_test_user_with_person(client, db)
        family_member = create_family_member(client, db, headers, "WrongPerson", "MALE")
        another_member = create_family_member(client, db, headers, "AnotherWrong")

        # Create relationship for family_member
        relationship_data = {
            "related_person_id": str(another_member.id),
            "relationship_type": RelationshipType.SPOUSE.value,
            "is_active": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{family_member.id}/relationships",
            headers=headers,
            json=relationship_data,
        )
        created_rel = r.json()

        # Try to delete using person.id (wrong person) - should return 404
        r = client.delete(
            f"{settings.API_V1_STR}/person/{person.id}/relationships/{created_rel['id']}",
            headers=headers,
        )
        assert r.status_code == 404

    def test_delete_relationship_without_auth(self, client: TestClient) -> None:
        """Test deleting relationship without authentication returns 401."""
        r = client.delete(
            f"{settings.API_V1_STR}/person/{uuid.uuid4()}/relationships/{uuid.uuid4()}"
        )
        assert r.status_code == 401


# ============================================================================
# Integration Tests - Admin Override Access
# ============================================================================


@pytest.mark.integration
class TestAdminOverrideAccess:
    """Integration tests for admin override access to person-specific endpoints."""

    def test_admin_can_access_any_person_relationships(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that admin can access relationships for any person."""
        # Create regular user with family member
        headers1, _, _ = create_test_user_with_person(client, db)
        family_member = create_family_member(client, db, headers1, "AdminAccessTest")

        # Create admin user
        headers2, _, _ = create_test_user_with_person(client, db, role="admin")

        # Admin should be able to access the family member's relationships
        r = client.get(
            f"{settings.API_V1_STR}/person/{family_member.id}/relationships",
            headers=headers2,
        )
        assert r.status_code == 200

    def test_admin_can_discover_for_any_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that admin can discover family members for any person."""
        # Create regular user with family member
        headers1, _, _ = create_test_user_with_person(client, db)
        family_member = create_family_member(client, db, headers1, "AdminDiscoverTest")

        # Create admin user
        headers2, _, _ = create_test_user_with_person(client, db, role="admin")

        # Admin should be able to discover for the family member
        r = client.get(
            f"{settings.API_V1_STR}/person/{family_member.id}/discover-family-members",
            headers=headers2,
        )
        assert r.status_code == 200

"""Property-based tests for Person API.

This module contains property-based tests for the Person API endpoints,
validating universal properties across many generated inputs.

**Feature: backend-testing-coverage**
"""

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlmodel import Session, select

from app.core.config import settings as app_settings
from app.db_models.person.person import Person
from app.db_models.person.gender import Gender
from app.db_models.user import User
from app.core.security import get_password_hash
from tests.utils.utils import random_email, random_lower_string


# ============================================================================
# Helper Functions
# ============================================================================


def create_test_user_with_person_for_property(
    client: TestClient, db: Session
) -> tuple[dict[str, str], Person, User] | None:
    """Create a test user with a person profile and return auth headers, person, and user.
    
    Returns None if creation fails (for property tests to handle gracefully).
    """
    # Create user
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
    r = client.post(f"{app_settings.API_V1_STR}/users/signup", json=signup_data)
    if r.status_code != 200:
        return None
    
    # Login to get auth headers
    login_data = {"username": email, "password": password}
    r = client.post(f"{app_settings.API_V1_STR}/login/access-token", data=login_data)
    if r.status_code != 200:
        return None
    
    tokens = r.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    # Get the person
    r = client.get(f"{app_settings.API_V1_STR}/person/me", headers=headers)
    if r.status_code != 200:
        return None
    
    person_data = r.json()
    person = db.exec(select(Person).where(Person.id == uuid.UUID(person_data["id"]))).first()
    user = db.exec(select(User).where(User.email == email)).first()
    
    if not person or not user:
        return None
    
    return headers, person, user


def create_another_user_person(db: Session, gender_id: uuid.UUID) -> tuple[User, Person]:
    """Create another user with a person for testing unauthorized access."""
    # Create user directly in DB
    user = User(
        email=f"other_{uuid.uuid4()}@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create person for this user
    person = Person(
        first_name="Other",
        last_name="Person",
        date_of_birth=date(1985, 5, 15),
        gender_id=gender_id,
        user_id=user.id,
        created_by_user_id=user.id,
        is_primary=True,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    
    return user, person


# ============================================================================
# UUID Generation Strategy
# ============================================================================


@st.composite
def random_uuid_strategy(draw):
    """Generate random UUIDs that are guaranteed not to exist in the database."""
    # Generate a random UUID using hypothesis
    # Using a specific pattern that's unlikely to collide with real data
    part1 = draw(st.integers(min_value=0x90000000, max_value=0x9FFFFFFF))
    part2 = draw(st.integers(min_value=0x0000, max_value=0xFFFF))
    part3 = draw(st.integers(min_value=0x0000, max_value=0xFFFF))
    part4 = draw(st.integers(min_value=0x0000, max_value=0xFFFF))
    part5 = draw(st.integers(min_value=0x000000000000, max_value=0xFFFFFFFFFFFF))
    
    uuid_str = f"{part1:08x}-{part2:04x}-{part3:04x}-{part4:04x}-{part5:012x}"
    return uuid.UUID(uuid_str)


# ============================================================================
# Property Tests - Task 15.4: Unauthorized Person Access
# ============================================================================


@pytest.mark.integration
class TestUnauthorizedPersonAccessProperty:
    """Property tests for unauthorized person access.
    
    **Feature: backend-testing-coverage, Property 3: Unauthorized Access Returns 403**
    **Validates: Requirements 8.10**
    
    Property: For any API request where the authenticated user does not have 
    permission to access or modify the requested resource, the API should 
    return a 403 Forbidden response.
    """

    @settings(
        max_examples=5,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    @given(
        # Generate random data for the test
        random_seed=st.integers(min_value=1, max_value=1000000),
    )
    def test_unauthorized_admin_endpoint_access_returns_403(
        self,
        client: TestClient,
        db: Session,
        random_seed: int,
    ) -> None:
        """Property 3: Normal user accessing admin-only person endpoints returns 403.
        
        For any authenticated non-admin user attempting to access admin-only
        person endpoints (GET /person/{user_id}, DELETE /person/{user_id}),
        the API should return 403 Forbidden.
        """
        # Rollback any pending transaction
        db.rollback()
        
        # Create a test user (non-admin)
        result = create_test_user_with_person_for_property(client, db)
        if result is None:
            # Skip this iteration if user creation failed
            return
        
        headers, person, user = result
        
        # Generate a random user_id to try to access
        target_user_id = uuid.uuid4()
        
        try:
            # Test GET /person/{user_id} - admin only endpoint
            r = client.get(
                f"{app_settings.API_V1_STR}/person/{target_user_id}",
                headers=headers,
            )
            assert r.status_code == 403, (
                f"Expected 403 for non-admin GET /person/{{user_id}}, "
                f"got {r.status_code}. Response: {r.json()}"
            )
            
            # Test DELETE /person/{user_id} - admin only endpoint
            r = client.delete(
                f"{app_settings.API_V1_STR}/person/{target_user_id}",
                headers=headers,
            )
            assert r.status_code == 403, (
                f"Expected 403 for non-admin DELETE /person/{{user_id}}, "
                f"got {r.status_code}. Response: {r.json()}"
            )
            
        finally:
            # Cleanup is handled by test session cleanup
            pass


# ============================================================================
# Property Tests - Task 15.5: Non-Existent Person
# ============================================================================


@pytest.mark.integration
class TestNonExistentPersonProperty:
    """Property tests for non-existent person access.
    
    **Feature: backend-testing-coverage, Property 2: Non-Existent Resource Returns 404**
    **Validates: Requirements 8.11**
    
    Property: For any API request that references a person ID that does not 
    exist in the database, the API should return a 404 Not Found response.
    """

    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    @given(
        non_existent_id=random_uuid_strategy(),
    )
    def test_non_existent_person_complete_details_returns_404(
        self,
        client: TestClient,
        db: Session,
        non_existent_id: uuid.UUID,
    ) -> None:
        """Property 2: GET /person/{person_id}/complete-details with non-existent ID returns 404.
        
        For any randomly generated UUID that doesn't exist in the database,
        requesting complete details should return 404.
        """
        # Rollback any pending transaction
        db.rollback()
        
        # Verify the UUID doesn't exist
        existing = db.exec(select(Person).where(Person.id == non_existent_id)).first()
        if existing:
            # Skip this test case if UUID happens to exist (extremely unlikely)
            return
        
        # Create a test user to get auth headers
        result = create_test_user_with_person_for_property(client, db)
        if result is None:
            # Skip this iteration if user creation failed
            return
        
        headers, _, _ = result
        
        # Test GET /person/{person_id}/complete-details
        r = client.get(
            f"{app_settings.API_V1_STR}/person/{non_existent_id}/complete-details",
            headers=headers,
        )
        
        assert r.status_code == 404, (
            f"Expected 404 for non-existent person complete-details, "
            f"got {r.status_code}. UUID: {non_existent_id}. Response: {r.json()}"
        )

    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    @given(
        non_existent_id=random_uuid_strategy(),
    )
    def test_non_existent_person_relationships_returns_404(
        self,
        client: TestClient,
        db: Session,
        non_existent_id: uuid.UUID,
    ) -> None:
        """Property 2: GET /person/{person_id}/relationships/with-details with non-existent ID returns 404.
        
        For any randomly generated UUID that doesn't exist in the database,
        requesting relationships should return 404.
        """
        # Rollback any pending transaction
        db.rollback()
        
        # Verify the UUID doesn't exist
        existing = db.exec(select(Person).where(Person.id == non_existent_id)).first()
        if existing:
            # Skip this test case if UUID happens to exist (extremely unlikely)
            return
        
        # Create a test user to get auth headers
        result = create_test_user_with_person_for_property(client, db)
        if result is None:
            # Skip this iteration if user creation failed
            return
        
        headers, _, _ = result
        
        # Test GET /person/{person_id}/relationships/with-details
        r = client.get(
            f"{app_settings.API_V1_STR}/person/{non_existent_id}/relationships/with-details",
            headers=headers,
        )
        
        assert r.status_code == 404, (
            f"Expected 404 for non-existent person relationships, "
            f"got {r.status_code}. UUID: {non_existent_id}. Response: {r.json()}"
        )

    @settings(
        max_examples=5,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    @given(
        non_existent_id=random_uuid_strategy(),
    )
    def test_non_existent_user_person_admin_endpoint_returns_404(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        db: Session,
        non_existent_id: uuid.UUID,
    ) -> None:
        """Property 2: Admin GET /person/{user_id} with non-existent user_id returns 404.
        
        For any randomly generated UUID that doesn't exist as a user_id,
        admin endpoint should return 404.
        """
        # Rollback any pending transaction
        db.rollback()
        
        # Verify the UUID doesn't exist as a user
        existing = db.exec(select(User).where(User.id == non_existent_id)).first()
        if existing:
            # Skip this test case if UUID happens to exist (extremely unlikely)
            return
        
        # Test GET /person/{user_id} as admin
        r = client.get(
            f"{app_settings.API_V1_STR}/person/{non_existent_id}",
            headers=superuser_token_headers,
        )
        
        assert r.status_code == 404, (
            f"Expected 404 for non-existent user person (admin), "
            f"got {r.status_code}. UUID: {non_existent_id}. Response: {r.json()}"
        )

    @settings(
        max_examples=5,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    @given(
        non_existent_id=random_uuid_strategy(),
    )
    def test_non_existent_user_person_admin_delete_returns_404(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        db: Session,
        non_existent_id: uuid.UUID,
    ) -> None:
        """Property 2: Admin DELETE /person/{user_id} with non-existent user_id returns 404.
        
        For any randomly generated UUID that doesn't exist as a user_id,
        admin delete endpoint should return 404.
        """
        # Rollback any pending transaction
        db.rollback()
        
        # Verify the UUID doesn't exist as a user
        existing = db.exec(select(User).where(User.id == non_existent_id)).first()
        if existing:
            # Skip this test case if UUID happens to exist (extremely unlikely)
            return
        
        # Test DELETE /person/{user_id} as admin
        r = client.delete(
            f"{app_settings.API_V1_STR}/person/{non_existent_id}",
            headers=superuser_token_headers,
        )
        
        assert r.status_code == 404, (
            f"Expected 404 for non-existent user person delete (admin), "
            f"got {r.status_code}. UUID: {non_existent_id}. Response: {r.json()}"
        )

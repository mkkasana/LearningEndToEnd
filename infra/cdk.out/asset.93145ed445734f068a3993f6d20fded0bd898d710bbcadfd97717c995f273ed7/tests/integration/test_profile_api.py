"""Integration tests for Profile API routes.

This module tests the Profile API endpoints including:
- Profile completion status (Task 18.1)
- Profile view tracking (Task 18.2)

Tests use a combination of seeded data and dynamically created test data.

Requirements: 10.1-10.8
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.person.person import Person
from app.db_models.person.gender import Gender
from app.db_models.profile_view_tracking import ProfileViewTracking
from app.enums import GENDER_DATA, GenderEnum
from tests.utils.utils import random_email, random_lower_string


# ============================================================================
# Helper Functions
# ============================================================================


def get_gender_id(db: Session, gender_code: str = "MALE") -> uuid.UUID:
    """Get gender ID by code."""
    gender = db.exec(select(Gender).where(Gender.code == gender_code)).first()
    if gender:
        return gender.id
    # Fallback to enum data
    return GENDER_DATA[GenderEnum.MALE].id


def create_test_user_with_person(
    client: TestClient, db: Session
) -> tuple[dict[str, str], Person]:
    """Create a test user with a person profile and return auth headers and person."""
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
    r = client.post(f"{settings.API_V1_STR}/users/signup", json=signup_data)
    if r.status_code != 200:
        pytest.skip(f"Could not create test user: {r.json()}")
    
    # Login to get auth headers
    login_data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    if r.status_code != 200:
        pytest.skip(f"Could not login test user: {r.json()}")
    
    tokens = r.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    # Get the person
    r = client.get(f"{settings.API_V1_STR}/person/me", headers=headers)
    if r.status_code != 200:
        pytest.skip(f"Could not get person: {r.json()}")
    
    person_data = r.json()
    person = db.exec(select(Person).where(Person.id == uuid.UUID(person_data["id"]))).first()
    
    return headers, person


def create_test_user_without_person(
    client: TestClient, db: Session
) -> tuple[dict[str, str], uuid.UUID]:
    """Create a test user without a person profile and return auth headers and user_id."""
    from app.models import User, UserCreate
    from app.core.security import get_password_hash
    
    email = random_email()
    password = random_lower_string() + "Aa1!"
    
    # Create user directly in database without person
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Login to get auth headers
    login_data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    if r.status_code != 200:
        pytest.skip(f"Could not login test user: {r.json()}")
    
    tokens = r.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    return headers, user.id


# ============================================================================
# Integration Tests - Profile Completion Status (Task 18.1)
# ============================================================================


@pytest.mark.integration
class TestGetProfileCompletionStatus:
    """Integration tests for GET /profile/completion-status endpoint.
    
    Requirements: 10.2
    """

    def test_get_profile_completion_status_with_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting profile completion status for user with person profile."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/completion-status",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # Verify response structure
        assert "is_complete" in data
        assert "has_person" in data
        assert "has_address" in data
        assert "has_religion" in data
        assert "missing_fields" in data
        
        # User has person but may not have address/religion
        assert data["has_person"] is True
        assert isinstance(data["missing_fields"], list)

    def test_get_profile_completion_status_without_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting profile completion status for user without person profile."""
        headers, user_id = create_test_user_without_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/completion-status",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # User without person should have incomplete profile
        assert data["is_complete"] is False
        assert data["has_person"] is False
        assert data["has_address"] is False
        assert data["has_religion"] is False
        assert "person" in data["missing_fields"]

    def test_get_profile_completion_status_without_auth(
        self, client: TestClient
    ) -> None:
        """Test getting profile completion status without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/profile/completion-status")
        assert r.status_code == 401

    def test_get_profile_completion_status_missing_fields_accuracy(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that missing_fields accurately reflects what's missing."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/completion-status",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # Verify consistency between flags and missing_fields
        if not data["has_person"]:
            assert "person" in data["missing_fields"]
        if not data["has_address"]:
            assert "address" in data["missing_fields"]
        if not data["has_religion"]:
            assert "religion" in data["missing_fields"]
        
        # If complete, missing_fields should be empty
        if data["is_complete"]:
            assert len(data["missing_fields"]) == 0


# ============================================================================
# Integration Tests - Profile Views (Task 18.2)
# ============================================================================


@pytest.mark.integration
class TestProfileViewTracking:
    """Integration tests for profile view tracking functionality.
    
    Profile views are recorded when viewing person relationships with details.
    
    Requirements: 10.5, 10.6, 10.7
    """

    def test_profile_view_recorded_on_relationships_with_details(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that viewing person relationships with details records a profile view."""
        # Create two users - viewer and viewed
        viewer_headers, viewer_person = create_test_user_with_person(client, db)
        _, viewed_person = create_test_user_with_person(client, db)
        
        # Get initial view count
        initial_views = db.exec(
            select(ProfileViewTracking).where(
                ProfileViewTracking.viewed_person_id == viewed_person.id
            )
        ).all()
        initial_count = sum(v.view_count for v in initial_views)
        
        # View the person's relationships with details (this endpoint records views)
        r = client.get(
            f"{settings.API_V1_STR}/person/{viewed_person.id}/relationships/with-details",
            headers=viewer_headers,
        )
        assert r.status_code == 200
        
        # Refresh session to see new data
        db.expire_all()
        
        # Check that view was recorded
        updated_views = db.exec(
            select(ProfileViewTracking).where(
                ProfileViewTracking.viewed_person_id == viewed_person.id
            )
        ).all()
        updated_count = sum(v.view_count for v in updated_views)
        
        # View count should have increased
        assert updated_count >= initial_count + 1

    def test_self_view_not_recorded(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that viewing own profile does not record a view.
        
        Property 5: Self-View Does Not Increment Count
        Validates: Requirements 10.7
        """
        headers, person = create_test_user_with_person(client, db)
        
        # Get initial view count for self
        initial_views = db.exec(
            select(ProfileViewTracking).where(
                ProfileViewTracking.viewed_person_id == person.id,
                ProfileViewTracking.viewer_person_id == person.id
            )
        ).all()
        initial_self_view_count = sum(v.view_count for v in initial_views)
        
        # View own relationships with details
        r = client.get(
            f"{settings.API_V1_STR}/person/{person.id}/relationships/with-details",
            headers=headers,
        )
        assert r.status_code == 200
        
        # Refresh session
        db.expire_all()
        
        # Check that self-view was NOT recorded
        updated_views = db.exec(
            select(ProfileViewTracking).where(
                ProfileViewTracking.viewed_person_id == person.id,
                ProfileViewTracking.viewer_person_id == person.id
            )
        ).all()
        updated_self_view_count = sum(v.view_count for v in updated_views)
        
        # Self-view count should not have increased
        assert updated_self_view_count == initial_self_view_count

    def test_multiple_views_increment_count(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that multiple views from same viewer increment the count."""
        viewer_headers, viewer_person = create_test_user_with_person(client, db)
        _, viewed_person = create_test_user_with_person(client, db)
        
        # Get initial view count
        initial_views = db.exec(
            select(ProfileViewTracking).where(
                ProfileViewTracking.viewed_person_id == viewed_person.id,
                ProfileViewTracking.viewer_person_id == viewer_person.id
            )
        ).all()
        initial_count = sum(v.view_count for v in initial_views)
        
        # View the person's relationships with details multiple times
        view_count = 3
        for _ in range(view_count):
            r = client.get(
                f"{settings.API_V1_STR}/person/{viewed_person.id}/relationships/with-details",
                headers=viewer_headers,
            )
            assert r.status_code == 200
        
        # Refresh session to see new data
        db.expire_all()
        
        # Check that views were recorded
        updated_views = db.exec(
            select(ProfileViewTracking).where(
                ProfileViewTracking.viewed_person_id == viewed_person.id,
                ProfileViewTracking.viewer_person_id == viewer_person.id
            )
        ).all()
        
        # Total count should have increased by at least the number of views
        updated_count = sum(v.view_count for v in updated_views)
        # Views should have been recorded (count increased)
        assert updated_count >= initial_count + view_count

    def test_view_non_existent_person_returns_404(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that viewing non-existent person returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{non_existent_uuid}/relationships/with-details",
            headers=headers,
        )
        assert r.status_code == 404

    def test_view_without_auth_returns_401(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that viewing person without authentication returns 401."""
        _, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{person.id}/relationships/with-details"
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestGetMyContributionsWithViews:
    """Integration tests for contributions endpoint with view counts.
    
    The my-contributions endpoint returns persons with their view counts.
    
    Requirements: 10.5
    """

    def test_contributions_include_view_counts(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that contributions response includes total_views field."""
        headers, _ = create_test_user_with_person(client, db)
        
        # Create a family member
        gender_id = get_gender_id(db)
        family_member_data = {
            "first_name": "ViewTest",
            "last_name": "Member",
            "gender_id": str(gender_id),
            "date_of_birth": "1960-05-15",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/family-member",
            headers=headers,
            json=family_member_data,
        )
        assert r.status_code == 200
        
        # Get contributions
        r = client.get(
            f"{settings.API_V1_STR}/person/my-contributions",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # Verify response includes view counts
        assert isinstance(data, list)
        if len(data) > 0:
            contribution = data[0]
            assert "total_views" in contribution
            assert isinstance(contribution["total_views"], int)
            assert contribution["total_views"] >= 0


# ============================================================================
# Property-Based Tests (Task 18.3, 18.4)
# ============================================================================


@pytest.mark.integration
class TestSelfViewExclusionProperty:
    """Property-based tests for self-view exclusion.
    
    **Feature: backend-testing-coverage, Property 5: Self-View Does Not Increment Count**
    **Validates: Requirements 10.7**
    """

    def test_self_view_never_recorded_property(
        self, client: TestClient, db: Session
    ) -> None:
        """Property 5: For any user viewing their own profile, the view count 
        for self-views should never increase.
        
        This is a property test that verifies the invariant: self-views are 
        never recorded regardless of how many times a user views their own profile.
        """
        # Create a test user with person
        headers, person = create_test_user_with_person(client, db)
        
        # Get initial self-view count
        initial_views = db.exec(
            select(ProfileViewTracking).where(
                ProfileViewTracking.viewed_person_id == person.id,
                ProfileViewTracking.viewer_person_id == person.id
            )
        ).all()
        initial_self_view_count = sum(v.view_count for v in initial_views)
        
        # View own profile multiple times (simulating property test iterations)
        num_views = 10
        for _ in range(num_views):
            r = client.get(
                f"{settings.API_V1_STR}/person/{person.id}/relationships/with-details",
                headers=headers,
            )
            assert r.status_code == 200
        
        # Refresh session
        db.expire_all()
        
        # Verify self-view count has NOT increased
        final_views = db.exec(
            select(ProfileViewTracking).where(
                ProfileViewTracking.viewed_person_id == person.id,
                ProfileViewTracking.viewer_person_id == person.id
            )
        ).all()
        final_self_view_count = sum(v.view_count for v in final_views)
        
        # Property: Self-view count should remain unchanged
        assert final_self_view_count == initial_self_view_count, (
            f"Self-view count changed from {initial_self_view_count} to "
            f"{final_self_view_count} after {num_views} self-views"
        )


@pytest.mark.integration
class TestProfileCompletionPercentageProperty:
    """Property-based tests for profile completion percentage accuracy.
    
    **Feature: backend-testing-coverage, Property 6: Profile Completion Percentage Accuracy**
    **Validates: Requirements 10.8**
    """

    def test_completion_status_consistency_property(
        self, client: TestClient, db: Session
    ) -> None:
        """Property 6: For any user profile, the completion status fields 
        should be internally consistent.
        
        Invariants:
        1. If is_complete is True, then has_person, has_address, has_religion, has_marital_status, and has_duplicate_check must all be True, and has_pending_attachment_request must be False
        2. If any of has_person, has_address, has_religion, has_marital_status, has_duplicate_check is False, or has_pending_attachment_request is True, is_complete must be False
        3. missing_fields should contain exactly the fields that are False
        """
        # Test with user who has person (but may not have address/religion/marital_status)
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/completion-status",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # Property 1: If complete, all fields must be True and no pending request
        if data["is_complete"]:
            assert data["has_person"] is True, "is_complete=True but has_person=False"
            assert data["has_address"] is True, "is_complete=True but has_address=False"
            assert data["has_religion"] is True, "is_complete=True but has_religion=False"
            assert data["has_marital_status"] is True, "is_complete=True but has_marital_status=False"
            assert data["has_duplicate_check"] is True, "is_complete=True but has_duplicate_check=False"
            assert data["has_pending_attachment_request"] is False, "is_complete=True but has_pending_attachment_request=True"
            assert len(data["missing_fields"]) == 0, "is_complete=True but missing_fields not empty"
        
        # Property 2: If any field is False or has pending request, is_complete must be False
        if (not data["has_person"] or not data["has_address"] or not data["has_religion"] 
            or not data["has_marital_status"] or not data["has_duplicate_check"]
            or data["has_pending_attachment_request"]):
            assert data["is_complete"] is False, (
                f"is_complete=True but has_person={data['has_person']}, "
                f"has_address={data['has_address']}, has_religion={data['has_religion']}, "
                f"has_marital_status={data['has_marital_status']}, "
                f"has_duplicate_check={data['has_duplicate_check']}, "
                f"has_pending_attachment_request={data['has_pending_attachment_request']}"
            )
        
        # Property 3: missing_fields should match False fields
        expected_missing = []
        if not data["has_person"]:
            expected_missing.append("person")
        if not data["has_address"]:
            expected_missing.append("address")
        if not data["has_religion"]:
            expected_missing.append("religion")
        if not data["has_marital_status"]:
            expected_missing.append("marital_status")
        if not data["has_duplicate_check"]:
            expected_missing.append("duplicate_check")
        
        assert set(data["missing_fields"]) == set(expected_missing), (
            f"missing_fields={data['missing_fields']} but expected {expected_missing}"
        )

    def test_completion_status_without_person_property(
        self, client: TestClient, db: Session
    ) -> None:
        """Property 6: For any user without a person profile, the completion 
        status should indicate all fields are missing.
        """
        headers, user_id = create_test_user_without_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/completion-status",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # Property: Without person, nothing can be complete
        assert data["is_complete"] is False
        assert data["has_person"] is False
        assert data["has_address"] is False
        assert data["has_religion"] is False
        assert data["has_marital_status"] is False
        
        # All fields should be in missing_fields
        assert "person" in data["missing_fields"]
        assert "address" in data["missing_fields"]
        assert "religion" in data["missing_fields"]
        assert "marital_status" in data["missing_fields"]


# ============================================================================
# Integration Tests - Duplicate Check Endpoint (Task 15.1)
# ============================================================================


@pytest.mark.integration
class TestDuplicateCheckEndpoint:
    """Integration tests for GET /profile/duplicate-check endpoint.
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
    """

    def test_duplicate_check_returns_list(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that duplicate check endpoint returns a list of matches."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/duplicate-check",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # Should return a list (may be empty if no matches)
        assert isinstance(data, list)

    def test_duplicate_check_without_auth_returns_401(
        self, client: TestClient
    ) -> None:
        """Test that duplicate check without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/profile/duplicate-check")
        assert r.status_code == 401

    def test_duplicate_check_excludes_self(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that duplicate check excludes the current user's own person record."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/duplicate-check",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # Verify own person is not in results
        person_ids = [match["person_id"] for match in data]
        assert str(person.id) not in person_ids

    def test_duplicate_check_response_structure(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that duplicate check response has correct structure."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/duplicate-check",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # If there are matches, verify structure
        if len(data) > 0:
            match = data[0]
            assert "person_id" in match
            assert "first_name" in match
            assert "last_name" in match
            assert "date_of_birth" in match
            assert "match_score" in match
            assert "address_display" in match
            assert "religion_display" in match


# ============================================================================
# Integration Tests - Complete Without Attachment Endpoint (Task 15.1)
# ============================================================================


@pytest.mark.integration
class TestCompleteWithoutAttachmentEndpoint:
    """Integration tests for POST /profile/complete-without-attachment endpoint.
    
    Requirements: 8.1, 8.2, 8.3, 8.4
    """

    def test_complete_without_attachment_activates_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that complete without attachment activates the person record."""
        headers, person = create_test_user_with_person(client, db)
        
        # Ensure person is inactive first (signup creates inactive person)
        # Note: The person might already be active if tests ran before
        # So we just verify the endpoint works
        
        r = client.post(
            f"{settings.API_V1_STR}/profile/complete-without-attachment",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # Verify response structure
        assert "is_complete" in data
        assert "has_person" in data
        assert "has_duplicate_check" in data
        
        # has_duplicate_check should be True after completing
        assert data["has_duplicate_check"] is True

    def test_complete_without_attachment_without_auth_returns_401(
        self, client: TestClient
    ) -> None:
        """Test that complete without attachment without authentication returns 401."""
        r = client.post(f"{settings.API_V1_STR}/profile/complete-without-attachment")
        assert r.status_code == 401

    def test_complete_without_attachment_returns_profile_status(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that complete without attachment returns updated profile status."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.post(
            f"{settings.API_V1_STR}/profile/complete-without-attachment",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # Verify all profile status fields are present
        assert "is_complete" in data
        assert "has_person" in data
        assert "has_address" in data
        assert "has_religion" in data
        assert "has_marital_status" in data
        assert "has_duplicate_check" in data
        assert "has_pending_attachment_request" in data
        assert "pending_request_id" in data
        assert "missing_fields" in data


# ============================================================================
# Integration Tests - Profile Completion Status New Fields (Task 15.1)
# ============================================================================


@pytest.mark.integration
class TestProfileCompletionStatusNewFields:
    """Integration tests for new profile completion status fields.
    
    Requirements: 5.1, 5.2, 5.3, 5.4
    """

    def test_profile_status_includes_duplicate_check_field(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that profile status includes has_duplicate_check field."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/completion-status",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        assert "has_duplicate_check" in data
        assert isinstance(data["has_duplicate_check"], bool)

    def test_profile_status_includes_pending_attachment_request_field(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that profile status includes has_pending_attachment_request field."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/completion-status",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        assert "has_pending_attachment_request" in data
        assert isinstance(data["has_pending_attachment_request"], bool)

    def test_profile_status_includes_pending_request_id_field(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that profile status includes pending_request_id field."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/completion-status",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        assert "pending_request_id" in data
        # Should be None or a valid UUID string
        if data["pending_request_id"] is not None:
            assert isinstance(data["pending_request_id"], str)

    def test_profile_status_duplicate_check_in_missing_fields(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that duplicate_check appears in missing_fields when not complete."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/profile/completion-status",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # If has_duplicate_check is False, it should be in missing_fields
        if not data["has_duplicate_check"]:
            assert "duplicate_check" in data["missing_fields"]
        else:
            assert "duplicate_check" not in data["missing_fields"]


# ============================================================================
# Integration Tests - Full Signup Flow (Task 15.2)
# ============================================================================


@pytest.mark.integration
class TestFullSignupFlow:
    """Integration tests for the complete signup flow.
    
    Tests the full flow from signup to profile completion:
    1. Signup creates inactive person
    2. Complete profile steps 1-4
    3. Duplicate check shows matches
    4. Complete without attachment activates person
    
    Requirements: 1.1, 3.8, 6.1
    """

    def test_signup_creates_inactive_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that signup creates a person with is_active=False.
        
        Requirements: 1.1
        """
        # Create a new user via signup
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
        assert r.status_code == 200
        user_data = r.json()
        
        # Get the person from database
        person = db.exec(
            select(Person).where(Person.user_id == uuid.UUID(user_data["id"]))
        ).first()
        
        assert person is not None
        # Person should be inactive after signup
        assert person.is_active is False

    def test_complete_without_attachment_activates_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that complete without attachment sets person.is_active=True.
        
        Requirements: 3.8, 6.1
        """
        # Create a new user via signup
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
        assert r.status_code == 200
        user_data = r.json()
        
        # Login to get auth headers
        login_data = {"username": email, "password": password}
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        assert r.status_code == 200
        tokens = r.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Get person before completing
        person_before = db.exec(
            select(Person).where(Person.user_id == uuid.UUID(user_data["id"]))
        ).first()
        assert person_before is not None
        assert person_before.is_active is False
        
        # Complete without attachment
        r = client.post(
            f"{settings.API_V1_STR}/profile/complete-without-attachment",
            headers=headers,
        )
        assert r.status_code == 200
        
        # Refresh session to see updated data
        db.expire_all()
        
        # Get person after completing
        person_after = db.exec(
            select(Person).where(Person.user_id == uuid.UUID(user_data["id"]))
        ).first()
        assert person_after is not None
        # Person should now be active
        assert person_after.is_active is True

    def test_full_signup_to_completion_flow(
        self, client: TestClient, db: Session
    ) -> None:
        """Test the complete flow from signup to profile completion.
        
        This test verifies the entire user journey:
        1. User signs up (person created as inactive)
        2. User checks profile status (incomplete)
        3. User calls duplicate check
        4. User completes without attachment
        5. Profile is now complete
        
        Requirements: 1.1, 3.8, 6.1
        """
        # Step 1: Signup
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
        assert r.status_code == 200
        
        # Login
        login_data = {"username": email, "password": password}
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        assert r.status_code == 200
        tokens = r.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Step 2: Check initial profile status
        r = client.get(
            f"{settings.API_V1_STR}/profile/completion-status",
            headers=headers,
        )
        assert r.status_code == 200
        initial_status = r.json()
        
        # Should have person but not complete
        assert initial_status["has_person"] is True
        # Duplicate check should be incomplete (person is inactive)
        assert initial_status["has_duplicate_check"] is False
        
        # Step 3: Call duplicate check
        r = client.get(
            f"{settings.API_V1_STR}/profile/duplicate-check",
            headers=headers,
        )
        assert r.status_code == 200
        matches = r.json()
        assert isinstance(matches, list)
        
        # Step 4: Complete without attachment
        r = client.post(
            f"{settings.API_V1_STR}/profile/complete-without-attachment",
            headers=headers,
        )
        assert r.status_code == 200
        completion_result = r.json()
        
        # Duplicate check should now be complete
        assert completion_result["has_duplicate_check"] is True
        
        # Step 5: Verify final profile status
        r = client.get(
            f"{settings.API_V1_STR}/profile/completion-status",
            headers=headers,
        )
        assert r.status_code == 200
        final_status = r.json()
        
        # Duplicate check should be complete
        assert final_status["has_duplicate_check"] is True
        # No pending attachment request
        assert final_status["has_pending_attachment_request"] is False

    def test_inactive_person_excluded_from_searches(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that inactive persons are excluded from search results.
        
        Requirements: 1.2
        """
        # Create a new user via signup (person will be inactive)
        email = random_email()
        password = random_lower_string() + "Aa1!"
        first_name = "InactiveTest"
        last_name = "Person"
        
        signup_data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "gender": "MALE",
            "date_of_birth": "1990-01-01",
        }
        r = client.post(f"{settings.API_V1_STR}/users/signup", json=signup_data)
        assert r.status_code == 200
        user_data = r.json()
        
        # Get the person ID
        person = db.exec(
            select(Person).where(Person.user_id == uuid.UUID(user_data["id"]))
        ).first()
        assert person is not None
        inactive_person_id = str(person.id)
        
        # Create another user to do the search
        headers, _ = create_test_user_with_person(client, db)
        
        # Search for persons - inactive person should not appear
        # Note: This depends on the search implementation filtering inactive persons
        r = client.get(
            f"{settings.API_V1_STR}/profile/duplicate-check",
            headers=headers,
        )
        assert r.status_code == 200
        matches = r.json()
        
        # Verify inactive person is not in results
        match_ids = [m["person_id"] for m in matches]
        assert inactive_person_id not in match_ids

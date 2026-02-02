"""Integration tests for Attachment Requests API routes.

This module tests the Attachment Requests API endpoints including:
- Create attachment request (POST /)
- Get requests to approve (GET /to-approve)
- Get my pending request (GET /my-pending)
- Get pending count (GET /pending-count)
- Approve request (POST /{id}/approve)
- Deny request (POST /{id}/deny)
- Cancel request (POST /{id}/cancel)

Requirements: 3.7-3.9, 6.2-6.6, 7.2-7.6, 8.2-8.6
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.db_models.person.person import Person
from app.db_models.person.person_attachment_request import PersonAttachmentRequest
from app.enums.attachment_request_status import AttachmentRequestStatus
from tests.factories import UserFactory, PersonFactory
from tests.utils.user import user_authentication_headers


# ============================================================================
# Helper Functions
# ============================================================================


def create_test_user_with_auth(
    client: TestClient, db: Session
) -> tuple[dict[str, str], uuid.UUID]:
    """Create a test user and return auth headers and user ID."""
    user = UserFactory.create(db, password="testpassword123")
    headers = user_authentication_headers(
        client=client,
        email=user.email,
        password="testpassword123",
    )
    return headers, user.id


def create_requester_with_person(
    client: TestClient, db: Session
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID]:
    """Create a requester user with a person record.
    
    Returns: (headers, user_id, person_id)
    """
    user = UserFactory.create(db, password="testpassword123")
    person = PersonFactory.create_with_user(db, user, is_primary=True)
    # Set is_active to False for temp person
    person.is_active = False
    db.add(person)
    db.commit()
    db.refresh(person)
    headers = user_authentication_headers(
        client=client,
        email=user.email,
        password="testpassword123",
    )
    return headers, user.id, person.id


def create_approver_with_target_person(
    client: TestClient, db: Session
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID]:
    """Create an approver user with a target person (no user linked).
    
    Returns: (headers, user_id, target_person_id)
    """
    user = UserFactory.create(db, password="testpassword123")
    # Create a person without linking to any user (can be attached to)
    target_person = PersonFactory.create(
        db,
        created_by_user=user,
        user=None,  # No user linked
        is_primary=False,
    )
    headers = user_authentication_headers(
        client=client,
        email=user.email,
        password="testpassword123",
    )
    return headers, user.id, target_person.id


# ============================================================================
# Integration Tests - Create Attachment Request
# ============================================================================


@pytest.mark.integration
class TestCreateAttachmentRequest:
    """Integration tests for POST /attachment-requests/ endpoint."""

    def test_create_attachment_request_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating an attachment request with valid data."""
        # Create requester with person
        requester_headers, requester_user_id, requester_person_id = (
            create_requester_with_person(client, db)
        )
        
        # Create approver with target person
        _, approver_user_id, target_person_id = create_approver_with_target_person(
            client, db
        )

        request_data = {"target_person_id": str(target_person_id)}

        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["requester_user_id"] == str(requester_user_id)
        assert data["target_person_id"] == str(target_person_id)
        assert data["approver_user_id"] == str(approver_user_id)
        assert data["status"] == AttachmentRequestStatus.PENDING.value

    def test_create_attachment_request_without_auth(
        self, client: TestClient
    ) -> None:
        """Test creating request without authentication returns 401."""
        request_data = {"target_person_id": str(uuid.uuid4())}

        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            json=request_data,
        )

        assert r.status_code == 401

    def test_create_attachment_request_no_person_record(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating request when requester has no person record returns 400."""
        # Create user without person record
        headers, _ = create_test_user_with_auth(client, db)
        
        request_data = {"target_person_id": str(uuid.uuid4())}

        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=headers,
            json=request_data,
        )

        assert r.status_code == 400
        assert "complete your profile" in r.json()["detail"]

    def test_create_attachment_request_target_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating request with non-existent target returns 404."""
        requester_headers, _, _ = create_requester_with_person(client, db)
        
        request_data = {"target_person_id": str(uuid.uuid4())}

        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )

        assert r.status_code == 404
        assert "not found" in r.json()["detail"]

    def test_create_attachment_request_target_already_linked(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating request when target already has user linked returns 400."""
        requester_headers, _, _ = create_requester_with_person(client, db)
        
        # Create another user with a person (already linked)
        other_user = UserFactory.create(db, password="testpassword123")
        linked_person = PersonFactory.create_with_user(db, other_user)
        
        request_data = {"target_person_id": str(linked_person.id)}

        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )

        assert r.status_code == 400
        assert "already linked" in r.json()["detail"]

    def test_create_attachment_request_duplicate_pending(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating request when already has pending request returns 400."""
        requester_headers, requester_user_id, requester_person_id = (
            create_requester_with_person(client, db)
        )
        _, approver_user_id, target_person_id = create_approver_with_target_person(
            client, db
        )

        # Create first request
        request_data = {"target_person_id": str(target_person_id)}
        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )
        assert r.status_code == 200

        # Create another target person
        approver_user = db.get(UserFactory.create(db).__class__, approver_user_id)
        if approver_user:
            another_target = PersonFactory.create(
                db, created_by_user=approver_user, user=None
            )
            
            # Try to create second request
            request_data2 = {"target_person_id": str(another_target.id)}
            r2 = client.post(
                f"{settings.API_V1_STR}/attachment-requests/",
                headers=requester_headers,
                json=request_data2,
            )

            assert r2.status_code == 400
            assert "already have a pending" in r2.json()["detail"]



# ============================================================================
# Integration Tests - Get Requests to Approve
# ============================================================================


@pytest.mark.integration
class TestGetRequestsToApprove:
    """Integration tests for GET /attachment-requests/to-approve endpoint."""

    def test_get_requests_to_approve_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting pending requests for approver."""
        # Create requester with person
        requester_headers, requester_user_id, requester_person_id = (
            create_requester_with_person(client, db)
        )
        
        # Create approver with target person
        approver_headers, approver_user_id, target_person_id = (
            create_approver_with_target_person(client, db)
        )

        # Create attachment request
        request_data = {"target_person_id": str(target_person_id)}
        client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )

        # Get requests to approve
        r = client.get(
            f"{settings.API_V1_STR}/attachment-requests/to-approve",
            headers=approver_headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Verify the request details
        request = data[0]
        assert "requester_first_name" in request
        assert "target_first_name" in request
        assert request["status"] == AttachmentRequestStatus.PENDING.value

    def test_get_requests_to_approve_empty(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting requests when none exist returns empty list."""
        headers, _ = create_test_user_with_auth(client, db)

        r = client.get(
            f"{settings.API_V1_STR}/attachment-requests/to-approve",
            headers=headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_requests_to_approve_without_auth(
        self, client: TestClient
    ) -> None:
        """Test getting requests without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/attachment-requests/to-approve")
        assert r.status_code == 401


# ============================================================================
# Integration Tests - Get My Pending Request
# ============================================================================


@pytest.mark.integration
class TestGetMyPendingRequest:
    """Integration tests for GET /attachment-requests/my-pending endpoint."""

    def test_get_my_pending_request_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting requester's pending request."""
        # Create requester with person
        requester_headers, _, _ = create_requester_with_person(client, db)
        
        # Create approver with target person
        _, _, target_person_id = create_approver_with_target_person(client, db)

        # Create attachment request
        request_data = {"target_person_id": str(target_person_id)}
        client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )

        # Get my pending request
        r = client.get(
            f"{settings.API_V1_STR}/attachment-requests/my-pending",
            headers=requester_headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["status"] == AttachmentRequestStatus.PENDING.value
        assert "target_first_name" in data
        assert "target_date_of_birth" in data

    def test_get_my_pending_request_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting pending request when none exists returns 404."""
        requester_headers, _, _ = create_requester_with_person(client, db)

        r = client.get(
            f"{settings.API_V1_STR}/attachment-requests/my-pending",
            headers=requester_headers,
        )

        assert r.status_code == 404
        assert "No pending" in r.json()["detail"]

    def test_get_my_pending_request_without_auth(
        self, client: TestClient
    ) -> None:
        """Test getting pending request without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/attachment-requests/my-pending")
        assert r.status_code == 401


# ============================================================================
# Integration Tests - Get Pending Count
# ============================================================================


@pytest.mark.integration
class TestGetPendingCount:
    """Integration tests for GET /attachment-requests/pending-count endpoint."""

    def test_get_pending_count_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting pending count for approver."""
        # Create requester with person
        requester_headers, _, _ = create_requester_with_person(client, db)
        
        # Create approver with target person
        approver_headers, _, target_person_id = create_approver_with_target_person(
            client, db
        )

        # Create attachment request
        request_data = {"target_person_id": str(target_person_id)}
        client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )

        # Get pending count
        r = client.get(
            f"{settings.API_V1_STR}/attachment-requests/pending-count",
            headers=approver_headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["count"] >= 1

    def test_get_pending_count_zero(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting pending count when none exist returns zero."""
        headers, _ = create_test_user_with_auth(client, db)

        r = client.get(
            f"{settings.API_V1_STR}/attachment-requests/pending-count",
            headers=headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["count"] == 0

    def test_get_pending_count_without_auth(
        self, client: TestClient
    ) -> None:
        """Test getting pending count without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/attachment-requests/pending-count")
        assert r.status_code == 401


# ============================================================================
# Integration Tests - Approve Request
# ============================================================================


@pytest.mark.integration
class TestApproveAttachmentRequest:
    """Integration tests for POST /attachment-requests/{id}/approve endpoint."""

    def test_approve_request_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test approving an attachment request."""
        # Create requester with person
        requester_headers, requester_user_id, requester_person_id = (
            create_requester_with_person(client, db)
        )
        
        # Create approver with target person
        approver_headers, approver_user_id, target_person_id = (
            create_approver_with_target_person(client, db)
        )

        # Create attachment request
        request_data = {"target_person_id": str(target_person_id)}
        create_response = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )
        request_id = create_response.json()["id"]

        # Approve the request
        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{request_id}/approve",
            headers=approver_headers,
        )

        assert r.status_code == 200
        assert "approved" in r.json()["message"].lower()

        # Verify target person is now linked to requester user
        target_person = db.get(Person, target_person_id)
        assert target_person is not None
        assert target_person.user_id == requester_user_id
        assert target_person.is_primary is True

    def test_approve_request_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test approving non-existent request returns 404."""
        headers, _ = create_test_user_with_auth(client, db)
        non_existent_id = uuid.uuid4()

        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{non_existent_id}/approve",
            headers=headers,
        )

        assert r.status_code == 404
        assert "not found" in r.json()["detail"]

    def test_approve_request_not_authorized(
        self, client: TestClient, db: Session
    ) -> None:
        """Test approving request by non-approver returns 403."""
        # Create requester with person
        requester_headers, _, _ = create_requester_with_person(client, db)
        
        # Create approver with target person
        _, _, target_person_id = create_approver_with_target_person(client, db)

        # Create attachment request
        request_data = {"target_person_id": str(target_person_id)}
        create_response = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )
        request_id = create_response.json()["id"]

        # Create another user and try to approve
        other_headers, _ = create_test_user_with_auth(client, db)
        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{request_id}/approve",
            headers=other_headers,
        )

        assert r.status_code == 403
        assert "not authorized" in r.json()["detail"]

    def test_approve_request_without_auth(
        self, client: TestClient
    ) -> None:
        """Test approving request without authentication returns 401."""
        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{uuid.uuid4()}/approve"
        )
        assert r.status_code == 401



# ============================================================================
# Integration Tests - Deny Request
# ============================================================================


@pytest.mark.integration
class TestDenyAttachmentRequest:
    """Integration tests for POST /attachment-requests/{id}/deny endpoint."""

    def test_deny_request_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test denying an attachment request."""
        # Create requester with person
        requester_headers, requester_user_id, requester_person_id = (
            create_requester_with_person(client, db)
        )
        
        # Create approver with target person
        approver_headers, _, target_person_id = create_approver_with_target_person(
            client, db
        )

        # Create attachment request
        request_data = {"target_person_id": str(target_person_id)}
        create_response = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )
        request_id = create_response.json()["id"]

        # Deny the request
        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{request_id}/deny",
            headers=approver_headers,
        )

        assert r.status_code == 200
        assert "denied" in r.json()["message"].lower()

    def test_deny_request_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test denying non-existent request returns 404."""
        headers, _ = create_test_user_with_auth(client, db)
        non_existent_id = uuid.uuid4()

        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{non_existent_id}/deny",
            headers=headers,
        )

        assert r.status_code == 404
        assert "not found" in r.json()["detail"]

    def test_deny_request_not_authorized(
        self, client: TestClient, db: Session
    ) -> None:
        """Test denying request by non-approver returns 403."""
        # Create requester with person
        requester_headers, _, _ = create_requester_with_person(client, db)
        
        # Create approver with target person
        _, _, target_person_id = create_approver_with_target_person(client, db)

        # Create attachment request
        request_data = {"target_person_id": str(target_person_id)}
        create_response = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )
        request_id = create_response.json()["id"]

        # Create another user and try to deny
        other_headers, _ = create_test_user_with_auth(client, db)
        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{request_id}/deny",
            headers=other_headers,
        )

        assert r.status_code == 403
        assert "not authorized" in r.json()["detail"]

    def test_deny_request_without_auth(
        self, client: TestClient
    ) -> None:
        """Test denying request without authentication returns 401."""
        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{uuid.uuid4()}/deny"
        )
        assert r.status_code == 401


# ============================================================================
# Integration Tests - Cancel Request
# ============================================================================


@pytest.mark.integration
class TestCancelAttachmentRequest:
    """Integration tests for POST /attachment-requests/{id}/cancel endpoint."""

    def test_cancel_request_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test cancelling an attachment request."""
        # Create requester with person
        requester_headers, _, _ = create_requester_with_person(client, db)
        
        # Create approver with target person
        _, _, target_person_id = create_approver_with_target_person(client, db)

        # Create attachment request
        request_data = {"target_person_id": str(target_person_id)}
        create_response = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )
        request_id = create_response.json()["id"]

        # Cancel the request
        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{request_id}/cancel",
            headers=requester_headers,
        )

        assert r.status_code == 200
        assert "cancelled" in r.json()["message"].lower()

        # Verify request is cancelled
        request = db.get(PersonAttachmentRequest, uuid.UUID(request_id))
        assert request is not None
        assert request.status == AttachmentRequestStatus.CANCELLED

    def test_cancel_request_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test cancelling non-existent request returns 404."""
        headers, _ = create_test_user_with_auth(client, db)
        non_existent_id = uuid.uuid4()

        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{non_existent_id}/cancel",
            headers=headers,
        )

        assert r.status_code == 404
        assert "not found" in r.json()["detail"]

    def test_cancel_request_not_authorized(
        self, client: TestClient, db: Session
    ) -> None:
        """Test cancelling request by non-requester returns 403."""
        # Create requester with person
        requester_headers, _, _ = create_requester_with_person(client, db)
        
        # Create approver with target person
        approver_headers, _, target_person_id = create_approver_with_target_person(
            client, db
        )

        # Create attachment request
        request_data = {"target_person_id": str(target_person_id)}
        create_response = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )
        request_id = create_response.json()["id"]

        # Approver tries to cancel (should fail - only requester can cancel)
        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{request_id}/cancel",
            headers=approver_headers,
        )

        assert r.status_code == 403
        assert "only cancel your own" in r.json()["detail"]

    def test_cancel_request_already_resolved(
        self, client: TestClient, db: Session
    ) -> None:
        """Test cancelling already resolved request returns 400."""
        # Create requester with person
        requester_headers, _, _ = create_requester_with_person(client, db)
        
        # Create approver with target person
        approver_headers, _, target_person_id = create_approver_with_target_person(
            client, db
        )

        # Create attachment request
        request_data = {"target_person_id": str(target_person_id)}
        create_response = client.post(
            f"{settings.API_V1_STR}/attachment-requests/",
            headers=requester_headers,
            json=request_data,
        )
        request_id = create_response.json()["id"]

        # Cancel the request first
        client.post(
            f"{settings.API_V1_STR}/attachment-requests/{request_id}/cancel",
            headers=requester_headers,
        )

        # Try to cancel again
        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{request_id}/cancel",
            headers=requester_headers,
        )

        assert r.status_code == 400
        assert "already been resolved" in r.json()["detail"]

    def test_cancel_request_without_auth(
        self, client: TestClient
    ) -> None:
        """Test cancelling request without authentication returns 401."""
        r = client.post(
            f"{settings.API_V1_STR}/attachment-requests/{uuid.uuid4()}/cancel"
        )
        assert r.status_code == 401

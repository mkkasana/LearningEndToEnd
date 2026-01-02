"""Integration tests for Support Tickets API routes.

This module tests the Support Tickets API endpoints including:
- Ticket CRUD operations (Task 21.1)
- Admin ticket management (Task 21.2)

Tests use dynamically created test data with proper cleanup.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.support_ticket import SupportTicket
from app.schemas.support_ticket import IssueStatus, IssueType
from tests.factories import UserFactory
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


def create_test_superuser_with_auth(
    client: TestClient, db: Session
) -> tuple[dict[str, str], uuid.UUID]:
    """Create a test superuser and return auth headers and user ID."""
    user = UserFactory.create_superuser(db, password="adminpassword123")
    headers = user_authentication_headers(
        client=client,
        email=user.email,
        password="adminpassword123",
    )
    return headers, user.id


# ============================================================================
# Integration Tests - Ticket CRUD (Task 21.1)
# ============================================================================


@pytest.mark.integration
class TestCreateSupportTicket:
    """Integration tests for POST /support-tickets/ endpoint."""

    def test_create_support_ticket_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating a support ticket with valid data."""
        headers, user_id = create_test_user_with_auth(client, db)

        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Test Bug Report",
            "description": "This is a test bug description for integration testing.",
        }

        r = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers,
            json=ticket_data,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Test Bug Report"
        assert data["description"] == "This is a test bug description for integration testing."
        assert data["issue_type"] == IssueType.BUG.value
        assert data["status"] == IssueStatus.OPEN.value
        assert data["user_id"] == str(user_id)
        assert data["resolved_by_user_id"] is None
        assert data["resolved_at"] is None

    def test_create_support_ticket_feature_request(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating a feature request ticket."""
        headers, _ = create_test_user_with_auth(client, db)

        ticket_data = {
            "issue_type": IssueType.FEATURE_REQUEST.value,
            "title": "New Feature Request",
            "description": "Please add this amazing feature to the application.",
        }

        r = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers,
            json=ticket_data,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["issue_type"] == IssueType.FEATURE_REQUEST.value

    def test_create_support_ticket_without_auth(
        self, client: TestClient
    ) -> None:
        """Test creating a ticket without authentication returns 401."""
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Unauthorized Ticket",
            "description": "This should fail.",
        }

        r = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            json=ticket_data,
        )

        assert r.status_code == 401

    def test_create_support_ticket_missing_title(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating a ticket without title returns 422."""
        headers, _ = create_test_user_with_auth(client, db)

        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "description": "Missing title field.",
        }

        r = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers,
            json=ticket_data,
        )

        assert r.status_code == 422

    def test_create_support_ticket_missing_description(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating a ticket without description returns 422."""
        headers, _ = create_test_user_with_auth(client, db)

        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Missing Description",
        }

        r = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers,
            json=ticket_data,
        )

        assert r.status_code == 422


@pytest.mark.integration
class TestGetMySupportTickets:
    """Integration tests for GET /support-tickets/me endpoint."""

    def test_get_my_support_tickets_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting current user's support tickets."""
        headers, user_id = create_test_user_with_auth(client, db)

        # Create a ticket first
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "My Test Ticket",
            "description": "Test description for my ticket.",
        }
        client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers,
            json=ticket_data,
        )

        # Get user's tickets
        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/me",
            headers=headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert "data" in data
        assert "count" in data
        assert data["count"] >= 1
        assert len(data["data"]) >= 1
        # Verify the ticket belongs to the user
        assert all(t["user_id"] == str(user_id) for t in data["data"])

    def test_get_my_support_tickets_with_status_filter(
        self, client: TestClient, db: Session
    ) -> None:
        """Test filtering tickets by status."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a ticket
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Filtered Ticket",
            "description": "Test description.",
        }
        client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers,
            json=ticket_data,
        )

        # Get only open tickets
        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/me",
            headers=headers,
            params={"status": IssueStatus.OPEN.value},
        )

        assert r.status_code == 200
        data = r.json()
        # All returned tickets should be open
        assert all(t["status"] == IssueStatus.OPEN.value for t in data["data"])

    def test_get_my_support_tickets_pagination(
        self, client: TestClient, db: Session
    ) -> None:
        """Test pagination of support tickets."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create multiple tickets
        for i in range(3):
            ticket_data = {
                "issue_type": IssueType.BUG.value,
                "title": f"Pagination Test Ticket {i}",
                "description": f"Test description {i}.",
            }
            client.post(
                f"{settings.API_V1_STR}/support-tickets/",
                headers=headers,
                json=ticket_data,
            )

        # Get with pagination
        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/me",
            headers=headers,
            params={"skip": 0, "limit": 2},
        )

        assert r.status_code == 200
        data = r.json()
        assert len(data["data"]) <= 2

    def test_get_my_support_tickets_without_auth(
        self, client: TestClient
    ) -> None:
        """Test getting tickets without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/support-tickets/me")
        assert r.status_code == 401


@pytest.mark.integration
class TestGetSupportTicketById:
    """Integration tests for GET /support-tickets/{ticket_id} endpoint."""

    def test_get_support_ticket_by_id_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting a specific support ticket by ID."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a ticket
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Get By ID Test",
            "description": "Test description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Get the ticket by ID
        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}",
            headers=headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["id"] == ticket_id
        assert data["title"] == "Get By ID Test"

    def test_get_support_ticket_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting non-existent ticket returns 404."""
        headers, _ = create_test_user_with_auth(client, db)
        non_existent_id = uuid.uuid4()

        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/{non_existent_id}",
            headers=headers,
        )

        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_support_ticket_other_user_forbidden(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting another user's ticket returns 403."""
        # Create first user and their ticket
        headers1, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "User 1 Ticket",
            "description": "Test description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers1,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Create second user and try to access first user's ticket
        headers2, _ = create_test_user_with_auth(client, db)
        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}",
            headers=headers2,
        )

        assert r.status_code == 403
        assert "permission" in r.json()["detail"].lower()

    def test_get_support_ticket_admin_can_access(
        self, client: TestClient, db: Session
    ) -> None:
        """Test admin can access any user's ticket."""
        # Create regular user and their ticket
        user_headers, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "User Ticket for Admin",
            "description": "Test description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=user_headers,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Admin should be able to access
        admin_headers, _ = create_test_superuser_with_auth(client, db)
        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}",
            headers=admin_headers,
        )

        assert r.status_code == 200
        assert r.json()["id"] == ticket_id

    def test_get_support_ticket_without_auth(
        self, client: TestClient
    ) -> None:
        """Test getting ticket without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/support-tickets/{uuid.uuid4()}")
        assert r.status_code == 401


@pytest.mark.integration
class TestUpdateSupportTicket:
    """Integration tests for PATCH /support-tickets/{ticket_id} endpoint."""

    def test_update_support_ticket_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating a support ticket."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a ticket
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Original Title",
            "description": "Original description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Update the ticket
        update_data = {
            "title": "Updated Title",
            "description": "Updated description.",
        }
        r = client.patch(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}",
            headers=headers,
            json=update_data,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated description."

    def test_update_support_ticket_partial(
        self, client: TestClient, db: Session
    ) -> None:
        """Test partial update of a support ticket."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a ticket
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Original Title",
            "description": "Original description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Update only the title
        update_data = {"title": "Only Title Updated"}
        r = client.patch(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}",
            headers=headers,
            json=update_data,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Only Title Updated"
        assert data["description"] == "Original description."  # Unchanged

    def test_update_support_ticket_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating non-existent ticket returns 404."""
        headers, _ = create_test_user_with_auth(client, db)
        non_existent_id = uuid.uuid4()

        update_data = {"title": "Updated Title"}
        r = client.patch(
            f"{settings.API_V1_STR}/support-tickets/{non_existent_id}",
            headers=headers,
            json=update_data,
        )

        assert r.status_code == 404

    def test_update_support_ticket_other_user_forbidden(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating another user's ticket returns 403."""
        # Create first user and their ticket
        headers1, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "User 1 Ticket",
            "description": "Test description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers1,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Create second user and try to update first user's ticket
        headers2, _ = create_test_user_with_auth(client, db)
        update_data = {"title": "Hacked Title"}
        r = client.patch(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}",
            headers=headers2,
            json=update_data,
        )

        assert r.status_code == 403

    def test_update_support_ticket_without_auth(
        self, client: TestClient
    ) -> None:
        """Test updating ticket without authentication returns 401."""
        update_data = {"title": "Updated Title"}
        r = client.patch(
            f"{settings.API_V1_STR}/support-tickets/{uuid.uuid4()}",
            json=update_data,
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestDeleteSupportTicket:
    """Integration tests for DELETE /support-tickets/{ticket_id} endpoint."""

    def test_delete_support_ticket_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting a support ticket."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a ticket
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Ticket to Delete",
            "description": "This ticket will be deleted.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Delete the ticket
        r = client.delete(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}",
            headers=headers,
        )

        assert r.status_code == 200
        assert "deleted" in r.json()["message"].lower()

        # Verify ticket is deleted
        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}",
            headers=headers,
        )
        assert r.status_code == 404

    def test_delete_support_ticket_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting non-existent ticket returns 404."""
        headers, _ = create_test_user_with_auth(client, db)
        non_existent_id = uuid.uuid4()

        r = client.delete(
            f"{settings.API_V1_STR}/support-tickets/{non_existent_id}",
            headers=headers,
        )

        assert r.status_code == 404

    def test_delete_support_ticket_other_user_forbidden(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting another user's ticket returns 403."""
        # Create first user and their ticket
        headers1, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "User 1 Ticket",
            "description": "Test description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=headers1,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Create second user and try to delete first user's ticket
        headers2, _ = create_test_user_with_auth(client, db)
        r = client.delete(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}",
            headers=headers2,
        )

        assert r.status_code == 403

    def test_delete_support_ticket_admin_can_delete(
        self, client: TestClient, db: Session
    ) -> None:
        """Test admin can delete any user's ticket."""
        # Create regular user and their ticket
        user_headers, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "User Ticket for Admin Delete",
            "description": "Test description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=user_headers,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Admin should be able to delete
        admin_headers, _ = create_test_superuser_with_auth(client, db)
        r = client.delete(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}",
            headers=admin_headers,
        )

        assert r.status_code == 200

    def test_delete_support_ticket_without_auth(
        self, client: TestClient
    ) -> None:
        """Test deleting ticket without authentication returns 401."""
        r = client.delete(f"{settings.API_V1_STR}/support-tickets/{uuid.uuid4()}")
        assert r.status_code == 401



# ============================================================================
# Integration Tests - Admin Ticket Management (Task 21.2)
# ============================================================================


@pytest.mark.integration
class TestGetAllSupportTicketsAdmin:
    """Integration tests for GET /support-tickets/admin/all endpoint."""

    def test_get_all_support_tickets_admin_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test admin can get all support tickets."""
        # Create a regular user and their ticket
        user_headers, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "User Ticket for Admin View",
            "description": "Test description.",
        }
        client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=user_headers,
            json=ticket_data,
        )

        # Admin gets all tickets
        admin_headers, _ = create_test_superuser_with_auth(client, db)
        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/admin/all",
            headers=admin_headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Verify response includes user information
        ticket = data[0]
        assert "user_email" in ticket
        assert "user_full_name" in ticket
        assert "resolved_by_email" in ticket

    def test_get_all_support_tickets_admin_with_status_filter(
        self, client: TestClient, db: Session
    ) -> None:
        """Test admin can filter tickets by status."""
        # Create a ticket
        user_headers, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Open Ticket for Filter",
            "description": "Test description.",
        }
        client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=user_headers,
            json=ticket_data,
        )

        # Admin filters by open status
        admin_headers, _ = create_test_superuser_with_auth(client, db)
        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/admin/all",
            headers=admin_headers,
            params={"status": IssueStatus.OPEN.value},
        )

        assert r.status_code == 200
        data = r.json()
        # All returned tickets should be open
        assert all(t["status"] == IssueStatus.OPEN.value for t in data)

    def test_get_all_support_tickets_admin_with_issue_type_filter(
        self, client: TestClient, db: Session
    ) -> None:
        """Test admin can filter tickets by issue type."""
        # Create a bug ticket
        user_headers, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Bug Ticket for Filter",
            "description": "Test description.",
        }
        client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=user_headers,
            json=ticket_data,
        )

        # Admin filters by bug type
        admin_headers, _ = create_test_superuser_with_auth(client, db)
        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/admin/all",
            headers=admin_headers,
            params={"issue_type": IssueType.BUG.value},
        )

        assert r.status_code == 200
        data = r.json()
        # All returned tickets should be bugs
        assert all(t["issue_type"] == IssueType.BUG.value for t in data)

    def test_get_all_support_tickets_admin_pagination(
        self, client: TestClient, db: Session
    ) -> None:
        """Test admin can paginate tickets."""
        # Create multiple tickets
        user_headers, _ = create_test_user_with_auth(client, db)
        for i in range(3):
            ticket_data = {
                "issue_type": IssueType.BUG.value,
                "title": f"Admin Pagination Ticket {i}",
                "description": f"Test description {i}.",
            }
            client.post(
                f"{settings.API_V1_STR}/support-tickets/",
                headers=user_headers,
                json=ticket_data,
            )

        # Admin gets with pagination
        admin_headers, _ = create_test_superuser_with_auth(client, db)
        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/admin/all",
            headers=admin_headers,
            params={"skip": 0, "limit": 2},
        )

        assert r.status_code == 200
        data = r.json()
        assert len(data) <= 2

    def test_get_all_support_tickets_admin_non_admin_forbidden(
        self, client: TestClient, db: Session
    ) -> None:
        """Test non-admin cannot access admin endpoint."""
        user_headers, _ = create_test_user_with_auth(client, db)

        r = client.get(
            f"{settings.API_V1_STR}/support-tickets/admin/all",
            headers=user_headers,
        )

        assert r.status_code == 403

    def test_get_all_support_tickets_admin_without_auth(
        self, client: TestClient
    ) -> None:
        """Test accessing admin endpoint without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/support-tickets/admin/all")
        assert r.status_code == 401


@pytest.mark.integration
class TestResolveSupportTicket:
    """Integration tests for PATCH /support-tickets/{ticket_id}/resolve endpoint."""

    def test_resolve_support_ticket_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test admin can resolve a support ticket."""
        # Create a ticket
        user_headers, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Ticket to Resolve",
            "description": "Test description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=user_headers,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Admin resolves the ticket
        admin_headers, admin_id = create_test_superuser_with_auth(client, db)
        r = client.patch(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}/resolve",
            headers=admin_headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["status"] == IssueStatus.CLOSED.value
        assert data["resolved_by_user_id"] == str(admin_id)
        assert data["resolved_at"] is not None

    def test_resolve_support_ticket_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test resolving non-existent ticket returns 404."""
        admin_headers, _ = create_test_superuser_with_auth(client, db)
        non_existent_id = uuid.uuid4()

        r = client.patch(
            f"{settings.API_V1_STR}/support-tickets/{non_existent_id}/resolve",
            headers=admin_headers,
        )

        assert r.status_code == 404

    def test_resolve_support_ticket_non_admin_forbidden(
        self, client: TestClient, db: Session
    ) -> None:
        """Test non-admin cannot resolve tickets."""
        # Create a ticket
        user_headers, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Ticket for Non-Admin Resolve",
            "description": "Test description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=user_headers,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Non-admin tries to resolve
        r = client.patch(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}/resolve",
            headers=user_headers,
        )

        assert r.status_code == 403


@pytest.mark.integration
class TestReopenSupportTicket:
    """Integration tests for PATCH /support-tickets/{ticket_id}/reopen endpoint."""

    def test_reopen_support_ticket_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test admin can reopen a closed support ticket."""
        # Create and resolve a ticket
        user_headers, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Ticket to Reopen",
            "description": "Test description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=user_headers,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Admin resolves the ticket first
        admin_headers, _ = create_test_superuser_with_auth(client, db)
        client.patch(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}/resolve",
            headers=admin_headers,
        )

        # Admin reopens the ticket
        r = client.patch(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}/reopen",
            headers=admin_headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["status"] == IssueStatus.OPEN.value
        assert data["resolved_by_user_id"] is None
        assert data["resolved_at"] is None

    def test_reopen_support_ticket_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test reopening non-existent ticket returns 404."""
        admin_headers, _ = create_test_superuser_with_auth(client, db)
        non_existent_id = uuid.uuid4()

        r = client.patch(
            f"{settings.API_V1_STR}/support-tickets/{non_existent_id}/reopen",
            headers=admin_headers,
        )

        assert r.status_code == 404

    def test_reopen_support_ticket_non_admin_forbidden(
        self, client: TestClient, db: Session
    ) -> None:
        """Test non-admin cannot reopen tickets."""
        # Create a ticket
        user_headers, _ = create_test_user_with_auth(client, db)
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": "Ticket for Non-Admin Reopen",
            "description": "Test description.",
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/support-tickets/",
            headers=user_headers,
            json=ticket_data,
        )
        ticket_id = create_response.json()["id"]

        # Non-admin tries to reopen
        r = client.patch(
            f"{settings.API_V1_STR}/support-tickets/{ticket_id}/reopen",
            headers=user_headers,
        )

        assert r.status_code == 403

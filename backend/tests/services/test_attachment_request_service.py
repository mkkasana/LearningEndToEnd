"""Unit tests for AttachmentRequestService.

Tests cover:
- create_request validations
- approve/deny/cancel logic
- cascade deletion

Requirements: 3.7-3.9, 6.2-6.4, 7.2-7.4, 8.2-8.4
"""

import uuid
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.db_models.person.person import Person
from app.db_models.person.person_attachment_request import PersonAttachmentRequest
from app.enums.attachment_request_status import AttachmentRequestStatus
from app.models import User
from app.schemas.attachment_request import AttachmentRequestCreate
from app.services.attachment_request_service import AttachmentRequestService


# ============================================================================
# Unit Tests for create_request
# ============================================================================


@pytest.mark.unit
class TestAttachmentRequestServiceCreateRequest:
    """Unit tests for create_request method."""

    def test_create_request_success(self, mock_session: MagicMock) -> None:
        """Test successful creation of attachment request."""
        requester_user_id = uuid.uuid4()
        target_person_id = uuid.uuid4()
        requester_person_id = uuid.uuid4()
        approver_user_id = uuid.uuid4()

        requester_person = Person(
            id=requester_person_id,
            user_id=requester_user_id,
            created_by_user_id=requester_user_id,
            first_name="Requester",
            last_name="Person",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 1),
        )

        target_person = Person(
            id=target_person_id,
            user_id=None,  # No user linked
            created_by_user_id=approver_user_id,
            first_name="Target",
            last_name="Person",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 1),
        )

        created_request = PersonAttachmentRequest(
            id=uuid.uuid4(),
            requester_user_id=requester_user_id,
            requester_person_id=requester_person_id,
            target_person_id=target_person_id,
            approver_user_id=approver_user_id,
            status=AttachmentRequestStatus.PENDING,
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=requester_person
        ), patch.object(
            service.request_repo, "get_pending_by_requester", return_value=None
        ), patch.object(
            service.person_repo, "get_by_id", return_value=target_person
        ), patch.object(
            service.request_repo, "create", return_value=created_request
        ):
            request_in = AttachmentRequestCreate(target_person_id=target_person_id)
            result = service.create_request(requester_user_id, request_in)

            assert result.id == created_request.id
            assert result.status == AttachmentRequestStatus.PENDING

    def test_create_request_no_person_record(self, mock_session: MagicMock) -> None:
        """Test create_request fails when requester has no person record."""
        requester_user_id = uuid.uuid4()
        target_person_id = uuid.uuid4()

        service = AttachmentRequestService(mock_session)

        with patch.object(service.person_repo, "get_by_user_id", return_value=None):
            request_in = AttachmentRequestCreate(target_person_id=target_person_id)

            with pytest.raises(HTTPException) as exc_info:
                service.create_request(requester_user_id, request_in)

            assert exc_info.value.status_code == 400
            assert "complete your profile" in exc_info.value.detail

    def test_create_request_existing_pending_request(
        self, mock_session: MagicMock
    ) -> None:
        """Test create_request fails when requester has existing pending request."""
        requester_user_id = uuid.uuid4()
        target_person_id = uuid.uuid4()

        requester_person = Person(
            id=uuid.uuid4(),
            user_id=requester_user_id,
            created_by_user_id=requester_user_id,
            first_name="Requester",
            last_name="Person",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 1),
        )

        existing_request = PersonAttachmentRequest(
            id=uuid.uuid4(),
            requester_user_id=requester_user_id,
            requester_person_id=requester_person.id,
            target_person_id=uuid.uuid4(),
            approver_user_id=uuid.uuid4(),
            status=AttachmentRequestStatus.PENDING,
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=requester_person
        ), patch.object(
            service.request_repo, "get_pending_by_requester", return_value=existing_request
        ):
            request_in = AttachmentRequestCreate(target_person_id=target_person_id)

            with pytest.raises(HTTPException) as exc_info:
                service.create_request(requester_user_id, request_in)

            assert exc_info.value.status_code == 400
            assert "already have a pending" in exc_info.value.detail

    def test_create_request_target_not_found(self, mock_session: MagicMock) -> None:
        """Test create_request fails when target person not found."""
        requester_user_id = uuid.uuid4()
        target_person_id = uuid.uuid4()

        requester_person = Person(
            id=uuid.uuid4(),
            user_id=requester_user_id,
            created_by_user_id=requester_user_id,
            first_name="Requester",
            last_name="Person",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 1),
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=requester_person
        ), patch.object(
            service.request_repo, "get_pending_by_requester", return_value=None
        ), patch.object(
            service.person_repo, "get_by_id", return_value=None
        ):
            request_in = AttachmentRequestCreate(target_person_id=target_person_id)

            with pytest.raises(HTTPException) as exc_info:
                service.create_request(requester_user_id, request_in)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail

    def test_create_request_target_already_linked(self, mock_session: MagicMock) -> None:
        """Test create_request fails when target person already has user linked."""
        requester_user_id = uuid.uuid4()
        target_person_id = uuid.uuid4()

        requester_person = Person(
            id=uuid.uuid4(),
            user_id=requester_user_id,
            created_by_user_id=requester_user_id,
            first_name="Requester",
            last_name="Person",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 1),
        )

        target_person = Person(
            id=target_person_id,
            user_id=uuid.uuid4(),  # Already has user linked
            created_by_user_id=uuid.uuid4(),
            first_name="Target",
            last_name="Person",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 1),
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=requester_person
        ), patch.object(
            service.request_repo, "get_pending_by_requester", return_value=None
        ), patch.object(
            service.person_repo, "get_by_id", return_value=target_person
        ):
            request_in = AttachmentRequestCreate(target_person_id=target_person_id)

            with pytest.raises(HTTPException) as exc_info:
                service.create_request(requester_user_id, request_in)

            assert exc_info.value.status_code == 400
            assert "already linked" in exc_info.value.detail

    def test_create_request_cannot_attach_to_own_creation(
        self, mock_session: MagicMock
    ) -> None:
        """Test create_request fails when target was created by requester."""
        requester_user_id = uuid.uuid4()
        target_person_id = uuid.uuid4()

        requester_person = Person(
            id=uuid.uuid4(),
            user_id=requester_user_id,
            created_by_user_id=requester_user_id,
            first_name="Requester",
            last_name="Person",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 1),
        )

        target_person = Person(
            id=target_person_id,
            user_id=None,
            created_by_user_id=requester_user_id,  # Created by requester
            first_name="Target",
            last_name="Person",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 1),
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=requester_person
        ), patch.object(
            service.request_repo, "get_pending_by_requester", return_value=None
        ), patch.object(
            service.person_repo, "get_by_id", return_value=target_person
        ):
            request_in = AttachmentRequestCreate(target_person_id=target_person_id)

            with pytest.raises(HTTPException) as exc_info:
                service.create_request(requester_user_id, request_in)

            assert exc_info.value.status_code == 400
            assert "cannot attach to a person you created" in exc_info.value.detail



# ============================================================================
# Unit Tests for approve_request
# ============================================================================


@pytest.mark.unit
class TestAttachmentRequestServiceApproveRequest:
    """Unit tests for approve_request method."""

    def test_approve_request_success(self, mock_session: MagicMock) -> None:
        """Test successful approval of attachment request."""
        request_id = uuid.uuid4()
        approver_user_id = uuid.uuid4()
        requester_user_id = uuid.uuid4()
        target_person_id = uuid.uuid4()
        requester_person_id = uuid.uuid4()

        pending_request = PersonAttachmentRequest(
            id=request_id,
            requester_user_id=requester_user_id,
            requester_person_id=requester_person_id,
            target_person_id=target_person_id,
            approver_user_id=approver_user_id,
            status=AttachmentRequestStatus.PENDING,
        )

        target_person = Person(
            id=target_person_id,
            user_id=None,
            created_by_user_id=approver_user_id,
            first_name="Target",
            last_name="Person",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 1),
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.request_repo, "get_by_id", return_value=pending_request
        ), patch.object(
            service.person_repo, "get_by_id", return_value=target_person
        ), patch.object(
            service.person_repo, "update", return_value=target_person
        ), patch.object(
            service, "_delete_person_with_metadata"
        ) as mock_delete, patch.object(
            service.request_repo, "update", return_value=pending_request
        ):
            service.approve_request(request_id, approver_user_id)

            # Verify target person was updated
            assert target_person.user_id == requester_user_id
            assert target_person.is_primary is True

            # Verify temp person was deleted
            mock_delete.assert_called_once_with(requester_person_id)

    def test_approve_request_not_found(self, mock_session: MagicMock) -> None:
        """Test approve_request fails when request not found."""
        request_id = uuid.uuid4()
        approver_user_id = uuid.uuid4()

        service = AttachmentRequestService(mock_session)

        with patch.object(service.request_repo, "get_by_id", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                service.approve_request(request_id, approver_user_id)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail

    def test_approve_request_not_authorized(self, mock_session: MagicMock) -> None:
        """Test approve_request fails when user is not the approver."""
        request_id = uuid.uuid4()
        approver_user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()

        pending_request = PersonAttachmentRequest(
            id=request_id,
            requester_user_id=uuid.uuid4(),
            requester_person_id=uuid.uuid4(),
            target_person_id=uuid.uuid4(),
            approver_user_id=approver_user_id,
            status=AttachmentRequestStatus.PENDING,
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.request_repo, "get_by_id", return_value=pending_request
        ):
            with pytest.raises(HTTPException) as exc_info:
                service.approve_request(request_id, other_user_id)

            assert exc_info.value.status_code == 403
            assert "not authorized" in exc_info.value.detail

    def test_approve_request_already_resolved(self, mock_session: MagicMock) -> None:
        """Test approve_request fails when request is already resolved."""
        request_id = uuid.uuid4()
        approver_user_id = uuid.uuid4()

        resolved_request = PersonAttachmentRequest(
            id=request_id,
            requester_user_id=uuid.uuid4(),
            requester_person_id=uuid.uuid4(),
            target_person_id=uuid.uuid4(),
            approver_user_id=approver_user_id,
            status=AttachmentRequestStatus.APPROVED,  # Already approved
            resolved_at=datetime.utcnow(),
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.request_repo, "get_by_id", return_value=resolved_request
        ):
            with pytest.raises(HTTPException) as exc_info:
                service.approve_request(request_id, approver_user_id)

            assert exc_info.value.status_code == 400
            assert "already been resolved" in exc_info.value.detail


# ============================================================================
# Unit Tests for deny_request
# ============================================================================


@pytest.mark.unit
class TestAttachmentRequestServiceDenyRequest:
    """Unit tests for deny_request method."""

    def test_deny_request_success(self, mock_session: MagicMock) -> None:
        """Test successful denial of attachment request."""
        request_id = uuid.uuid4()
        approver_user_id = uuid.uuid4()
        requester_user_id = uuid.uuid4()
        requester_person_id = uuid.uuid4()

        pending_request = PersonAttachmentRequest(
            id=request_id,
            requester_user_id=requester_user_id,
            requester_person_id=requester_person_id,
            target_person_id=uuid.uuid4(),
            approver_user_id=approver_user_id,
            status=AttachmentRequestStatus.PENDING,
        )

        requester_user = User(
            id=requester_user_id,
            email="requester@example.com",
            hashed_password="test",
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.request_repo, "get_by_id", return_value=pending_request
        ), patch.object(
            service, "_delete_person_with_metadata"
        ) as mock_delete_person, patch.object(
            service.user_repo, "get_by_id", return_value=requester_user
        ), patch.object(
            service.user_repo, "delete"
        ) as mock_delete_user, patch.object(
            service.request_repo, "update", return_value=pending_request
        ):
            service.deny_request(request_id, approver_user_id)

            # Verify temp person was deleted
            mock_delete_person.assert_called_once_with(requester_person_id)

            # Verify requester user was deleted
            mock_delete_user.assert_called_once_with(requester_user)

    def test_deny_request_not_found(self, mock_session: MagicMock) -> None:
        """Test deny_request fails when request not found."""
        request_id = uuid.uuid4()
        approver_user_id = uuid.uuid4()

        service = AttachmentRequestService(mock_session)

        with patch.object(service.request_repo, "get_by_id", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                service.deny_request(request_id, approver_user_id)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail

    def test_deny_request_not_authorized(self, mock_session: MagicMock) -> None:
        """Test deny_request fails when user is not the approver."""
        request_id = uuid.uuid4()
        approver_user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()

        pending_request = PersonAttachmentRequest(
            id=request_id,
            requester_user_id=uuid.uuid4(),
            requester_person_id=uuid.uuid4(),
            target_person_id=uuid.uuid4(),
            approver_user_id=approver_user_id,
            status=AttachmentRequestStatus.PENDING,
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.request_repo, "get_by_id", return_value=pending_request
        ):
            with pytest.raises(HTTPException) as exc_info:
                service.deny_request(request_id, other_user_id)

            assert exc_info.value.status_code == 403
            assert "not authorized" in exc_info.value.detail

    def test_deny_request_already_resolved(self, mock_session: MagicMock) -> None:
        """Test deny_request fails when request is already resolved."""
        request_id = uuid.uuid4()
        approver_user_id = uuid.uuid4()

        resolved_request = PersonAttachmentRequest(
            id=request_id,
            requester_user_id=uuid.uuid4(),
            requester_person_id=uuid.uuid4(),
            target_person_id=uuid.uuid4(),
            approver_user_id=approver_user_id,
            status=AttachmentRequestStatus.DENIED,  # Already denied
            resolved_at=datetime.utcnow(),
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.request_repo, "get_by_id", return_value=resolved_request
        ):
            with pytest.raises(HTTPException) as exc_info:
                service.deny_request(request_id, approver_user_id)

            assert exc_info.value.status_code == 400
            assert "already been resolved" in exc_info.value.detail


# ============================================================================
# Unit Tests for cancel_request
# ============================================================================


@pytest.mark.unit
class TestAttachmentRequestServiceCancelRequest:
    """Unit tests for cancel_request method."""

    def test_cancel_request_success(self, mock_session: MagicMock) -> None:
        """Test successful cancellation of attachment request."""
        request_id = uuid.uuid4()
        requester_user_id = uuid.uuid4()

        pending_request = PersonAttachmentRequest(
            id=request_id,
            requester_user_id=requester_user_id,
            requester_person_id=uuid.uuid4(),
            target_person_id=uuid.uuid4(),
            approver_user_id=uuid.uuid4(),
            status=AttachmentRequestStatus.PENDING,
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.request_repo, "get_by_id", return_value=pending_request
        ), patch.object(
            service.request_repo, "update", return_value=pending_request
        ):
            service.cancel_request(request_id, requester_user_id)

            # Verify status was updated
            assert pending_request.status == AttachmentRequestStatus.CANCELLED
            assert pending_request.resolved_by_user_id == requester_user_id

    def test_cancel_request_not_found(self, mock_session: MagicMock) -> None:
        """Test cancel_request fails when request not found."""
        request_id = uuid.uuid4()
        requester_user_id = uuid.uuid4()

        service = AttachmentRequestService(mock_session)

        with patch.object(service.request_repo, "get_by_id", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                service.cancel_request(request_id, requester_user_id)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail

    def test_cancel_request_not_authorized(self, mock_session: MagicMock) -> None:
        """Test cancel_request fails when user is not the requester."""
        request_id = uuid.uuid4()
        requester_user_id = uuid.uuid4()
        other_user_id = uuid.uuid4()

        pending_request = PersonAttachmentRequest(
            id=request_id,
            requester_user_id=requester_user_id,
            requester_person_id=uuid.uuid4(),
            target_person_id=uuid.uuid4(),
            approver_user_id=uuid.uuid4(),
            status=AttachmentRequestStatus.PENDING,
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.request_repo, "get_by_id", return_value=pending_request
        ):
            with pytest.raises(HTTPException) as exc_info:
                service.cancel_request(request_id, other_user_id)

            assert exc_info.value.status_code == 403
            assert "only cancel your own" in exc_info.value.detail

    def test_cancel_request_already_resolved(self, mock_session: MagicMock) -> None:
        """Test cancel_request fails when request is already resolved."""
        request_id = uuid.uuid4()
        requester_user_id = uuid.uuid4()

        resolved_request = PersonAttachmentRequest(
            id=request_id,
            requester_user_id=requester_user_id,
            requester_person_id=uuid.uuid4(),
            target_person_id=uuid.uuid4(),
            approver_user_id=uuid.uuid4(),
            status=AttachmentRequestStatus.CANCELLED,  # Already cancelled
            resolved_at=datetime.utcnow(),
        )

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.request_repo, "get_by_id", return_value=resolved_request
        ):
            with pytest.raises(HTTPException) as exc_info:
                service.cancel_request(request_id, requester_user_id)

            assert exc_info.value.status_code == 400
            assert "already been resolved" in exc_info.value.detail


# ============================================================================
# Unit Tests for get_pending_count
# ============================================================================


@pytest.mark.unit
class TestAttachmentRequestServiceGetPendingCount:
    """Unit tests for get_pending_count method."""

    def test_get_pending_count_returns_count(self, mock_session: MagicMock) -> None:
        """Test get_pending_count returns correct count."""
        approver_user_id = uuid.uuid4()

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.request_repo, "count_pending_by_approver", return_value=5
        ):
            result = service.get_pending_count(approver_user_id)

            assert result == 5

    def test_get_pending_count_returns_zero(self, mock_session: MagicMock) -> None:
        """Test get_pending_count returns zero when no pending requests."""
        approver_user_id = uuid.uuid4()

        service = AttachmentRequestService(mock_session)

        with patch.object(
            service.request_repo, "count_pending_by_approver", return_value=0
        ):
            result = service.get_pending_count(approver_user_id)

            assert result == 0

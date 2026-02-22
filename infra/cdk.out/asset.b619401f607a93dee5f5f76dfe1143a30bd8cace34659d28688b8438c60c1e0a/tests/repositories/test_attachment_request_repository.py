"""Unit tests for AttachmentRequestRepository.

Tests CRUD operations and filtering by status and user.
Requirements: 2.2, 4.2, 4.3
"""

import uuid
from datetime import date, datetime
from unittest.mock import MagicMock

import pytest
from sqlmodel import Session, select

from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.db_models.person.person_attachment_request import PersonAttachmentRequest
from app.enums.attachment_request_status import AttachmentRequestStatus
from app.models import User
from app.repositories.attachment_request_repository import AttachmentRequestRepository


# ============================================================================
# Unit Tests (Mocked)
# ============================================================================


@pytest.mark.unit
class TestAttachmentRequestRepositoryGetPendingByRequester:
    """Unit tests for get_pending_by_requester method."""

    def test_returns_pending_request_when_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_pending_by_requester returns request when exists."""
        repo = AttachmentRequestRepository(mock_session)
        user_id = uuid.uuid4()
        expected_request = PersonAttachmentRequest(
            id=uuid.uuid4(),
            requester_user_id=user_id,
            requester_person_id=uuid.uuid4(),
            target_person_id=uuid.uuid4(),
            approver_user_id=uuid.uuid4(),
            status=AttachmentRequestStatus.PENDING,
        )
        mock_session.exec.return_value.first.return_value = expected_request

        result = repo.get_pending_by_requester(user_id)

        assert result == expected_request
        mock_session.exec.assert_called_once()

    def test_returns_none_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_pending_by_requester returns None when no pending request."""
        repo = AttachmentRequestRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_pending_by_requester(uuid.uuid4())

        assert result is None


@pytest.mark.unit
class TestAttachmentRequestRepositoryGetPendingByApprover:
    """Unit tests for get_pending_by_approver method."""

    def test_returns_list_of_pending_requests(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_pending_by_approver returns list of requests."""
        repo = AttachmentRequestRepository(mock_session)
        approver_id = uuid.uuid4()
        requests = [
            PersonAttachmentRequest(
                id=uuid.uuid4(),
                requester_user_id=uuid.uuid4(),
                requester_person_id=uuid.uuid4(),
                target_person_id=uuid.uuid4(),
                approver_user_id=approver_id,
                status=AttachmentRequestStatus.PENDING,
            ),
            PersonAttachmentRequest(
                id=uuid.uuid4(),
                requester_user_id=uuid.uuid4(),
                requester_person_id=uuid.uuid4(),
                target_person_id=uuid.uuid4(),
                approver_user_id=approver_id,
                status=AttachmentRequestStatus.PENDING,
            ),
        ]
        mock_session.exec.return_value.all.return_value = requests

        result = repo.get_pending_by_approver(approver_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_returns_empty_list_when_no_requests(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_pending_by_approver returns empty list when no requests."""
        repo = AttachmentRequestRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_pending_by_approver(uuid.uuid4())

        assert result == []


@pytest.mark.unit
class TestAttachmentRequestRepositoryCountPendingByApprover:
    """Unit tests for count_pending_by_approver method."""

    def test_returns_count_of_pending_requests(
        self, mock_session: MagicMock
    ) -> None:
        """Test count_pending_by_approver returns correct count."""
        repo = AttachmentRequestRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 5

        result = repo.count_pending_by_approver(uuid.uuid4())

        assert result == 5
        mock_session.exec.assert_called_once()

    def test_returns_zero_when_no_requests(
        self, mock_session: MagicMock
    ) -> None:
        """Test count_pending_by_approver returns 0 when no requests."""
        repo = AttachmentRequestRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 0

        result = repo.count_pending_by_approver(uuid.uuid4())

        assert result == 0


@pytest.mark.unit
class TestAttachmentRequestRepositoryGetByTargetPerson:
    """Unit tests for get_by_target_person method."""

    def test_returns_requests_for_target_person(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_target_person returns requests for target."""
        repo = AttachmentRequestRepository(mock_session)
        target_person_id = uuid.uuid4()
        requests = [
            PersonAttachmentRequest(
                id=uuid.uuid4(),
                requester_user_id=uuid.uuid4(),
                requester_person_id=uuid.uuid4(),
                target_person_id=target_person_id,
                approver_user_id=uuid.uuid4(),
                status=AttachmentRequestStatus.PENDING,
            ),
        ]
        mock_session.exec.return_value.all.return_value = requests

        result = repo.get_by_target_person(target_person_id)

        assert len(result) == 1
        mock_session.exec.assert_called_once()

    def test_returns_empty_list_when_no_requests(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_target_person returns empty list when no requests."""
        repo = AttachmentRequestRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_target_person(uuid.uuid4())

        assert result == []



# ============================================================================
# Integration Tests (Real Database)
# ============================================================================


@pytest.fixture
def requester_user(db: Session) -> User:
    """Create a requester user."""
    user = User(
        email=f"requester_{uuid.uuid4()}@example.com",
        hashed_password="test_password",
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def approver_user(db: Session) -> User:
    """Create an approver user."""
    user = User(
        email=f"approver_{uuid.uuid4()}@example.com",
        hashed_password="test_password",
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def male_gender(db: Session) -> Gender:
    """Get or create male gender."""
    gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
    if not gender:
        gender = Gender(
            id=uuid.uuid4(),
            name="Male",
            code="MALE",
            description="Male gender",
            is_active=True,
        )
        db.add(gender)
        db.commit()
        db.refresh(gender)
    return gender


@pytest.fixture
def requester_person(
    db: Session, requester_user: User, male_gender: Gender
) -> Person:
    """Create a person for the requester."""
    person = Person(
        user_id=requester_user.id,
        created_by_user_id=requester_user.id,
        is_primary=True,
        is_active=False,  # Temp person during signup
        first_name="Requester",
        last_name="Person",
        gender_id=male_gender.id,
        date_of_birth=date(1990, 1, 1),
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@pytest.fixture
def target_person(
    db: Session, approver_user: User, male_gender: Gender
) -> Person:
    """Create a target person (created by approver, no user linked)."""
    person = Person(
        user_id=None,  # No user linked - can be attached to
        created_by_user_id=approver_user.id,
        is_primary=False,
        is_active=True,
        first_name="Target",
        last_name="Person",
        gender_id=male_gender.id,
        date_of_birth=date(1990, 1, 1),
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@pytest.mark.integration
class TestAttachmentRequestRepositoryCreate:
    """Integration tests for create method."""

    def test_create_attachment_request(
        self,
        db: Session,
        requester_user: User,
        approver_user: User,
        requester_person: Person,
        target_person: Person,
    ) -> None:
        """Test creating an attachment request."""
        repo = AttachmentRequestRepository(db)

        request = PersonAttachmentRequest(
            requester_user_id=requester_user.id,
            requester_person_id=requester_person.id,
            target_person_id=target_person.id,
            approver_user_id=approver_user.id,
            status=AttachmentRequestStatus.PENDING,
        )

        created = repo.create(request)

        assert created.id is not None
        assert created.requester_user_id == requester_user.id
        assert created.approver_user_id == approver_user.id
        assert created.status == AttachmentRequestStatus.PENDING

        # Clean up
        db.delete(created)
        db.commit()


@pytest.mark.integration
class TestAttachmentRequestRepositoryGetPendingByRequesterIntegration:
    """Integration tests for get_pending_by_requester method."""

    def test_returns_pending_request(
        self,
        db: Session,
        requester_user: User,
        approver_user: User,
        requester_person: Person,
        target_person: Person,
    ) -> None:
        """Test get_pending_by_requester returns pending request."""
        repo = AttachmentRequestRepository(db)

        # Create a pending request
        request = PersonAttachmentRequest(
            requester_user_id=requester_user.id,
            requester_person_id=requester_person.id,
            target_person_id=target_person.id,
            approver_user_id=approver_user.id,
            status=AttachmentRequestStatus.PENDING,
        )
        db.add(request)
        db.commit()

        result = repo.get_pending_by_requester(requester_user.id)

        assert result is not None
        assert result.requester_user_id == requester_user.id
        assert result.status == AttachmentRequestStatus.PENDING

        # Clean up
        db.delete(request)
        db.commit()

    def test_does_not_return_approved_request(
        self,
        db: Session,
        requester_user: User,
        approver_user: User,
        requester_person: Person,
        target_person: Person,
    ) -> None:
        """Test get_pending_by_requester does not return approved requests."""
        repo = AttachmentRequestRepository(db)

        # Create an approved request
        request = PersonAttachmentRequest(
            requester_user_id=requester_user.id,
            requester_person_id=requester_person.id,
            target_person_id=target_person.id,
            approver_user_id=approver_user.id,
            status=AttachmentRequestStatus.APPROVED,
            resolved_at=datetime.utcnow(),
            resolved_by_user_id=approver_user.id,
        )
        db.add(request)
        db.commit()

        result = repo.get_pending_by_requester(requester_user.id)

        assert result is None

        # Clean up
        db.delete(request)
        db.commit()


@pytest.mark.integration
class TestAttachmentRequestRepositoryGetPendingByApproverIntegration:
    """Integration tests for get_pending_by_approver method."""

    def test_returns_only_pending_requests_for_approver(
        self,
        db: Session,
        requester_user: User,
        approver_user: User,
        requester_person: Person,
        target_person: Person,
    ) -> None:
        """Test get_pending_by_approver returns only pending requests."""
        repo = AttachmentRequestRepository(db)

        # Create a pending request
        pending_request = PersonAttachmentRequest(
            requester_user_id=requester_user.id,
            requester_person_id=requester_person.id,
            target_person_id=target_person.id,
            approver_user_id=approver_user.id,
            status=AttachmentRequestStatus.PENDING,
        )
        db.add(pending_request)
        db.commit()

        result = repo.get_pending_by_approver(approver_user.id)

        assert len(result) == 1
        assert result[0].status == AttachmentRequestStatus.PENDING
        assert result[0].approver_user_id == approver_user.id

        # Clean up
        db.delete(pending_request)
        db.commit()

    def test_does_not_return_requests_for_other_approvers(
        self,
        db: Session,
        requester_user: User,
        approver_user: User,
        requester_person: Person,
        target_person: Person,
    ) -> None:
        """Test get_pending_by_approver does not return other approvers' requests."""
        repo = AttachmentRequestRepository(db)
        
        # Create another approver user
        other_approver = User(
            email=f"other_approver_{uuid.uuid4()}@example.com",
            hashed_password="test_password",
            is_active=True,
            is_superuser=False,
        )
        db.add(other_approver)
        db.commit()
        db.refresh(other_approver)

        # Create a pending request for a different approver
        request = PersonAttachmentRequest(
            requester_user_id=requester_user.id,
            requester_person_id=requester_person.id,
            target_person_id=target_person.id,
            approver_user_id=other_approver.id,
            status=AttachmentRequestStatus.PENDING,
        )
        db.add(request)
        db.commit()

        result = repo.get_pending_by_approver(approver_user.id)

        assert len(result) == 0

        # Clean up
        db.delete(request)
        db.delete(other_approver)
        db.commit()


@pytest.mark.integration
class TestAttachmentRequestRepositoryCountPendingByApproverIntegration:
    """Integration tests for count_pending_by_approver method."""

    def test_counts_pending_requests(
        self,
        db: Session,
        requester_user: User,
        approver_user: User,
        requester_person: Person,
        target_person: Person,
    ) -> None:
        """Test count_pending_by_approver returns correct count."""
        repo = AttachmentRequestRepository(db)

        # Create a pending request
        request = PersonAttachmentRequest(
            requester_user_id=requester_user.id,
            requester_person_id=requester_person.id,
            target_person_id=target_person.id,
            approver_user_id=approver_user.id,
            status=AttachmentRequestStatus.PENDING,
        )
        db.add(request)
        db.commit()

        count = repo.count_pending_by_approver(approver_user.id)

        assert count == 1

        # Clean up
        db.delete(request)
        db.commit()

    def test_does_not_count_non_pending_requests(
        self,
        db: Session,
        requester_user: User,
        approver_user: User,
        requester_person: Person,
        target_person: Person,
    ) -> None:
        """Test count_pending_by_approver does not count non-pending requests."""
        repo = AttachmentRequestRepository(db)

        # Create an approved request
        request = PersonAttachmentRequest(
            requester_user_id=requester_user.id,
            requester_person_id=requester_person.id,
            target_person_id=target_person.id,
            approver_user_id=approver_user.id,
            status=AttachmentRequestStatus.APPROVED,
            resolved_at=datetime.utcnow(),
            resolved_by_user_id=approver_user.id,
        )
        db.add(request)
        db.commit()

        count = repo.count_pending_by_approver(approver_user.id)

        assert count == 0

        # Clean up
        db.delete(request)
        db.commit()


@pytest.mark.integration
class TestAttachmentRequestRepositoryUpdate:
    """Integration tests for update method."""

    def test_update_request_status(
        self,
        db: Session,
        requester_user: User,
        approver_user: User,
        requester_person: Person,
        target_person: Person,
    ) -> None:
        """Test updating an attachment request status."""
        repo = AttachmentRequestRepository(db)

        # Create a pending request
        request = PersonAttachmentRequest(
            requester_user_id=requester_user.id,
            requester_person_id=requester_person.id,
            target_person_id=target_person.id,
            approver_user_id=approver_user.id,
            status=AttachmentRequestStatus.PENDING,
        )
        db.add(request)
        db.commit()
        db.refresh(request)

        # Update the status
        request.status = AttachmentRequestStatus.APPROVED
        request.resolved_at = datetime.utcnow()
        request.resolved_by_user_id = approver_user.id
        updated = repo.update(request)

        assert updated.status == AttachmentRequestStatus.APPROVED
        assert updated.resolved_at is not None
        assert updated.resolved_by_user_id == approver_user.id

        # Clean up
        db.delete(updated)
        db.commit()

"""Unit tests for ProfileService.

Tests cover:
- Profile completion calculation
- Onboarding status checks

Requirements: 2.10, 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.person.person import Person
from app.enums.marital_status import MaritalStatus
from app.services.profile_service import ProfileService


@pytest.mark.unit
class TestProfileServiceCompletion:
    """Tests for profile completion checks."""

    def test_check_profile_completion_all_complete(
        self, mock_session: MagicMock
    ) -> None:
        """Test profile completion when all fields are present."""
        # Arrange
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        mock_person = Person(
            id=person_id,
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            marital_status=MaritalStatus.SINGLE,  # Set a valid marital status
            is_active=True,  # Person is active (duplicate check complete)
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[MagicMock()]
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=True
        ), patch.object(
            service.attachment_request_repo, "get_pending_by_requester", return_value=None
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is True
            assert result.has_person is True
            assert result.has_address is True
            assert result.has_religion is True
            assert result.has_marital_status is True
            assert result.has_duplicate_check is True
            assert result.has_pending_attachment_request is False
            assert result.pending_request_id is None
            assert result.missing_fields == []

    def test_check_profile_completion_missing_person(
        self, mock_session: MagicMock
    ) -> None:
        """Test profile completion when person record is missing."""
        # Arrange
        user_id = uuid.uuid4()

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=None
        ), patch.object(
            service.attachment_request_repo, "get_pending_by_requester", return_value=None
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is False
            assert result.has_person is False
            assert result.has_address is False
            assert result.has_religion is False
            assert result.has_marital_status is False
            assert result.has_duplicate_check is False
            assert result.has_pending_attachment_request is False
            assert "person" in result.missing_fields
            assert "address" in result.missing_fields
            assert "religion" in result.missing_fields
            assert "marital_status" in result.missing_fields
            assert "duplicate_check" in result.missing_fields

    def test_check_profile_completion_missing_address(
        self, mock_session: MagicMock
    ) -> None:
        """Test profile completion when address is missing."""
        # Arrange
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        mock_person = Person(
            id=person_id,
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            marital_status=MaritalStatus.SINGLE,
            is_active=True,
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[]
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=True
        ), patch.object(
            service.attachment_request_repo, "get_pending_by_requester", return_value=None
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is False
            assert result.has_person is True
            assert result.has_address is False
            assert result.has_religion is True
            assert result.has_marital_status is True
            assert result.has_duplicate_check is True
            assert "address" in result.missing_fields
            assert "person" not in result.missing_fields

    def test_check_profile_completion_missing_religion(
        self, mock_session: MagicMock
    ) -> None:
        """Test profile completion when religion is missing."""
        # Arrange
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        mock_person = Person(
            id=person_id,
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            marital_status=MaritalStatus.SINGLE,
            is_active=True,
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[MagicMock()]
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=False
        ), patch.object(
            service.attachment_request_repo, "get_pending_by_requester", return_value=None
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is False
            assert result.has_person is True
            assert result.has_address is True
            assert result.has_religion is False
            assert result.has_marital_status is True
            assert result.has_duplicate_check is True
            assert "religion" in result.missing_fields

    def test_check_profile_completion_missing_address_and_religion(
        self, mock_session: MagicMock
    ) -> None:
        """Test profile completion when both address and religion are missing."""
        # Arrange
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        mock_person = Person(
            id=person_id,
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            marital_status=MaritalStatus.SINGLE,  # Has marital status
            is_active=True,
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[]
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=False
        ), patch.object(
            service.attachment_request_repo, "get_pending_by_requester", return_value=None
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is False
            assert result.has_person is True
            assert result.has_address is False
            assert result.has_religion is False
            assert result.has_marital_status is True
            assert result.has_duplicate_check is True
            assert "address" in result.missing_fields
            assert "religion" in result.missing_fields
            assert len(result.missing_fields) == 2

    def test_check_profile_completion_with_multiple_addresses(
        self, mock_session: MagicMock
    ) -> None:
        """Test profile completion with multiple addresses."""
        # Arrange
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        mock_person = Person(
            id=person_id,
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            marital_status=MaritalStatus.MARRIED,  # Set a valid marital status
            is_active=True,
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo,
            "get_by_person_id",
            return_value=[MagicMock(), MagicMock()],
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=True
        ), patch.object(
            service.attachment_request_repo, "get_pending_by_requester", return_value=None
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is True
            assert result.has_address is True
            assert result.has_marital_status is True
            assert result.has_duplicate_check is True
            assert result.has_pending_attachment_request is False


@pytest.mark.unit
class TestProfileServiceDuplicateCheck:
    """Tests for duplicate check functionality."""

    def test_check_profile_completion_with_pending_request(
        self, mock_session: MagicMock
    ) -> None:
        """Test profile completion when user has pending attachment request."""
        # Arrange
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        request_id = uuid.uuid4()
        mock_person = Person(
            id=person_id,
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            marital_status=MaritalStatus.SINGLE,
            is_active=False,  # Person is inactive
        )
        mock_pending_request = MagicMock()
        mock_pending_request.id = request_id

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[MagicMock()]
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=True
        ), patch.object(
            service.attachment_request_repo,
            "get_pending_by_requester",
            return_value=mock_pending_request,
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is False  # Not complete due to pending request
            assert result.has_person is True
            assert result.has_address is True
            assert result.has_religion is True
            assert result.has_marital_status is True
            assert result.has_duplicate_check is True  # True because pending request
            assert result.has_pending_attachment_request is True
            assert result.pending_request_id == request_id

    def test_check_profile_completion_inactive_person_no_request(
        self, mock_session: MagicMock
    ) -> None:
        """Test profile completion when person is inactive and no pending request."""
        # Arrange
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        mock_person = Person(
            id=person_id,
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            marital_status=MaritalStatus.SINGLE,
            is_active=False,  # Person is inactive
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[MagicMock()]
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=True
        ), patch.object(
            service.attachment_request_repo, "get_pending_by_requester", return_value=None
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is False
            assert result.has_duplicate_check is False  # False because inactive and no request
            assert result.has_pending_attachment_request is False
            assert "duplicate_check" in result.missing_fields

    def test_get_duplicate_matches_no_person(self, mock_session: MagicMock) -> None:
        """Test get_duplicate_matches returns empty list when user has no person."""
        # Arrange
        user_id = uuid.uuid4()
        service = ProfileService(mock_session)

        with patch.object(service.person_repo, "get_by_user_id", return_value=None):
            # Act
            result = service.get_duplicate_matches(user_id)

            # Assert
            assert result == []

    def test_get_duplicate_matches_no_address(self, mock_session: MagicMock) -> None:
        """Test get_duplicate_matches returns empty list when user has no address."""
        # Arrange
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        mock_person = Person(
            id=person_id,
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(service.address_repo, "get_by_person_id", return_value=[]):
            # Act
            result = service.get_duplicate_matches(user_id)

            # Assert
            assert result == []

    def test_get_duplicate_matches_no_religion(self, mock_session: MagicMock) -> None:
        """Test get_duplicate_matches returns empty list when user has no religion."""
        # Arrange
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        mock_person = Person(
            id=person_id,
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
        )
        mock_address = MagicMock()

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[mock_address]
        ), patch.object(service.religion_repo, "get_by_person_id", return_value=None):
            # Act
            result = service.get_duplicate_matches(user_id)

            # Assert
            assert result == []


@pytest.mark.unit
class TestProfileServiceCompleteWithoutAttachment:
    """Tests for complete_without_attachment functionality."""

    def test_complete_without_attachment_success(
        self, mock_session: MagicMock
    ) -> None:
        """Test complete_without_attachment activates person successfully."""
        # Arrange
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        mock_person = Person(
            id=person_id,
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            marital_status=MaritalStatus.SINGLE,
            is_active=False,  # Initially inactive
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.attachment_request_repo, "get_pending_by_requester", return_value=None
        ), patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[MagicMock()]
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=True
        ):
            # Act
            result = service.complete_without_attachment(user_id)

            # Assert
            assert mock_person.is_active is True  # Person should be activated
            mock_session.add.assert_called_with(mock_person)
            mock_session.commit.assert_called()
            assert result.has_duplicate_check is True

    def test_complete_without_attachment_with_pending_request(
        self, mock_session: MagicMock
    ) -> None:
        """Test complete_without_attachment fails when user has pending request."""
        from fastapi import HTTPException

        # Arrange
        user_id = uuid.uuid4()
        mock_pending_request = MagicMock()
        mock_pending_request.id = uuid.uuid4()

        service = ProfileService(mock_session)

        with patch.object(
            service.attachment_request_repo,
            "get_pending_by_requester",
            return_value=mock_pending_request,
        ):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                service.complete_without_attachment(user_id)

            assert exc_info.value.status_code == 400
            assert "pending" in exc_info.value.detail.lower()

    def test_complete_without_attachment_no_person(
        self, mock_session: MagicMock
    ) -> None:
        """Test complete_without_attachment fails when user has no person."""
        from fastapi import HTTPException

        # Arrange
        user_id = uuid.uuid4()

        service = ProfileService(mock_session)

        with patch.object(
            service.attachment_request_repo, "get_pending_by_requester", return_value=None
        ), patch.object(service.person_repo, "get_by_user_id", return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                service.complete_without_attachment(user_id)

            assert exc_info.value.status_code == 404
            assert "not found" in exc_info.value.detail.lower()

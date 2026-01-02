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
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[MagicMock()]
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=True
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is True
            assert result.has_person is True
            assert result.has_address is True
            assert result.has_religion is True
            assert result.missing_fields == []

    def test_check_profile_completion_missing_person(
        self, mock_session: MagicMock
    ) -> None:
        """Test profile completion when person record is missing."""
        # Arrange
        user_id = uuid.uuid4()

        service = ProfileService(mock_session)

        with patch.object(service.person_repo, "get_by_user_id", return_value=None):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is False
            assert result.has_person is False
            assert result.has_address is False
            assert result.has_religion is False
            assert "person" in result.missing_fields
            assert "address" in result.missing_fields
            assert "religion" in result.missing_fields

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
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[]
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=True
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is False
            assert result.has_person is True
            assert result.has_address is False
            assert result.has_religion is True
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
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[MagicMock()]
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=False
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is False
            assert result.has_person is True
            assert result.has_address is True
            assert result.has_religion is False
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
        )

        service = ProfileService(mock_session)

        with patch.object(
            service.person_repo, "get_by_user_id", return_value=mock_person
        ), patch.object(
            service.address_repo, "get_by_person_id", return_value=[]
        ), patch.object(
            service.religion_repo, "person_has_religion", return_value=False
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is False
            assert result.has_person is True
            assert result.has_address is False
            assert result.has_religion is False
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
        ):
            # Act
            result = service.check_profile_completion(user_id)

            # Assert
            assert result.is_complete is True
            assert result.has_address is True

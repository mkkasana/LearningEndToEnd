"""Unit tests for PersonReligionService.

Tests cover:
- Religion assignment
- Religion updates with category/subcategory

Requirements: 2.6, 2.18
"""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.person.person_religion import PersonReligion
from app.schemas.person.person_religion import PersonReligionCreate, PersonReligionUpdate
from app.services.person.person_religion_service import PersonReligionService


@pytest.mark.unit
class TestPersonReligionServiceQueries:
    """Tests for religion query operations."""

    def test_get_by_person_id_returns_religion(self, mock_session: MagicMock) -> None:
        """Test getting religion by person ID returns the religion."""
        # Arrange
        person_id = uuid.uuid4()
        mock_religion = PersonReligion(
            id=uuid.uuid4(),
            person_id=person_id,
            religion_id=uuid.uuid4(),
        )

        service = PersonReligionService(mock_session)
        with patch.object(
            service.person_religion_repo, "get_by_person_id", return_value=mock_religion
        ):
            # Act
            result = service.get_by_person_id(person_id)

            # Assert
            assert result is not None
            assert result.person_id == person_id

    def test_get_by_person_id_returns_none_for_nonexistent(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting religion for person without religion returns None."""
        # Arrange
        service = PersonReligionService(mock_session)
        with patch.object(
            service.person_religion_repo, "get_by_person_id", return_value=None
        ):
            # Act
            result = service.get_by_person_id(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestPersonReligionServiceCreate:
    """Tests for religion creation."""

    def test_create_person_religion_with_religion_only(
        self, mock_session: MagicMock
    ) -> None:
        """Test creating person religion with only religion ID."""
        # Arrange
        person_id = uuid.uuid4()
        religion_id = uuid.uuid4()
        religion_create = PersonReligionCreate(religion_id=religion_id)

        service = PersonReligionService(mock_session)
        
        def return_religion(religion: PersonReligion) -> PersonReligion:
            return religion

        with patch.object(
            service.person_religion_repo, "create", side_effect=return_religion
        ):
            # Act
            result = service.create_person_religion(person_id, religion_create)

            # Assert
            assert result.person_id == person_id
            assert result.religion_id == religion_id

    def test_create_person_religion_with_category(
        self, mock_session: MagicMock
    ) -> None:
        """Test creating person religion with category."""
        # Arrange
        person_id = uuid.uuid4()
        religion_id = uuid.uuid4()
        category_id = uuid.uuid4()
        religion_create = PersonReligionCreate(
            religion_id=religion_id,
            religion_category_id=category_id,
        )

        service = PersonReligionService(mock_session)
        
        def return_religion(religion: PersonReligion) -> PersonReligion:
            return religion

        with patch.object(
            service.person_religion_repo, "create", side_effect=return_religion
        ):
            # Act
            result = service.create_person_religion(person_id, religion_create)

            # Assert
            assert result.religion_category_id == category_id

    def test_create_person_religion_with_subcategory(
        self, mock_session: MagicMock
    ) -> None:
        """Test creating person religion with subcategory."""
        # Arrange
        person_id = uuid.uuid4()
        religion_id = uuid.uuid4()
        category_id = uuid.uuid4()
        subcategory_id = uuid.uuid4()
        religion_create = PersonReligionCreate(
            religion_id=religion_id,
            religion_category_id=category_id,
            religion_sub_category_id=subcategory_id,
        )

        service = PersonReligionService(mock_session)
        
        def return_religion(religion: PersonReligion) -> PersonReligion:
            return religion

        with patch.object(
            service.person_religion_repo, "create", side_effect=return_religion
        ):
            # Act
            result = service.create_person_religion(person_id, religion_create)

            # Assert
            assert result.religion_sub_category_id == subcategory_id


@pytest.mark.unit
class TestPersonReligionServiceUpdate:
    """Tests for religion update operations."""

    def test_update_person_religion_category(self, mock_session: MagicMock) -> None:
        """Test updating person religion category."""
        # Arrange
        new_category_id = uuid.uuid4()
        mock_religion = PersonReligion(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        religion_update = PersonReligionUpdate(religion_category_id=new_category_id)

        service = PersonReligionService(mock_session)
        
        def return_religion(religion: PersonReligion) -> PersonReligion:
            return religion

        with patch.object(
            service.person_religion_repo, "update", side_effect=return_religion
        ):
            # Act
            result = service.update_person_religion(mock_religion, religion_update)

            # Assert
            assert result.religion_category_id == new_category_id

    def test_update_person_religion_updates_timestamp(
        self, mock_session: MagicMock
    ) -> None:
        """Test that updating religion updates the timestamp."""
        # Arrange
        old_timestamp = datetime(2020, 1, 1, 0, 0, 0)
        mock_religion = PersonReligion(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            created_at=old_timestamp,
            updated_at=old_timestamp,
        )
        religion_update = PersonReligionUpdate(religion_category_id=uuid.uuid4())

        service = PersonReligionService(mock_session)
        
        def return_religion(religion: PersonReligion) -> PersonReligion:
            return religion

        with patch.object(
            service.person_religion_repo, "update", side_effect=return_religion
        ):
            # Act
            result = service.update_person_religion(mock_religion, religion_update)

            # Assert
            assert result.updated_at > old_timestamp


@pytest.mark.unit
class TestPersonReligionServiceDelete:
    """Tests for religion deletion."""

    def test_delete_person_religion_calls_repository(
        self, mock_session: MagicMock
    ) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_religion = PersonReligion(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
        )

        service = PersonReligionService(mock_session)
        mock_delete = MagicMock()
        
        with patch.object(service.person_religion_repo, "delete", mock_delete):
            # Act
            service.delete_person_religion(mock_religion)

            # Assert
            mock_delete.assert_called_once_with(mock_religion)

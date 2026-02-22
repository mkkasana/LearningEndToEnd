"""Unit tests for PersonMetadataService.

Tests cover:
- Metadata retrieval by person
- Metadata creation
- Metadata updates
- Metadata deletion

Requirements: 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.person.person_metadata import PersonMetadata
from app.schemas.person import PersonMetadataCreate, PersonMetadataUpdate
from app.services.person.person_metadata_service import PersonMetadataService


@pytest.mark.unit
class TestPersonMetadataServiceQueries:
    """Tests for metadata query operations."""

    def test_get_metadata_by_person_returns_metadata(self, mock_session: MagicMock) -> None:
        """Test getting metadata by person returns the metadata."""
        # Arrange
        person_id = uuid.uuid4()
        mock_metadata = MagicMock(spec=PersonMetadata)
        mock_metadata.id = uuid.uuid4()
        mock_metadata.person_id = person_id

        service = PersonMetadataService(mock_session)
        with patch.object(service.metadata_repo, "get_by_person_id", return_value=mock_metadata):
            # Act
            result = service.get_metadata_by_person(person_id)

            # Assert
            assert result is not None
            assert result.person_id == person_id

    def test_get_metadata_by_person_returns_none_for_nonexistent(self, mock_session: MagicMock) -> None:
        """Test getting metadata for nonexistent person returns None."""
        # Arrange
        service = PersonMetadataService(mock_session)
        with patch.object(service.metadata_repo, "get_by_person_id", return_value=None):
            # Act
            result = service.get_metadata_by_person(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestPersonMetadataServiceCreate:
    """Tests for metadata creation."""

    def test_create_metadata_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating metadata with valid data."""
        # Arrange
        person_id = uuid.uuid4()
        metadata_create = PersonMetadataCreate(
            bio="Test bio",
            profile_picture_url="https://example.com/pic.jpg"
        )

        service = PersonMetadataService(mock_session)

        def return_metadata(metadata: PersonMetadata) -> PersonMetadata:
            metadata.id = uuid.uuid4()
            return metadata

        with patch.object(service.metadata_repo, "create", side_effect=return_metadata):
            # Act
            result = service.create_metadata(person_id, metadata_create)

            # Assert
            assert result is not None
            assert result.person_id == person_id

    def test_create_metadata_sets_person_id(self, mock_session: MagicMock) -> None:
        """Test that create_metadata sets the person_id correctly."""
        # Arrange
        person_id = uuid.uuid4()
        metadata_create = PersonMetadataCreate()

        service = PersonMetadataService(mock_session)

        def return_metadata(metadata: PersonMetadata) -> PersonMetadata:
            metadata.id = uuid.uuid4()
            return metadata

        with patch.object(service.metadata_repo, "create", side_effect=return_metadata):
            # Act
            result = service.create_metadata(person_id, metadata_create)

            # Assert
            assert result.person_id == person_id


@pytest.mark.unit
class TestPersonMetadataServiceUpdate:
    """Tests for metadata update operations."""

    def test_update_metadata_bio(self, mock_session: MagicMock) -> None:
        """Test updating metadata bio."""
        # Arrange
        from app.db_models.person.person_metadata import PersonMetadata
        
        mock_metadata = PersonMetadata(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            bio="Old bio"
        )
        metadata_update = PersonMetadataUpdate(bio="New bio")

        service = PersonMetadataService(mock_session)

        def return_metadata(metadata: PersonMetadata) -> PersonMetadata:
            return metadata

        with patch.object(service.metadata_repo, "update", side_effect=return_metadata):
            # Act
            result = service.update_metadata(mock_metadata, metadata_update)

            # Assert
            assert result.bio == "New bio"

    def test_update_metadata_profile_image(self, mock_session: MagicMock) -> None:
        """Test updating metadata profile image URL."""
        # Arrange
        from app.db_models.person.person_metadata import PersonMetadata
        
        mock_metadata = PersonMetadata(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            profile_image_url="https://old.com/pic.jpg"
        )
        metadata_update = PersonMetadataUpdate(profile_image_url="https://new.com/pic.jpg")

        service = PersonMetadataService(mock_session)

        def return_metadata(metadata: PersonMetadata) -> PersonMetadata:
            return metadata

        with patch.object(service.metadata_repo, "update", side_effect=return_metadata):
            # Act
            result = service.update_metadata(mock_metadata, metadata_update)

            # Assert
            assert result.profile_image_url == "https://new.com/pic.jpg"


@pytest.mark.unit
class TestPersonMetadataServiceDelete:
    """Tests for metadata deletion."""

    def test_delete_metadata_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_metadata = MagicMock(spec=PersonMetadata)
        mock_metadata.id = uuid.uuid4()
        mock_metadata.person_id = uuid.uuid4()

        service = PersonMetadataService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.metadata_repo, "delete", mock_delete):
            # Act
            service.delete_metadata(mock_metadata)

            # Assert
            mock_delete.assert_called_once_with(mock_metadata)

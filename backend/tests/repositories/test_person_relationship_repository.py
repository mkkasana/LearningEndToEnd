"""Unit tests for PersonRelationshipRepository."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.db_models.person.person_relationship import PersonRelationship
from app.enums import RelationshipType
from app.repositories.person.person_relationship_repository import (
    PersonRelationshipRepository,
)


@pytest.mark.unit
class TestGetByPersonId:
    """Tests for get_by_person_id method."""

    def test_get_by_person_id_returns_relationships(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_person_id returns list of relationships."""
        repo = PersonRelationshipRepository(mock_session)
        person_id = uuid.uuid4()
        relationships = [
            PersonRelationship(
                id=uuid.uuid4(),
                person_id=person_id,
                related_person_id=uuid.uuid4(),
                relationship_type=RelationshipType.FATHER,
                is_active=True,
            ),
            PersonRelationship(
                id=uuid.uuid4(),
                person_id=person_id,
                related_person_id=uuid.uuid4(),
                relationship_type=RelationshipType.MOTHER,
                is_active=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = relationships

        result = repo.get_by_person_id(person_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_by_person_id_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_person_id returns empty list when no relationships."""
        repo = PersonRelationshipRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_person_id(uuid.uuid4())

        assert result == []


@pytest.mark.unit
class TestGetActiveRelationships:
    """Tests for get_active_relationships method."""

    def test_get_active_relationships_returns_only_active(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_active_relationships returns only active relationships."""
        repo = PersonRelationshipRepository(mock_session)
        person_id = uuid.uuid4()
        active_rel = PersonRelationship(
            id=uuid.uuid4(),
            person_id=person_id,
            related_person_id=uuid.uuid4(),
            relationship_type=RelationshipType.FATHER,
            is_active=True,
        )
        mock_session.exec.return_value.all.return_value = [active_rel]

        result = repo.get_active_relationships(person_id)

        assert len(result) == 1
        assert result[0].is_active is True

    def test_get_active_relationships_returns_empty_when_none_active(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_active_relationships returns empty when no active relationships."""
        repo = PersonRelationshipRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_active_relationships(uuid.uuid4())

        assert result == []


@pytest.mark.unit
class TestGetByRelationshipType:
    """Tests for get_by_relationship_type method."""

    def test_get_by_relationship_type_returns_matching(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_relationship_type returns relationships of specified type."""
        repo = PersonRelationshipRepository(mock_session)
        person_id = uuid.uuid4()
        father_rel = PersonRelationship(
            id=uuid.uuid4(),
            person_id=person_id,
            related_person_id=uuid.uuid4(),
            relationship_type=RelationshipType.FATHER,
            is_active=True,
        )
        mock_session.exec.return_value.all.return_value = [father_rel]

        result = repo.get_by_relationship_type(person_id, RelationshipType.FATHER)

        assert len(result) == 1
        assert result[0].relationship_type == RelationshipType.FATHER

    def test_get_by_relationship_type_returns_empty_when_no_match(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_relationship_type returns empty when no matching type."""
        repo = PersonRelationshipRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_relationship_type(uuid.uuid4(), RelationshipType.SPOUSE)

        assert result == []


@pytest.mark.unit
class TestGetByRelationshipTypes:
    """Tests for get_by_relationship_types method."""

    def test_get_by_relationship_types_returns_multiple_types(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_relationship_types returns relationships of multiple types."""
        repo = PersonRelationshipRepository(mock_session)
        person_id = uuid.uuid4()
        relationships = [
            PersonRelationship(
                id=uuid.uuid4(),
                person_id=person_id,
                related_person_id=uuid.uuid4(),
                relationship_type=RelationshipType.FATHER,
                is_active=True,
            ),
            PersonRelationship(
                id=uuid.uuid4(),
                person_id=person_id,
                related_person_id=uuid.uuid4(),
                relationship_type=RelationshipType.MOTHER,
                is_active=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = relationships

        result = repo.get_by_relationship_types(
            person_id, [RelationshipType.FATHER, RelationshipType.MOTHER]
        )

        assert len(result) == 2


@pytest.mark.unit
class TestFindInverse:
    """Tests for find_inverse method."""

    def test_find_inverse_returns_relationship_when_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test find_inverse returns inverse relationship when exists."""
        repo = PersonRelationshipRepository(mock_session)
        person_id = uuid.uuid4()
        related_person_id = uuid.uuid4()
        inverse_rel = PersonRelationship(
            id=uuid.uuid4(),
            person_id=related_person_id,
            related_person_id=person_id,
            relationship_type=RelationshipType.SON,
            is_active=True,
        )
        mock_session.exec.return_value.first.return_value = inverse_rel

        result = repo.find_inverse(person_id, related_person_id)

        assert result == inverse_rel
        assert result.person_id == related_person_id
        assert result.related_person_id == person_id

    def test_find_inverse_returns_none_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test find_inverse returns None when no inverse exists."""
        repo = PersonRelationshipRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.find_inverse(uuid.uuid4(), uuid.uuid4())

        assert result is None


@pytest.mark.unit
class TestFindInverseIncludingInactive:
    """Tests for find_inverse_including_inactive method."""

    def test_find_inverse_including_inactive_returns_inactive(
        self, mock_session: MagicMock
    ) -> None:
        """Test find_inverse_including_inactive returns inactive relationships."""
        repo = PersonRelationshipRepository(mock_session)
        person_id = uuid.uuid4()
        related_person_id = uuid.uuid4()
        inactive_rel = PersonRelationship(
            id=uuid.uuid4(),
            person_id=related_person_id,
            related_person_id=person_id,
            relationship_type=RelationshipType.SON,
            is_active=False,
        )
        mock_session.exec.return_value.first.return_value = inactive_rel

        result = repo.find_inverse_including_inactive(person_id, related_person_id)

        assert result == inactive_rel
        assert result.is_active is False

    def test_find_inverse_including_inactive_returns_none_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test find_inverse_including_inactive returns None when not found."""
        repo = PersonRelationshipRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.find_inverse_including_inactive(uuid.uuid4(), uuid.uuid4())

        assert result is None


@pytest.mark.unit
class TestDeleteWithoutCommit:
    """Tests for delete_without_commit method."""

    def test_delete_without_commit_calls_session_delete(
        self, mock_session: MagicMock
    ) -> None:
        """Test delete_without_commit calls session.delete without commit."""
        repo = PersonRelationshipRepository(mock_session)
        relationship = PersonRelationship(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            related_person_id=uuid.uuid4(),
            relationship_type=RelationshipType.FATHER,
            is_active=True,
        )

        repo.delete_without_commit(relationship)

        mock_session.delete.assert_called_once_with(relationship)
        mock_session.commit.assert_not_called()


@pytest.mark.unit
class TestUpdateWithoutCommit:
    """Tests for update_without_commit method."""

    def test_update_without_commit_calls_session_add(
        self, mock_session: MagicMock
    ) -> None:
        """Test update_without_commit calls session.add without commit."""
        repo = PersonRelationshipRepository(mock_session)
        relationship = PersonRelationship(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            related_person_id=uuid.uuid4(),
            relationship_type=RelationshipType.FATHER,
            is_active=True,
        )

        result = repo.update_without_commit(relationship)

        mock_session.add.assert_called_once_with(relationship)
        mock_session.commit.assert_not_called()
        assert result == relationship

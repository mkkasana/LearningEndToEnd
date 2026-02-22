"""Unit tests for ReligionCategoryRepository."""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.religion.religion_category import ReligionCategory
from app.repositories.religion.religion_category_repository import (
    ReligionCategoryRepository,
)


@pytest.mark.unit
class TestGetCategoriesByReligion:
    """Tests for get_categories_by_religion method."""

    def test_get_categories_by_religion_returns_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_categories_by_religion returns list of categories."""
        repo = ReligionCategoryRepository(mock_session)
        religion_id = uuid.uuid4()
        categories = [
            ReligionCategory(
                id=uuid.uuid4(),
                name="Catholic",
                code="CATHOLIC",
                religion_id=religion_id,
                is_active=True,
            ),
            ReligionCategory(
                id=uuid.uuid4(),
                name="Protestant",
                code="PROTESTANT",
                religion_id=religion_id,
                is_active=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = categories

        result = repo.get_categories_by_religion(religion_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_categories_by_religion_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_categories_by_religion returns empty list when no categories."""
        repo = ReligionCategoryRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_categories_by_religion(uuid.uuid4())

        assert result == []


@pytest.mark.unit
class TestCodeExists:
    """Tests for code_exists method."""

    def test_code_exists_returns_true_when_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test code_exists returns True when code exists in religion."""
        repo = ReligionCategoryRepository(mock_session)
        religion_id = uuid.uuid4()
        mock_session.exec.return_value.first.return_value = ReligionCategory(
            id=uuid.uuid4(),
            name="Catholic",
            code="CATHOLIC",
            religion_id=religion_id,
            is_active=True,
        )

        result = repo.code_exists("CATHOLIC", religion_id)

        assert result is True

    def test_code_exists_returns_false_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test code_exists returns False when code doesn't exist."""
        repo = ReligionCategoryRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.code_exists("NONEXISTENT", uuid.uuid4())

        assert result is False

    def test_code_exists_excludes_specified_id(
        self, mock_session: MagicMock
    ) -> None:
        """Test code_exists excludes specified category ID."""
        repo = ReligionCategoryRepository(mock_session)
        religion_id = uuid.uuid4()
        exclude_id = uuid.uuid4()
        mock_session.exec.return_value.first.return_value = None

        result = repo.code_exists(
            "CATHOLIC", religion_id, exclude_category_id=exclude_id
        )

        assert result is False
        mock_session.exec.assert_called_once()

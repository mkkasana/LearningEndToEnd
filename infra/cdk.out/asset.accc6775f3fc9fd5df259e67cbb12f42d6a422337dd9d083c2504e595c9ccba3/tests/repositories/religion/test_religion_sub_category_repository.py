"""Unit tests for ReligionSubCategoryRepository.

Tests cover:
- Sub-category retrieval by category
- Code existence check

Requirements: 3.12, 3.15
"""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.religion.religion_sub_category import ReligionSubCategory
from app.repositories.religion.religion_sub_category_repository import ReligionSubCategoryRepository


@pytest.mark.unit
class TestGetSubCategoriesByCategory:
    """Tests for get_sub_categories_by_category method."""

    def test_get_sub_categories_by_category_returns_list(self, mock_session: MagicMock) -> None:
        """Test get_sub_categories_by_category returns list of sub-categories."""
        repo = ReligionSubCategoryRepository(mock_session)
        category_id = uuid.uuid4()
        sub_categories = [
            ReligionSubCategory(
                id=uuid.uuid4(),
                name="Lingayat",
                code="LIN",
                category_id=category_id,
                is_active=True,
            ),
            ReligionSubCategory(
                id=uuid.uuid4(),
                name="Nath",
                code="NAT",
                category_id=category_id,
                is_active=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = sub_categories

        result = repo.get_sub_categories_by_category(category_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_sub_categories_by_category_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test get_sub_categories_by_category returns empty list when no sub-categories."""
        repo = ReligionSubCategoryRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_sub_categories_by_category(uuid.uuid4())

        assert result == []


@pytest.mark.unit
class TestCodeExists:
    """Tests for code_exists method."""

    def test_code_exists_returns_true_when_exists(self, mock_session: MagicMock) -> None:
        """Test code_exists returns True when code exists."""
        repo = ReligionSubCategoryRepository(mock_session)
        category_id = uuid.uuid4()
        sub_category = ReligionSubCategory(
            id=uuid.uuid4(),
            name="Lingayat",
            code="LIN",
            category_id=category_id,
            is_active=True,
        )
        mock_session.exec.return_value.first.return_value = sub_category

        result = repo.code_exists("LIN", category_id)

        assert result is True

    def test_code_exists_returns_false_when_not_exists(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False when code doesn't exist."""
        repo = ReligionSubCategoryRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.code_exists("UNKNOWN", uuid.uuid4())

        assert result is False

    def test_code_exists_with_exclude_id(self, mock_session: MagicMock) -> None:
        """Test code_exists with exclude_sub_category_id parameter."""
        repo = ReligionSubCategoryRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        sub_category_id = uuid.uuid4()
        category_id = uuid.uuid4()
        result = repo.code_exists("LIN", category_id, exclude_sub_category_id=sub_category_id)

        assert result is False
        mock_session.exec.assert_called_once()

    def test_code_exists_case_insensitive(self, mock_session: MagicMock) -> None:
        """Test code_exists handles lowercase input."""
        repo = ReligionSubCategoryRepository(mock_session)
        category_id = uuid.uuid4()
        sub_category = ReligionSubCategory(
            id=uuid.uuid4(),
            name="Lingayat",
            code="LIN",
            category_id=category_id,
            is_active=True,
        )
        mock_session.exec.return_value.first.return_value = sub_category

        result = repo.code_exists("lin", category_id)

        assert result is True

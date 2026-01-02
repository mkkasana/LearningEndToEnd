"""Unit tests for LocalityRepository.

Tests cover:
- Locality retrieval by sub-district
- Locality retrieval by code
- Locality count by sub-district

Requirements: 3.13, 3.15
"""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.address import Locality
from app.repositories.address.locality_repository import LocalityRepository


@pytest.mark.unit
class TestGetBySubDistrict:
    """Tests for get_by_sub_district method."""

    def test_get_by_sub_district_returns_localities(self, mock_session: MagicMock) -> None:
        """Test get_by_sub_district returns list of localities."""
        repo = LocalityRepository(mock_session)
        sub_district_id = uuid.uuid4()
        localities = [
            Locality(
                id=uuid.uuid4(),
                name="Versova",
                code="VER",
                sub_district_id=sub_district_id,
                is_active=True,
            ),
            Locality(
                id=uuid.uuid4(),
                name="Lokhandwala",
                code="LOK",
                sub_district_id=sub_district_id,
                is_active=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = localities

        result = repo.get_by_sub_district(sub_district_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_by_sub_district_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test get_by_sub_district returns empty list when no localities."""
        repo = LocalityRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_sub_district(uuid.uuid4())

        assert result == []


@pytest.mark.unit
class TestGetByCode:
    """Tests for get_by_code method."""

    def test_get_by_code_returns_locality(self, mock_session: MagicMock) -> None:
        """Test get_by_code returns locality when found."""
        repo = LocalityRepository(mock_session)
        sub_district_id = uuid.uuid4()
        locality = Locality(
            id=uuid.uuid4(),
            name="Versova",
            code="VER",
            sub_district_id=sub_district_id,
            is_active=True,
        )
        mock_session.exec.return_value.first.return_value = locality

        result = repo.get_by_code("VER", sub_district_id)

        assert result == locality
        assert result.code == "VER"

    def test_get_by_code_returns_none_when_not_found(self, mock_session: MagicMock) -> None:
        """Test get_by_code returns None when locality not found."""
        repo = LocalityRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_by_code("XX", uuid.uuid4())

        assert result is None


@pytest.mark.unit
class TestCountBySubDistrict:
    """Tests for count_by_sub_district method."""

    def test_count_by_sub_district_returns_count(self, mock_session: MagicMock) -> None:
        """Test count_by_sub_district returns correct count."""
        repo = LocalityRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 20

        result = repo.count_by_sub_district(uuid.uuid4())

        assert result == 20

    def test_count_by_sub_district_returns_zero(self, mock_session: MagicMock) -> None:
        """Test count_by_sub_district returns 0 when no localities."""
        repo = LocalityRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 0

        result = repo.count_by_sub_district(uuid.uuid4())

        assert result == 0

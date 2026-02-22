"""Unit tests for SubDistrictRepository.

Tests cover:
- Sub-district retrieval by district
- Sub-district retrieval by code
- Sub-district count by district

Requirements: 3.12, 3.15
"""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.address import SubDistrict
from app.repositories.address.sub_district_repository import SubDistrictRepository


@pytest.mark.unit
class TestGetByDistrict:
    """Tests for get_by_district method."""

    def test_get_by_district_returns_sub_districts(self, mock_session: MagicMock) -> None:
        """Test get_by_district returns list of sub-districts."""
        repo = SubDistrictRepository(mock_session)
        district_id = uuid.uuid4()
        sub_districts = [
            SubDistrict(
                id=uuid.uuid4(),
                name="Andheri",
                code="AND",
                district_id=district_id,
                is_active=True,
            ),
            SubDistrict(
                id=uuid.uuid4(),
                name="Bandra",
                code="BAN",
                district_id=district_id,
                is_active=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = sub_districts

        result = repo.get_by_district(district_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_by_district_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test get_by_district returns empty list when no sub-districts."""
        repo = SubDistrictRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_district(uuid.uuid4())

        assert result == []


@pytest.mark.unit
class TestGetByCode:
    """Tests for get_by_code method."""

    def test_get_by_code_returns_sub_district(self, mock_session: MagicMock) -> None:
        """Test get_by_code returns sub-district when found."""
        repo = SubDistrictRepository(mock_session)
        district_id = uuid.uuid4()
        sub_district = SubDistrict(
            id=uuid.uuid4(),
            name="Andheri",
            code="AND",
            district_id=district_id,
            is_active=True,
        )
        mock_session.exec.return_value.first.return_value = sub_district

        result = repo.get_by_code("AND", district_id)

        assert result == sub_district
        assert result.code == "AND"

    def test_get_by_code_returns_none_when_not_found(self, mock_session: MagicMock) -> None:
        """Test get_by_code returns None when sub-district not found."""
        repo = SubDistrictRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_by_code("XX", uuid.uuid4())

        assert result is None


@pytest.mark.unit
class TestCountByDistrict:
    """Tests for count_by_district method."""

    def test_count_by_district_returns_count(self, mock_session: MagicMock) -> None:
        """Test count_by_district returns correct count."""
        repo = SubDistrictRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 15

        result = repo.count_by_district(uuid.uuid4())

        assert result == 15

    def test_count_by_district_returns_zero(self, mock_session: MagicMock) -> None:
        """Test count_by_district returns 0 when no sub-districts."""
        repo = SubDistrictRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 0

        result = repo.count_by_district(uuid.uuid4())

        assert result == 0

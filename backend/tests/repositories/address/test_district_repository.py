"""Unit tests for DistrictRepository.

Tests cover:
- District retrieval by state
- District retrieval by code
- District count by state

Requirements: 3.11, 3.15
"""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.address import District
from app.repositories.address.district_repository import DistrictRepository


@pytest.mark.unit
class TestGetByState:
    """Tests for get_by_state method."""

    def test_get_by_state_returns_districts(self, mock_session: MagicMock) -> None:
        """Test get_by_state returns list of districts."""
        repo = DistrictRepository(mock_session)
        state_id = uuid.uuid4()
        districts = [
            District(
                id=uuid.uuid4(),
                name="Mumbai",
                code="MUM",
                state_id=state_id,
                is_active=True,
            ),
            District(
                id=uuid.uuid4(),
                name="Pune",
                code="PUN",
                state_id=state_id,
                is_active=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = districts

        result = repo.get_by_state(state_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_by_state_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test get_by_state returns empty list when no districts."""
        repo = DistrictRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_state(uuid.uuid4())

        assert result == []


@pytest.mark.unit
class TestGetByCode:
    """Tests for get_by_code method."""

    def test_get_by_code_returns_district(self, mock_session: MagicMock) -> None:
        """Test get_by_code returns district when found."""
        repo = DistrictRepository(mock_session)
        state_id = uuid.uuid4()
        district = District(
            id=uuid.uuid4(),
            name="Mumbai",
            code="MUM",
            state_id=state_id,
            is_active=True,
        )
        mock_session.exec.return_value.first.return_value = district

        result = repo.get_by_code("MUM", state_id)

        assert result == district
        assert result.code == "MUM"

    def test_get_by_code_returns_none_when_not_found(self, mock_session: MagicMock) -> None:
        """Test get_by_code returns None when district not found."""
        repo = DistrictRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_by_code("XX", uuid.uuid4())

        assert result is None


@pytest.mark.unit
class TestCountByState:
    """Tests for count_by_state method."""

    def test_count_by_state_returns_count(self, mock_session: MagicMock) -> None:
        """Test count_by_state returns correct count."""
        repo = DistrictRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 10

        result = repo.count_by_state(uuid.uuid4())

        assert result == 10

    def test_count_by_state_returns_zero(self, mock_session: MagicMock) -> None:
        """Test count_by_state returns 0 when no districts."""
        repo = DistrictRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 0

        result = repo.count_by_state(uuid.uuid4())

        assert result == 0

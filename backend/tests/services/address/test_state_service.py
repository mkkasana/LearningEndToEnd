"""Unit tests for StateService.

Tests cover:
- State retrieval by country
- State retrieval by ID
- State CRUD operations
- Code validation

Requirements: 2.16, 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.address import State
from app.schemas.address import StateCreate, StateUpdate
from app.services.address.state_service import StateService


@pytest.mark.unit
class TestStateServiceQueries:
    """Tests for state query operations."""

    def test_get_states_by_country_returns_list(self, mock_session: MagicMock) -> None:
        """Test getting states by country returns a list."""
        # Arrange
        country_id = uuid.uuid4()
        mock_states = [
            State(id=uuid.uuid4(), name="Maharashtra", code="MH", country_id=country_id, is_active=True),
            State(id=uuid.uuid4(), name="Karnataka", code="KA", country_id=country_id, is_active=True),
        ]

        service = StateService(mock_session)
        with patch.object(service.state_repo, "get_by_country", return_value=mock_states):
            # Act
            result = service.get_states_by_country(country_id)

            # Assert
            assert len(result) == 2
            assert result[0].stateName == "Maharashtra"
            assert result[1].stateName == "Karnataka"

    def test_get_states_by_country_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test getting states for country with no states returns empty list."""
        # Arrange
        country_id = uuid.uuid4()
        service = StateService(mock_session)
        with patch.object(service.state_repo, "get_by_country", return_value=[]):
            # Act
            result = service.get_states_by_country(country_id)

            # Assert
            assert len(result) == 0

    def test_get_state_by_id_returns_state(self, mock_session: MagicMock) -> None:
        """Test getting state by ID returns the state."""
        # Arrange
        state_id = uuid.uuid4()
        mock_state = State(id=state_id, name="Maharashtra", code="MH", country_id=uuid.uuid4(), is_active=True)

        service = StateService(mock_session)
        with patch.object(service.state_repo, "get_by_id", return_value=mock_state):
            # Act
            result = service.get_state_by_id(state_id)

            # Assert
            assert result is not None
            assert result.id == state_id
            assert result.name == "Maharashtra"

    def test_get_state_by_id_returns_none_for_nonexistent(self, mock_session: MagicMock) -> None:
        """Test getting nonexistent state returns None."""
        # Arrange
        service = StateService(mock_session)
        with patch.object(service.state_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_state_by_id(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestStateServiceCreate:
    """Tests for state creation."""

    def test_create_state_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating state with valid data."""
        # Arrange
        country_id = uuid.uuid4()
        state_create = StateCreate(name="New State", code="ns", country_id=country_id, is_active=True)

        service = StateService(mock_session)

        def return_state(state: State) -> State:
            return state

        with patch.object(service.state_repo, "create", side_effect=return_state):
            # Act
            result = service.create_state(state_create)

            # Assert
            assert result.name == "New State"
            assert result.code == "NS"  # Should be uppercase
            assert result.country_id == country_id
            assert result.is_active is True

    def test_create_state_uppercases_code(self, mock_session: MagicMock) -> None:
        """Test that state code is uppercased on creation."""
        # Arrange
        state_create = StateCreate(name="Test", code="ts", country_id=uuid.uuid4(), is_active=True)

        service = StateService(mock_session)

        def return_state(state: State) -> State:
            return state

        with patch.object(service.state_repo, "create", side_effect=return_state):
            # Act
            result = service.create_state(state_create)

            # Assert
            assert result.code == "TS"

    def test_create_state_with_none_code(self, mock_session: MagicMock) -> None:
        """Test creating state with None code."""
        # Arrange
        state_create = StateCreate(name="Test", code=None, country_id=uuid.uuid4(), is_active=True)

        service = StateService(mock_session)

        def return_state(state: State) -> State:
            return state

        with patch.object(service.state_repo, "create", side_effect=return_state):
            # Act
            result = service.create_state(state_create)

            # Assert
            assert result.code is None


@pytest.mark.unit
class TestStateServiceUpdate:
    """Tests for state update operations."""

    def test_update_state_name(self, mock_session: MagicMock) -> None:
        """Test updating state name."""
        # Arrange
        mock_state = State(id=uuid.uuid4(), name="Old Name", code="ON", country_id=uuid.uuid4(), is_active=True)
        state_update = StateUpdate(name="New Name")

        service = StateService(mock_session)

        def return_state(state: State) -> State:
            return state

        with patch.object(service.state_repo, "update", side_effect=return_state):
            # Act
            result = service.update_state(mock_state, state_update)

            # Assert
            assert result.name == "New Name"

    def test_update_state_code_uppercases(self, mock_session: MagicMock) -> None:
        """Test that updating state code uppercases it."""
        # Arrange
        mock_state = State(id=uuid.uuid4(), name="State", code="OLD", country_id=uuid.uuid4(), is_active=True)
        state_update = StateUpdate(code="new")

        service = StateService(mock_session)

        def return_state(state: State) -> State:
            return state

        with patch.object(service.state_repo, "update", side_effect=return_state):
            # Act
            result = service.update_state(mock_state, state_update)

            # Assert
            assert result.code == "NEW"


@pytest.mark.unit
class TestStateServiceDelete:
    """Tests for state deletion."""

    def test_delete_state_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_state = State(id=uuid.uuid4(), name="State to Delete", code="SD", country_id=uuid.uuid4(), is_active=True)

        service = StateService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.state_repo, "delete", mock_delete):
            # Act
            service.delete_state(mock_state)

            # Assert
            mock_delete.assert_called_once_with(mock_state)


@pytest.mark.unit
class TestStateServiceValidation:
    """Tests for state validation."""

    def test_code_exists_returns_true_for_existing_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns True for existing code."""
        # Arrange
        country_id = uuid.uuid4()
        mock_state = State(id=uuid.uuid4(), name="Maharashtra", code="MH", country_id=country_id, is_active=True)

        service = StateService(mock_session)
        with patch.object(service.state_repo, "get_by_code", return_value=mock_state):
            # Act
            result = service.code_exists("MH", country_id)

            # Assert
            assert result is True

    def test_code_exists_returns_false_for_nonexistent_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False for nonexistent code."""
        # Arrange
        service = StateService(mock_session)
        with patch.object(service.state_repo, "get_by_code", return_value=None):
            # Act
            result = service.code_exists("XX", uuid.uuid4())

            # Assert
            assert result is False

    def test_code_exists_with_exclude_returns_false(self, mock_session: MagicMock) -> None:
        """Test code_exists with exclude returns False when excluding the match."""
        # Arrange
        state_id = uuid.uuid4()
        country_id = uuid.uuid4()
        mock_state = State(id=state_id, name="Maharashtra", code="MH", country_id=country_id, is_active=True)

        service = StateService(mock_session)
        with patch.object(service.state_repo, "get_by_code", return_value=mock_state):
            # Act
            result = service.code_exists("MH", country_id, exclude_state_id=state_id)

            # Assert
            assert result is False

    def test_code_exists_returns_false_for_empty_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False for empty code."""
        # Arrange
        service = StateService(mock_session)

        # Act
        result = service.code_exists("", uuid.uuid4())

        # Assert
        assert result is False

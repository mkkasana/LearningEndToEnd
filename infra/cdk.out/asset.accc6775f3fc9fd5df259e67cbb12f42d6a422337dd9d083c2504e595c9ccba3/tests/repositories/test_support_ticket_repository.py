"""Unit tests for SupportTicketRepository."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.db_models.support_ticket import SupportTicket
from app.repositories.support_ticket_repository import SupportTicketRepository
from app.schemas.support_ticket import IssueStatus, IssueType


@pytest.mark.unit
class TestGetByUserId:
    """Tests for get_by_user_id method."""

    def test_get_by_user_id_returns_tickets(self, mock_session: MagicMock) -> None:
        """Test get_by_user_id returns list of tickets."""
        repo = SupportTicketRepository(mock_session)
        user_id = uuid.uuid4()
        tickets = [
            SupportTicket(
                id=uuid.uuid4(),
                user_id=user_id,
                title="Issue 1",
                description="Description 1",
                issue_type=IssueType.BUG.value,
                status=IssueStatus.OPEN.value,
            ),
            SupportTicket(
                id=uuid.uuid4(),
                user_id=user_id,
                title="Issue 2",
                description="Description 2",
                issue_type=IssueType.FEATURE_REQUEST.value,
                status=IssueStatus.CLOSED.value,
            ),
        ]
        mock_session.exec.return_value.all.return_value = tickets

        result = repo.get_by_user_id(user_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_by_user_id_with_status_filter(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_user_id filters by status."""
        repo = SupportTicketRepository(mock_session)
        user_id = uuid.uuid4()
        open_ticket = SupportTicket(
            id=uuid.uuid4(),
            user_id=user_id,
            title="Open Issue",
            description="Description",
            issue_type=IssueType.BUG.value,
            status=IssueStatus.OPEN.value,
        )
        mock_session.exec.return_value.all.return_value = [open_ticket]

        result = repo.get_by_user_id(user_id, status=IssueStatus.OPEN)

        assert len(result) == 1
        assert result[0].status == IssueStatus.OPEN.value

    def test_get_by_user_id_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_user_id returns empty list when no tickets."""
        repo = SupportTicketRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_user_id(uuid.uuid4())

        assert result == []

    def test_get_by_user_id_with_pagination(self, mock_session: MagicMock) -> None:
        """Test get_by_user_id respects skip and limit."""
        repo = SupportTicketRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        repo.get_by_user_id(uuid.uuid4(), skip=10, limit=50)

        mock_session.exec.assert_called_once()


@pytest.mark.unit
class TestGetAll:
    """Tests for get_all method."""

    def test_get_all_returns_all_tickets(self, mock_session: MagicMock) -> None:
        """Test get_all returns all tickets."""
        repo = SupportTicketRepository(mock_session)
        tickets = [
            SupportTicket(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                title="Issue 1",
                description="Description 1",
                issue_type=IssueType.BUG.value,
                status=IssueStatus.OPEN.value,
            ),
            SupportTicket(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                title="Issue 2",
                description="Description 2",
                issue_type=IssueType.FEATURE_REQUEST.value,
                status=IssueStatus.CLOSED.value,
            ),
        ]
        mock_session.exec.return_value.all.return_value = tickets

        result = repo.get_all()

        assert len(result) == 2

    def test_get_all_with_status_filter(self, mock_session: MagicMock) -> None:
        """Test get_all filters by status."""
        repo = SupportTicketRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        repo.get_all(status=IssueStatus.OPEN)

        mock_session.exec.assert_called_once()

    def test_get_all_with_issue_type_filter(self, mock_session: MagicMock) -> None:
        """Test get_all filters by issue type."""
        repo = SupportTicketRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        repo.get_all(issue_type=IssueType.BUG)

        mock_session.exec.assert_called_once()

    def test_get_all_with_multiple_filters(self, mock_session: MagicMock) -> None:
        """Test get_all with both status and issue type filters."""
        repo = SupportTicketRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        repo.get_all(status=IssueStatus.OPEN, issue_type=IssueType.BUG)

        mock_session.exec.assert_called_once()


@pytest.mark.unit
class TestCountByUserId:
    """Tests for count_by_user_id method."""

    def test_count_by_user_id_returns_count(self, mock_session: MagicMock) -> None:
        """Test count_by_user_id returns correct count."""
        repo = SupportTicketRepository(mock_session)
        user_id = uuid.uuid4()
        tickets = [
            SupportTicket(
                id=uuid.uuid4(),
                user_id=user_id,
                title="Issue 1",
                description="Description 1",
                issue_type=IssueType.BUG.value,
                status=IssueStatus.OPEN.value,
            ),
            SupportTicket(
                id=uuid.uuid4(),
                user_id=user_id,
                title="Issue 2",
                description="Description 2",
                issue_type=IssueType.BUG.value,
                status=IssueStatus.OPEN.value,
            ),
        ]
        mock_session.exec.return_value.all.return_value = tickets

        result = repo.count_by_user_id(user_id)

        assert result == 2

    def test_count_by_user_id_with_status_filter(
        self, mock_session: MagicMock
    ) -> None:
        """Test count_by_user_id filters by status."""
        repo = SupportTicketRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.count_by_user_id(uuid.uuid4(), status=IssueStatus.OPEN)

        assert result == 0

    def test_count_by_user_id_returns_zero_when_no_tickets(
        self, mock_session: MagicMock
    ) -> None:
        """Test count_by_user_id returns 0 when no tickets."""
        repo = SupportTicketRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.count_by_user_id(uuid.uuid4())

        assert result == 0


@pytest.mark.unit
class TestCountAll:
    """Tests for count_all method."""

    def test_count_all_returns_total_count(self, mock_session: MagicMock) -> None:
        """Test count_all returns total count."""
        repo = SupportTicketRepository(mock_session)
        tickets = [
            SupportTicket(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                title="Issue 1",
                description="Description 1",
                issue_type=IssueType.BUG.value,
                status=IssueStatus.OPEN.value,
            ),
            SupportTicket(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                title="Issue 2",
                description="Description 2",
                issue_type=IssueType.BUG.value,
                status=IssueStatus.CLOSED.value,
            ),
            SupportTicket(
                id=uuid.uuid4(),
                user_id=uuid.uuid4(),
                title="Issue 3",
                description="Description 3",
                issue_type=IssueType.FEATURE_REQUEST.value,
                status=IssueStatus.OPEN.value,
            ),
        ]
        mock_session.exec.return_value.all.return_value = tickets

        result = repo.count_all()

        assert result == 3

    def test_count_all_with_filters(self, mock_session: MagicMock) -> None:
        """Test count_all with status and issue type filters."""
        repo = SupportTicketRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.count_all(status=IssueStatus.OPEN, issue_type=IssueType.BUG)

        assert result == 0

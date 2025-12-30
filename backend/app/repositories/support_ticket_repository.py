"""Support ticket repository."""

import logging
import uuid

from sqlmodel import Session, desc, select

from app.db_models.support_ticket import SupportTicket
from app.repositories.base import BaseRepository
from app.schemas.support_ticket import IssueStatus, IssueType

logger = logging.getLogger(__name__)


class SupportTicketRepository(BaseRepository[SupportTicket]):
    """Repository for SupportTicket data access."""

    def __init__(self, session: Session):
        super().__init__(SupportTicket, session)

    def get_by_user_id(
        self,
        user_id: uuid.UUID,
        status: IssueStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[SupportTicket]:
        """Get all tickets for a specific user with optional status filter."""
        logger.debug(
            f"Querying tickets by user_id: {user_id}, status={status}, skip={skip}, limit={limit}"
        )
        statement = select(SupportTicket).where(SupportTicket.user_id == user_id)

        if status is not None:
            statement = statement.where(SupportTicket.status == status.value)

        statement = (
            statement.order_by(desc(SupportTicket.created_at)).offset(skip).limit(limit)
        )

        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} tickets for user {user_id}")
        return results

    def get_all(  # type: ignore[override]
        self,
        status: IssueStatus | None = None,
        issue_type: IssueType | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[SupportTicket]:
        """Get all tickets with optional filters (admin only)."""
        logger.debug(
            f"Querying all tickets: status={status}, issue_type={issue_type}, skip={skip}, limit={limit}"
        )
        statement = select(SupportTicket)

        if status is not None:
            statement = statement.where(SupportTicket.status == status.value)

        if issue_type is not None:
            statement = statement.where(SupportTicket.issue_type == issue_type.value)

        statement = (
            statement.order_by(desc(SupportTicket.created_at)).offset(skip).limit(limit)
        )

        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} tickets")
        return results

    def count_by_user_id(
        self, user_id: uuid.UUID, status: IssueStatus | None = None
    ) -> int:
        """Count tickets for a specific user with optional status filter."""
        logger.debug(f"Counting tickets for user: {user_id}, status={status}")
        statement = select(SupportTicket).where(SupportTicket.user_id == user_id)

        if status is not None:
            statement = statement.where(SupportTicket.status == status.value)

        count = len(list(self.session.exec(statement).all()))
        logger.debug(f"User {user_id} has {count} tickets")
        return count

    def count_all(
        self, status: IssueStatus | None = None, issue_type: IssueType | None = None
    ) -> int:
        """Count all tickets with optional filters (admin only)."""
        logger.debug(f"Counting all tickets: status={status}, issue_type={issue_type}")
        statement = select(SupportTicket)

        if status is not None:
            statement = statement.where(SupportTicket.status == status.value)

        if issue_type is not None:
            statement = statement.where(SupportTicket.issue_type == issue_type.value)

        count = len(list(self.session.exec(statement).all()))
        logger.debug(f"Total tickets: {count}")
        return count

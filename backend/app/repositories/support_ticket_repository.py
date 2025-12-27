"""Support ticket repository."""

import uuid

from sqlmodel import Session, select

from app.db_models.support_ticket import SupportTicket
from app.repositories.base import BaseRepository
from app.schemas.support_ticket import IssueStatus, IssueType


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
        statement = select(SupportTicket).where(SupportTicket.user_id == user_id)

        if status is not None:
            statement = statement.where(SupportTicket.status == status.value)

        statement = (
            statement.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit)
        )

        return list(self.session.exec(statement).all())

    def get_all(
        self,
        status: IssueStatus = IssueStatus.OPEN,
        issue_type: IssueType | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[SupportTicket]:
        """Get all tickets with optional filters (admin only)."""
        statement = select(SupportTicket)

        if status is not None:
            statement = statement.where(SupportTicket.status == status.value)

        if issue_type is not None:
            statement = statement.where(SupportTicket.issue_type == issue_type.value)

        statement = (
            statement.order_by(SupportTicket.created_at.desc()).offset(skip).limit(limit)
        )

        return list(self.session.exec(statement).all())

    def count_by_user_id(
        self, user_id: uuid.UUID, status: IssueStatus = IssueStatus.OPEN
    ) -> int:
        """Count tickets for a specific user with optional status filter."""
        statement = select(SupportTicket).where(SupportTicket.user_id == user_id)

        if status is not None:
            statement = statement.where(SupportTicket.status == status.value)

        return len(list(self.session.exec(statement).all()))

    def count_all(
        self, status: IssueStatus | None = None, issue_type: IssueType | None = None
    ) -> int:
        """Count all tickets with optional filters (admin only)."""
        statement = select(SupportTicket)

        if status is not None:
            statement = statement.where(SupportTicket.status == status.value)

        if issue_type is not None:
            statement = statement.where(SupportTicket.issue_type == issue_type.value)

        return len(list(self.session.exec(statement).all()))

"""Support ticket service."""

import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.support_ticket import SupportTicket
from app.repositories.support_ticket_repository import SupportTicketRepository
from app.schemas.support_ticket import (
    IssueStatus,
    IssueType,
    SupportTicketCreate,
    SupportTicketUpdate,
)


class SupportTicketService:
    """Service for support ticket business logic."""

    def __init__(self, session: Session):
        self.session = session
        self.support_ticket_repo = SupportTicketRepository(session)

    def create_support_ticket(
        self, user_id: uuid.UUID, support_ticket_in: SupportTicketCreate
    ) -> SupportTicket:
        """Create a new support ticket for a user."""
        support_ticket = SupportTicket(
            user_id=user_id,
            issue_type=support_ticket_in.issue_type.value,
            title=support_ticket_in.title,
            description=support_ticket_in.description,
            status=IssueStatus.OPEN.value,
        )
        return self.support_ticket_repo.create(support_ticket)

    def get_user_support_tickets(
        self,
        user_id: uuid.UUID,
        status: IssueStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[SupportTicket], int]:
        """Get all support tickets for a user with pagination."""
        tickets = self.support_ticket_repo.get_by_user_id(
            user_id, status=status, skip=skip, limit=limit
        )
        count = self.support_ticket_repo.count_by_user_id(user_id, status=status)
        return tickets, count

    def get_all_support_tickets_admin(
        self,
        status: IssueStatus | None = None,
        issue_type: IssueType | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[SupportTicket], int]:
        """Get all support tickets for admin with filters and pagination."""
        tickets = self.support_ticket_repo.get_all(
            status=status, issue_type=issue_type, skip=skip, limit=limit
        )
        count = self.support_ticket_repo.count_all(status=status, issue_type=issue_type)
        return tickets, count

    def get_support_ticket_by_id(self, support_ticket_id: uuid.UUID) -> SupportTicket | None:
        """Get a single support ticket by ID."""
        return self.support_ticket_repo.get_by_id(support_ticket_id)

    def update_support_ticket(
        self, support_ticket: SupportTicket, support_ticket_in: SupportTicketUpdate
    ) -> SupportTicket:
        """Update a support ticket."""
        update_data = support_ticket_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(support_ticket, key, value)
        support_ticket.updated_at = datetime.utcnow()
        return self.support_ticket_repo.update(support_ticket)

    def resolve_support_ticket(
        self, support_ticket: SupportTicket, resolved_by_user_id: uuid.UUID
    ) -> SupportTicket:
        """Mark a support ticket as resolved."""
        support_ticket.status = IssueStatus.CLOSED.value
        support_ticket.resolved_at = datetime.utcnow()
        support_ticket.resolved_by_user_id = resolved_by_user_id
        support_ticket.updated_at = datetime.utcnow()
        return self.support_ticket_repo.update(support_ticket)

    def reopen_support_ticket(self, support_ticket: SupportTicket) -> SupportTicket:
        """Reopen a closed support ticket."""
        support_ticket.status = IssueStatus.OPEN.value
        support_ticket.resolved_at = None
        support_ticket.resolved_by_user_id = None
        support_ticket.updated_at = datetime.utcnow()
        return self.support_ticket_repo.update(support_ticket)

    def delete_support_ticket(self, support_ticket: SupportTicket) -> None:
        """Delete a support ticket."""
        self.support_ticket_repo.delete(support_ticket)

    def can_user_access_support_ticket(
        self, support_ticket: SupportTicket, user_id: uuid.UUID, is_superuser: bool
    ) -> bool:
        """Check if user can access a support ticket."""
        return is_superuser or support_ticket.user_id == user_id

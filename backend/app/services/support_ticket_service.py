"""Support ticket service."""

import logging
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

logger = logging.getLogger(__name__)


class SupportTicketService:
    """Service for support ticket business logic."""

    def __init__(self, session: Session):
        self.session = session
        self.support_ticket_repo = SupportTicketRepository(session)

    def create_support_ticket(
        self, user_id: uuid.UUID, support_ticket_in: SupportTicketCreate
    ) -> SupportTicket:
        """Create a new support ticket for a user."""
        logger.info(
            f"Creating support ticket: {support_ticket_in.title} "
            f"for user: {user_id}"
        )
        try:
            support_ticket = SupportTicket(
                user_id=user_id,
                issue_type=support_ticket_in.issue_type.value,
                title=support_ticket_in.title,
                description=support_ticket_in.description,
                status=IssueStatus.OPEN.value,
            )
            created_ticket = self.support_ticket_repo.create(support_ticket)
            logger.info(
                f"Support ticket created: {created_ticket.title} "
                f"(ID: {created_ticket.id})"
            )
            return created_ticket
        except Exception as e:
            logger.error(
                f"Failed to create support ticket: {support_ticket_in.title} "
                f"for user: {user_id}",
                exc_info=True,
            )
            raise

    def get_user_support_tickets(
        self,
        user_id: uuid.UUID,
        status: IssueStatus | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[SupportTicket], int]:
        """Get all support tickets for a user with pagination."""
        logger.debug(
            f"Fetching support tickets for user: {user_id}, "
            f"status={status}, skip={skip}, limit={limit}"
        )
        tickets = self.support_ticket_repo.get_by_user_id(
            user_id, status=status, skip=skip, limit=limit
        )
        count = self.support_ticket_repo.count_by_user_id(user_id, status=status)
        logger.info(
            f"Retrieved {len(tickets)} support tickets for user {user_id} "
            f"(total: {count})"
        )
        return tickets, count

    def get_all_support_tickets_admin(
        self,
        status: IssueStatus | None = None,
        issue_type: IssueType | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[SupportTicket], int]:
        """Get all support tickets for admin with filters and pagination."""
        logger.debug(
            f"Fetching all support tickets (admin), "
            f"status={status}, issue_type={issue_type}, skip={skip}, limit={limit}"
        )
        tickets = self.support_ticket_repo.get_all(
            status=status, issue_type=issue_type, skip=skip, limit=limit
        )
        count = self.support_ticket_repo.count_all(status=status, issue_type=issue_type)
        logger.info(f"Retrieved {len(tickets)} support tickets (total: {count})")
        return tickets, count

    def get_support_ticket_by_id(
        self, support_ticket_id: uuid.UUID
    ) -> SupportTicket | None:
        """Get a single support ticket by ID."""
        logger.debug(f"Fetching support ticket by ID: {support_ticket_id}")
        ticket = self.support_ticket_repo.get_by_id(support_ticket_id)
        if ticket:
            logger.info(f"Support ticket found: {ticket.title} (ID: {ticket.id})")
        else:
            logger.info(f"Support ticket not found: ID {support_ticket_id}")
        return ticket

    def update_support_ticket(
        self, support_ticket: SupportTicket, support_ticket_in: SupportTicketUpdate
    ) -> SupportTicket:
        """Update a support ticket."""
        logger.info(
            f"Updating support ticket: {support_ticket.title} "
            f"(ID: {support_ticket.id})"
        )
        try:
            update_data = support_ticket_in.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(support_ticket, key, value)
            support_ticket.updated_at = datetime.utcnow()
            updated_ticket = self.support_ticket_repo.update(support_ticket)
            logger.info(
                f"Support ticket updated: {updated_ticket.title} "
                f"(ID: {updated_ticket.id})"
            )
            return updated_ticket
        except Exception as e:
            logger.error(
                f"Failed to update support ticket: {support_ticket.title} "
                f"(ID: {support_ticket.id})",
                exc_info=True,
            )
            raise

    def resolve_support_ticket(
        self, support_ticket: SupportTicket, resolved_by_user_id: uuid.UUID
    ) -> SupportTicket:
        """Mark a support ticket as resolved."""
        logger.info(
            f"Resolving support ticket: {support_ticket.title} "
            f"(ID: {support_ticket.id}) by user: {resolved_by_user_id}"
        )
        try:
            support_ticket.status = IssueStatus.CLOSED.value
            support_ticket.resolved_at = datetime.utcnow()
            support_ticket.resolved_by_user_id = resolved_by_user_id
            support_ticket.updated_at = datetime.utcnow()
            resolved_ticket = self.support_ticket_repo.update(support_ticket)
            logger.info(
                f"Support ticket resolved: {resolved_ticket.title} "
                f"(ID: {resolved_ticket.id})"
            )
            return resolved_ticket
        except Exception as e:
            logger.error(
                f"Failed to resolve support ticket: {support_ticket.title} "
                f"(ID: {support_ticket.id})",
                exc_info=True,
            )
            raise

    def reopen_support_ticket(self, support_ticket: SupportTicket) -> SupportTicket:
        """Reopen a closed support ticket."""
        logger.info(
            f"Reopening support ticket: {support_ticket.title} "
            f"(ID: {support_ticket.id})"
        )
        try:
            support_ticket.status = IssueStatus.OPEN.value
            support_ticket.resolved_at = None
            support_ticket.resolved_by_user_id = None
            support_ticket.updated_at = datetime.utcnow()
            reopened_ticket = self.support_ticket_repo.update(support_ticket)
            logger.info(
                f"Support ticket reopened: {reopened_ticket.title} "
                f"(ID: {reopened_ticket.id})"
            )
            return reopened_ticket
        except Exception as e:
            logger.error(
                f"Failed to reopen support ticket: {support_ticket.title} "
                f"(ID: {support_ticket.id})",
                exc_info=True,
            )
            raise

    def delete_support_ticket(self, support_ticket: SupportTicket) -> None:
        """Delete a support ticket."""
        logger.info(
            f"Deleting support ticket: {support_ticket.title} "
            f"(ID: {support_ticket.id})"
        )
        try:
            self.support_ticket_repo.delete(support_ticket)
            logger.info(
                f"Support ticket deleted: {support_ticket.title} "
                f"(ID: {support_ticket.id})"
            )
        except Exception as e:
            logger.error(
                f"Failed to delete support ticket: {support_ticket.title} "
                f"(ID: {support_ticket.id})",
                exc_info=True,
            )
            raise

    def can_user_access_support_ticket(
        self, support_ticket: SupportTicket, user_id: uuid.UUID, is_superuser: bool
    ) -> bool:
        """Check if user can access a support ticket."""
        can_access = is_superuser or support_ticket.user_id == user_id
        if can_access:
            logger.debug(
                f"User {user_id} has access to support ticket: "
                f"{support_ticket.title} (ID: {support_ticket.id})"
            )
        else:
            logger.warning(
                f"User {user_id} denied access to support ticket: "
                f"{support_ticket.title} (ID: {support_ticket.id})"
            )
        return can_access

"""Support Ticket API routes."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import CurrentUser, SessionDep, get_current_active_admin
from app.db_models.user import User
from app.schemas.common import Message
from app.schemas.support_ticket import (
    IssueStatus,
    IssueType,
    SupportTicketCreate,
    SupportTicketPublic,
    SupportTicketPublicWithUser,
    SupportTicketsPublic,
    SupportTicketUpdate,
)
from app.services.support_ticket_service import SupportTicketService
from app.utils.logging_decorator import log_route

router = APIRouter(prefix="/support-tickets", tags=["issues"])

# Type alias for superuser dependency
SuperUser = Annotated[User, Depends(get_current_active_admin)]


@router.post("/", response_model=SupportTicketPublic)
@log_route
def create_support_ticket(
    session: SessionDep,
    current_user: CurrentUser,
    support_ticket_in: SupportTicketCreate,
) -> Any:
    """
    Create a new support ticket.
    """
    support_ticket_service = SupportTicketService(session)
    support_ticket = support_ticket_service.create_support_ticket(
        current_user.id, support_ticket_in
    )
    return support_ticket


@router.get("/me", response_model=SupportTicketsPublic)
@log_route
def get_my_support_tickets(
    session: SessionDep,
    current_user: CurrentUser,
    status: IssueStatus | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get current user's support tickets with optional status filter.
    """
    support_ticket_service = SupportTicketService(session)
    tickets, count = support_ticket_service.get_user_support_tickets(
        current_user.id, status=status, skip=skip, limit=limit
    )
    return SupportTicketsPublic(data=tickets, count=count)


@router.get("/{support_ticket_id}", response_model=SupportTicketPublic)
@log_route
def get_support_ticket(
    session: SessionDep, current_user: CurrentUser, support_ticket_id: uuid.UUID
) -> Any:
    """
    Get a specific support ticket by ID (owner or admin only).
    """
    support_ticket_service = SupportTicketService(session)
    support_ticket = support_ticket_service.get_support_ticket_by_id(support_ticket_id)

    if not support_ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    if not support_ticket_service.can_user_access_support_ticket(
        support_ticket, current_user.id, current_user.is_admin
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return support_ticket


@router.patch("/{support_ticket_id}", response_model=SupportTicketPublic)
@log_route
def update_support_ticket(
    session: SessionDep,
    current_user: CurrentUser,
    support_ticket_id: uuid.UUID,
    support_ticket_in: SupportTicketUpdate,
) -> Any:
    """
    Update a support ticket (owner only).
    """
    support_ticket_service = SupportTicketService(session)
    support_ticket = support_ticket_service.get_support_ticket_by_id(support_ticket_id)

    if not support_ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    if support_ticket.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    support_ticket = support_ticket_service.update_support_ticket(
        support_ticket, support_ticket_in
    )
    return support_ticket


@router.delete("/{support_ticket_id}", response_model=Message)
@log_route
def delete_support_ticket(
    session: SessionDep, current_user: CurrentUser, support_ticket_id: uuid.UUID
) -> Any:
    """
    Delete a support ticket (owner or admin).
    """
    support_ticket_service = SupportTicketService(session)
    support_ticket = support_ticket_service.get_support_ticket_by_id(support_ticket_id)

    if not support_ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    if not support_ticket_service.can_user_access_support_ticket(
        support_ticket, current_user.id, current_user.is_admin
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    support_ticket_service.delete_support_ticket(support_ticket)
    return Message(message="Support ticket deleted successfully")


@router.get("/admin/all", response_model=list[SupportTicketPublicWithUser])
@log_route
def get_all_support_tickets_admin(
    session: SessionDep,
    current_user: SuperUser,  # noqa: ARG001
    status: IssueStatus | None = None,
    issue_type: IssueType | None = None,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get all support tickets with filters (admin only).
    """
    support_ticket_service = SupportTicketService(session)
    tickets, count = support_ticket_service.get_all_support_tickets_admin(
        status=status, issue_type=issue_type, skip=skip, limit=limit
    )

    # Enrich tickets with user information
    result = []
    for ticket in tickets:
        # Get user who created the ticket
        user = session.get(User, ticket.user_id)
        user_email = user.email if user else "Unknown"
        user_full_name = user.full_name if user else None

        # Get user who resolved the ticket (if applicable)
        resolved_by_email = None
        if ticket.resolved_by_user_id:
            resolved_by_user = session.get(User, ticket.resolved_by_user_id)
            resolved_by_email = resolved_by_user.email if resolved_by_user else None

        ticket_with_user = SupportTicketPublicWithUser(
            id=ticket.id,
            user_id=ticket.user_id,
            issue_type=ticket.issue_type,
            title=ticket.title,
            description=ticket.description,
            status=ticket.status,
            resolved_by_user_id=ticket.resolved_by_user_id,
            resolved_at=ticket.resolved_at,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            user_email=user_email,
            user_full_name=user_full_name,
            resolved_by_email=resolved_by_email,
        )
        result.append(ticket_with_user)

    return result


@router.patch("/{support_ticket_id}/resolve", response_model=SupportTicketPublic)
@log_route
def resolve_support_ticket(
    session: SessionDep,
    support_ticket_id: uuid.UUID,
    current_user: SuperUser,
) -> Any:
    """
    Mark a support ticket as resolved (admin only).
    """
    support_ticket_service = SupportTicketService(session)
    support_ticket = support_ticket_service.get_support_ticket_by_id(support_ticket_id)

    if not support_ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    support_ticket = support_ticket_service.resolve_support_ticket(
        support_ticket, current_user.id
    )
    return support_ticket


@router.patch("/{support_ticket_id}/reopen", response_model=SupportTicketPublic)
@log_route
def reopen_support_ticket(
    session: SessionDep,
    support_ticket_id: uuid.UUID,
    current_user: SuperUser,  # noqa: ARG001
) -> Any:
    """
    Reopen a closed support ticket (admin only).
    """
    support_ticket_service = SupportTicketService(session)
    support_ticket = support_ticket_service.get_support_ticket_by_id(support_ticket_id)

    if not support_ticket:
        raise HTTPException(status_code=404, detail="Support ticket not found")

    support_ticket = support_ticket_service.reopen_support_ticket(support_ticket)
    return support_ticket

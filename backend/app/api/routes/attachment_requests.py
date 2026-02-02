"""Attachment Request API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.schemas.attachment_request import (
    AttachmentRequestCreate,
    AttachmentRequestPublic,
    AttachmentRequestWithDetails,
    MyPendingRequestResponse,
    PendingCountResponse,
)
from app.schemas.common import Message
from app.services.attachment_request_service import AttachmentRequestService
from app.utils.logging_decorator import log_route

router = APIRouter(prefix="/attachment-requests", tags=["attachment-requests"])


@router.post("/", response_model=AttachmentRequestPublic)
@log_route
def create_attachment_request(
    session: SessionDep,
    current_user: CurrentUser,
    request_in: AttachmentRequestCreate,
) -> Any:
    """
    Create a new attachment request.

    The requester wants to attach their account to an existing Person record.
    The request will be sent to the user who created that Person for approval.
    """
    service = AttachmentRequestService(session)
    attachment_request = service.create_request(current_user.id, request_in)
    return attachment_request


@router.get("/to-approve", response_model=list[AttachmentRequestWithDetails])
@log_route
def get_requests_to_approve(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get all pending attachment requests for the current user to approve.

    Returns requests where the current user is the approver (creator of the target person).
    Includes full details about the requester and target person.
    """
    service = AttachmentRequestService(session)
    requests = service.get_requests_to_approve(current_user.id)
    return requests


@router.get("/my-pending", response_model=MyPendingRequestResponse)
@log_route
def get_my_pending_request(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get the current user's pending attachment request.

    Returns 404 if no pending request exists.
    """
    service = AttachmentRequestService(session)
    request = service.get_my_pending_request(current_user.id)
    if not request:
        raise HTTPException(
            status_code=404,
            detail="No pending attachment request found",
        )
    return request


@router.get("/pending-count", response_model=PendingCountResponse)
@log_route
def get_pending_count(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Get the count of pending attachment requests for the current user.

    Used for displaying a badge in the sidebar navigation.
    """
    service = AttachmentRequestService(session)
    count = service.get_pending_count(current_user.id)
    return PendingCountResponse(count=count)


@router.post("/{request_id}/approve", response_model=Message)
@log_route
def approve_attachment_request(
    session: SessionDep,
    current_user: CurrentUser,
    request_id: uuid.UUID,
) -> Any:
    """
    Approve an attachment request.

    Only the approver (creator of the target person) can approve.
    This will:
    - Link the requester's user account to the target person
    - Delete the requester's temporary person record
    - Mark the request as approved
    """
    service = AttachmentRequestService(session)
    service.approve_request(request_id, current_user.id)
    return Message(message="Attachment request approved successfully")


@router.post("/{request_id}/deny", response_model=Message)
@log_route
def deny_attachment_request(
    session: SessionDep,
    current_user: CurrentUser,
    request_id: uuid.UUID,
) -> Any:
    """
    Deny an attachment request.

    Only the approver (creator of the target person) can deny.
    This will:
    - Delete the requester's temporary person record
    - Delete the requester's user account
    - Mark the request as denied
    """
    service = AttachmentRequestService(session)
    service.deny_request(request_id, current_user.id)
    return Message(message="Attachment request denied successfully")


@router.post("/{request_id}/cancel", response_model=Message)
@log_route
def cancel_attachment_request(
    session: SessionDep,
    current_user: CurrentUser,
    request_id: uuid.UUID,
) -> Any:
    """
    Cancel an attachment request.

    Only the requester can cancel their own request.
    This will only update the request status to cancelled.
    The requester's person and user records are preserved.
    """
    service = AttachmentRequestService(session)
    service.cancel_request(request_id, current_user.id)
    return Message(message="Attachment request cancelled successfully")

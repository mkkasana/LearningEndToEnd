"""Profile API routes."""

from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.schemas.profile import ProfileCompletionStatus
from app.services.profile_service import ProfileService
from app.utils.logging_decorator import log_route

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/completion-status", response_model=ProfileCompletionStatus)
@log_route
def get_profile_completion_status(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get current user's profile completion status.
    Returns whether person and address information is complete.
    """
    profile_service = ProfileService(session)
    return profile_service.check_profile_completion(current_user.id)

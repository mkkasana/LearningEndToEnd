"""Profile API routes."""

from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser, SessionDep
from app.schemas.person.person_search import PersonMatchResult
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


@router.get("/duplicate-check", response_model=list[PersonMatchResult])
@log_route
def get_duplicate_check(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Search for potential duplicate persons matching the current user's data.
    
    Returns persons that could be the same person as the current user,
    filtered to exclude:
    - The current user's own person record
    - Persons that already have a linked user account
    - Inactive persons
    
    Only returns persons with a match score >= 40%.
    """
    profile_service = ProfileService(session)
    return profile_service.get_duplicate_matches(current_user.id)


@router.post("/complete-without-attachment", response_model=ProfileCompletionStatus)
@log_route
def complete_without_attachment(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Complete profile without attaching to an existing person.
    
    Activates the current user's person record, marking the duplicate
    check step as complete.
    
    Returns 400 error if user has a pending attachment request.
    """
    profile_service = ProfileService(session)
    return profile_service.complete_without_attachment(current_user.id)

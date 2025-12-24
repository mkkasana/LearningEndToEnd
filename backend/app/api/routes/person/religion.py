"""Person Religion API routes."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.schemas.common import Message
from app.schemas.person.person_religion import (
    PersonReligionCreate,
    PersonReligionPublic,
    PersonReligionUpdate,
)
from app.services.person.person_religion_service import PersonReligionService
from app.services.person.person_service import PersonService

router = APIRouter()


@router.get("/me/religion", response_model=PersonReligionPublic)
def get_my_religion(session: SessionDep, current_user: CurrentUser) -> Any:
    """Get religion for current user's person profile."""
    person_service = PersonService(session)
    religion_service = PersonReligionService(session)
    
    person = person_service.get_person_by_user_id(current_user.id)
    if not person:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    religion = religion_service.get_by_person_id(current_user.id)
    if not religion:
        raise HTTPException(status_code=404, detail="Religion not found")
    
    return religion


@router.post("/me/religion", response_model=PersonReligionPublic)
def create_my_religion(
    session: SessionDep, current_user: CurrentUser, religion_in: PersonReligionCreate
) -> Any:
    """Create religion for current user's person profile."""
    person_service = PersonService(session)
    religion_service = PersonReligionService(session)
    
    person = person_service.get_person_by_user_id(current_user.id)
    if not person:
        raise HTTPException(status_code=404, detail="Person profile not found")
    
    # Check if religion already exists
    existing = religion_service.get_by_person_id(current_user.id)
    if existing:
        raise HTTPException(
            status_code=400, detail="Religion already exists for this person"
        )
    
    religion = religion_service.create_person_religion(current_user.id, religion_in)
    return religion


@router.patch("/me/religion", response_model=PersonReligionPublic)
def update_my_religion(
    session: SessionDep, current_user: CurrentUser, religion_in: PersonReligionUpdate
) -> Any:
    """Update religion for current user."""
    religion_service = PersonReligionService(session)
    
    religion = religion_service.get_by_person_id(current_user.id)
    if not religion:
        raise HTTPException(status_code=404, detail="Religion not found")
    
    religion = religion_service.update_person_religion(religion, religion_in)
    return religion


@router.delete("/me/religion", response_model=Message)
def delete_my_religion(session: SessionDep, current_user: CurrentUser) -> Any:
    """Delete religion for current user."""
    religion_service = PersonReligionService(session)
    
    religion = religion_service.get_by_person_id(current_user.id)
    if not religion:
        raise HTTPException(status_code=404, detail="Religion not found")
    
    religion_service.delete_person_religion(religion)
    return Message(message="Religion deleted successfully")

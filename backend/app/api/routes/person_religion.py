"""Person Religion API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import CurrentUser, get_db
from app.schemas.person.person_religion import (
    PersonReligionCreate,
    PersonReligionPublic,
    PersonReligionUpdate,
)
from app.services.person.person_religion_service import PersonReligionService

router = APIRouter()


@router.post(
    "/",
    response_model=PersonReligionPublic,
    status_code=status.HTTP_201_CREATED,
    summary="Create religion for current user",
)
def create_my_religion(
    *,
    session: Session = Depends(get_db),
    current_user: CurrentUser,
    religion_in: PersonReligionCreate,
) -> PersonReligionPublic:
    """Create religion information for the current user."""
    service = PersonReligionService(session)
    
    # Check if user already has religion
    existing = service.get_by_person_id(current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has religion information. Use PUT to update.",
        )
    
    person_religion = service.create_person_religion(current_user.id, religion_in)
    session.commit()
    session.refresh(person_religion)
    return PersonReligionPublic.model_validate(person_religion)


@router.get(
    "/me",
    response_model=PersonReligionPublic,
    summary="Get current user's religion",
)
def get_my_religion(
    *,
    session: Session = Depends(get_db),
    current_user: CurrentUser,
) -> PersonReligionPublic:
    """Get religion information for the current user."""
    service = PersonReligionService(session)
    person_religion = service.get_by_person_id(current_user.id)
    
    if not person_religion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Religion information not found for current user",
        )
    
    return PersonReligionPublic.model_validate(person_religion)


@router.put(
    "/me",
    response_model=PersonReligionPublic,
    summary="Update current user's religion",
)
def update_my_religion(
    *,
    session: Session = Depends(get_db),
    current_user: CurrentUser,
    religion_in: PersonReligionUpdate,
) -> PersonReligionPublic:
    """Update religion information for the current user."""
    service = PersonReligionService(session)
    person_religion = service.get_by_person_id(current_user.id)
    
    if not person_religion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Religion information not found. Use POST to create.",
        )
    
    updated_religion = service.update_person_religion(person_religion, religion_in)
    session.commit()
    session.refresh(updated_religion)
    return PersonReligionPublic.model_validate(updated_religion)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete current user's religion",
)
def delete_my_religion(
    *,
    session: Session = Depends(get_db),
    current_user: CurrentUser,
) -> None:
    """Delete religion information for the current user."""
    service = PersonReligionService(session)
    person_religion = service.get_by_person_id(current_user.id)
    
    if not person_religion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Religion information not found",
        )
    
    service.delete_person_religion(person_religion)
    session.commit()

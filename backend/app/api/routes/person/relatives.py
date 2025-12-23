"""Person Relatives API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.schemas.person import PersonRelationshipPublic
from app.services.person import PersonRelationshipService, PersonService

router = APIRouter()


@router.get("/{user_id}/parents", response_model=list[PersonRelationshipPublic])
def get_parents(session: SessionDep, user_id: uuid.UUID) -> Any:
    """
    Get all parents (father and mother) for a person.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(user_id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    relationship_service = PersonRelationshipService(session)
    parents = relationship_service.get_parents(person.user_id)
    return parents


@router.get("/{user_id}/children", response_model=list[PersonRelationshipPublic])
def get_children(session: SessionDep, user_id: uuid.UUID) -> Any:
    """
    Get all children (sons and daughters) for a person.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(user_id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    relationship_service = PersonRelationshipService(session)
    children = relationship_service.get_children(person.user_id)
    return children


@router.get("/{user_id}/spouses", response_model=list[PersonRelationshipPublic])
def get_spouses(session: SessionDep, user_id: uuid.UUID) -> Any:
    """
    Get all spouses for a person.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(user_id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    relationship_service = PersonRelationshipService(session)
    spouses = relationship_service.get_spouses(person.user_id)
    return spouses

"""Life Events API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.schemas.common import Message
from app.schemas.person.life_event import (
    LifeEventCreate,
    LifeEventPublic,
    LifeEventsPublic,
    LifeEventUpdate,
)
from app.services.person.life_event_service import LifeEventService
from app.services.person.person_service import PersonService
from app.utils.logging_decorator import log_route

router = APIRouter(prefix="/life-events", tags=["life-events"])


def _get_user_person_id(session: SessionDep, current_user: CurrentUser) -> uuid.UUID:
    """Get the person ID for the current user.

    Raises HTTPException if user has no person record.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=400,
            detail="User must have a person record to manage life events",
        )

    return person.id


@router.get("/me", response_model=LifeEventsPublic)
@log_route
def get_my_life_events(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get current user's life events.

    Returns life events sorted by date (most recent first):
    - Year descending
    - Month descending (nulls last)
    - Date descending (nulls last)
    """
    person_id = _get_user_person_id(session, current_user)

    life_event_service = LifeEventService(session)
    events, count = life_event_service.get_life_events(
        person_id, skip=skip, limit=limit
    )

    return LifeEventsPublic(data=events, count=count)


@router.post("/", response_model=LifeEventPublic)
@log_route
def create_life_event(
    session: SessionDep,
    current_user: CurrentUser,
    life_event_in: LifeEventCreate,
) -> Any:
    """
    Create a new life event for the current user.

    Required fields:
    - event_type: One of birth, marriage, death, purchase, sale, achievement,
                  education, career, health, travel, other
    - title: Event title (max 100 characters)
    - event_year: Year when the event occurred

    Optional fields:
    - description: Event description (max 500 characters)
    - event_month: Month (1-12)
    - event_date: Day (1-31, validated against month/year)
    - Address fields: country_id, state_id, district_id, sub_district_id, locality_id
    - address_details: Additional address info (max 30 characters)
    """
    person_id = _get_user_person_id(session, current_user)

    life_event_service = LifeEventService(session)

    try:
        life_event = life_event_service.create_life_event(person_id, life_event_in)
        return life_event
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/{life_event_id}", response_model=LifeEventPublic)
@log_route
def get_life_event(
    session: SessionDep,
    current_user: CurrentUser,
    life_event_id: uuid.UUID,
) -> Any:
    """
    Get a specific life event by ID.

    Users can only access their own life events.
    Admins and superusers can access all events.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)
    person_id = person.id if person else None

    life_event_service = LifeEventService(session)
    life_event = life_event_service.get_life_event_by_id(life_event_id)

    if not life_event:
        raise HTTPException(status_code=404, detail="Life event not found")

    if not life_event_service.user_can_access_event(
        current_user, life_event, person_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return life_event


@router.put("/{life_event_id}", response_model=LifeEventPublic)
@log_route
def update_life_event(
    session: SessionDep,
    current_user: CurrentUser,
    life_event_id: uuid.UUID,
    life_event_in: LifeEventUpdate,
) -> Any:
    """
    Update a life event.

    Users can only update their own life events.
    All fields are optional - only provided fields will be updated.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)
    person_id = person.id if person else None

    life_event_service = LifeEventService(session)
    life_event = life_event_service.get_life_event_by_id(life_event_id)

    if not life_event:
        raise HTTPException(status_code=404, detail="Life event not found")

    if not life_event_service.user_can_access_event(
        current_user, life_event, person_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    try:
        updated_event = life_event_service.update_life_event(life_event, life_event_in)
        return updated_event
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.delete("/{life_event_id}", response_model=Message)
@log_route
def delete_life_event(
    session: SessionDep,
    current_user: CurrentUser,
    life_event_id: uuid.UUID,
) -> Any:
    """
    Delete a life event.

    Users can only delete their own life events.
    Admins and superusers can delete any event.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)
    person_id = person.id if person else None

    life_event_service = LifeEventService(session)
    life_event = life_event_service.get_life_event_by_id(life_event_id)

    if not life_event:
        raise HTTPException(status_code=404, detail="Life event not found")

    if not life_event_service.user_can_access_event(
        current_user, life_event, person_id
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    life_event_service.delete_life_event(life_event)
    return Message(message="Life event deleted successfully")

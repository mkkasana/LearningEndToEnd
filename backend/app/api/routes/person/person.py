"""Person API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.schemas.person import (
    PersonAddressCreate,
    PersonAddressPublic,
    PersonAddressUpdate,
    PersonCreate,
    PersonPublic,
    PersonUpdate,
)
from app.services.person import PersonAddressService, PersonService

router = APIRouter()


@router.get("/me", response_model=PersonPublic)
def get_my_person(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    return person


@router.post("/me", response_model=PersonPublic)
def create_my_person(
    session: SessionDep, current_user: CurrentUser, person_in: PersonCreate
) -> Any:
    """
    Create person profile for current user.
    """
    person_service = PersonService(session)

    # Check if user already has a person profile
    if person_service.user_has_person(current_user.id):
        raise HTTPException(
            status_code=400,
            detail="Person profile already exists for this user",
        )

    # Ensure user_id matches current user
    if person_in.user_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot create person profile for another user",
        )

    person = person_service.create_person(person_in)
    return person


@router.patch("/me", response_model=PersonPublic)
def update_my_person(
    session: SessionDep, current_user: CurrentUser, person_in: PersonUpdate
) -> Any:
    """
    Update current user's person profile.
    """
    person_service = PersonService(session)

    person = person_service.get_person_by_user_id(current_user.id)
    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    updated_person = person_service.update_person(person, person_in)
    return updated_person


@router.delete("/me")
def delete_my_person(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete current user's person profile.
    """
    person_service = PersonService(session)

    person = person_service.get_person_by_user_id(current_user.id)
    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    person_service.delete_person(person)
    return {"message": "Person profile deleted successfully"}


# Admin endpoints
@router.get(
    "/{user_id}",
    response_model=PersonPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def get_person_by_user_id(session: SessionDep, user_id: uuid.UUID) -> Any:
    """
    Get person by user ID (admin only).
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(user_id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    return person


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_person_by_user_id(session: SessionDep, user_id: uuid.UUID) -> Any:
    """
    Delete person by user ID (admin only).
    """
    person_service = PersonService(session)

    person = person_service.get_person_by_user_id(user_id)
    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    person_service.delete_person(person)
    return {"message": "Person deleted successfully"}


# ============================================================================
# Person Address Endpoints
# ============================================================================


@router.get("/me/addresses", response_model=list[PersonAddressPublic])
def get_my_addresses(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get all addresses for current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    address_service = PersonAddressService(session)
    addresses = address_service.get_addresses_by_person(person.user_id)
    return addresses


@router.post("/me/addresses", response_model=PersonAddressPublic)
def create_my_address(
    session: SessionDep, current_user: CurrentUser, address_in: PersonAddressCreate
) -> Any:
    """
    Create new address for current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    address_service = PersonAddressService(session)
    address = address_service.create_address(person.user_id, address_in)
    return address


@router.get("/me/addresses/{address_id}", response_model=PersonAddressPublic)
def get_my_address(
    session: SessionDep, current_user: CurrentUser, address_id: uuid.UUID
) -> Any:
    """
    Get specific address by ID for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    address_service = PersonAddressService(session)
    address = address_service.get_address_by_id(address_id)

    if not address or address.person_id != person.user_id:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    return address


@router.patch("/me/addresses/{address_id}", response_model=PersonAddressPublic)
def update_my_address(
    session: SessionDep,
    current_user: CurrentUser,
    address_id: uuid.UUID,
    address_in: PersonAddressUpdate,
) -> Any:
    """
    Update address for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    address_service = PersonAddressService(session)
    address = address_service.get_address_by_id(address_id)

    if not address or address.person_id != person.user_id:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    updated_address = address_service.update_address(address, address_in)
    return updated_address


@router.delete("/me/addresses/{address_id}")
def delete_my_address(
    session: SessionDep, current_user: CurrentUser, address_id: uuid.UUID
) -> Any:
    """
    Delete address for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    address_service = PersonAddressService(session)
    address = address_service.get_address_by_id(address_id)

    if not address or address.person_id != person.user_id:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    address_service.delete_address(address)
    return {"message": "Address deleted successfully"}

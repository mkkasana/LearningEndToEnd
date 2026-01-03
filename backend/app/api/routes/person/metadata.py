"""Person metadata API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import SessionDep, get_current_active_admin
from app.schemas.person import (
    GenderDetailPublic,
    ProfessionCreate,
    ProfessionDetailPublic,
    ProfessionUpdate,
)
from app.services.person import GenderService, ProfessionService
from app.utils.logging_decorator import log_route

router = APIRouter(
    prefix="/person",
    tags=["person-metadata"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# Professions Endpoints
# ============================================================================


@router.get("/professions")
@log_route
def get_professions(session: SessionDep) -> Any:
    """
    Get list of professions for dropdown options.
    Public endpoint - no authentication required.
    """
    profession_service = ProfessionService(session)
    professions = profession_service.get_professions()
    return professions


@router.get("/professions/{profession_id}", response_model=ProfessionDetailPublic)
@log_route
def get_profession_by_id(session: SessionDep, profession_id: uuid.UUID) -> Any:
    """
    Get a specific profession by ID.
    Public endpoint - no authentication required.
    """
    profession_service = ProfessionService(session)
    profession = profession_service.get_profession_by_id(profession_id)

    if not profession:
        raise HTTPException(
            status_code=404,
            detail="Profession not found",
        )

    return profession


@router.post(
    "/professions",
    response_model=ProfessionDetailPublic,
    dependencies=[Depends(get_current_active_admin)],
)
@log_route
def create_profession(session: SessionDep, profession_in: ProfessionCreate) -> Any:
    """
    Create a new profession.
    Requires admin authentication.
    """
    profession_service = ProfessionService(session)

    # Check if profession name already exists
    if profession_service.name_exists(profession_in.name):
        raise HTTPException(
            status_code=400,
            detail=f"Profession with name '{profession_in.name}' already exists",
        )

    profession = profession_service.create_profession(profession_in)
    return profession


@router.patch(
    "/professions/{profession_id}",
    response_model=ProfessionDetailPublic,
    dependencies=[Depends(get_current_active_admin)],
)
@log_route
def update_profession(
    session: SessionDep,
    profession_id: uuid.UUID,
    profession_in: ProfessionUpdate,
) -> Any:
    """
    Update a profession.
    Requires admin authentication.
    """
    profession_service = ProfessionService(session)

    # Get existing profession
    profession = profession_service.get_profession_by_id(profession_id)
    if not profession:
        raise HTTPException(
            status_code=404,
            detail="Profession not found",
        )

    # Check if new name conflicts with existing profession
    if profession_in.name:
        if profession_service.name_exists(
            profession_in.name, exclude_profession_id=profession_id
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Profession with name '{profession_in.name}' already exists",
            )

    updated_profession = profession_service.update_profession(profession, profession_in)
    return updated_profession


@router.delete(
    "/professions/{profession_id}",
    dependencies=[Depends(get_current_active_admin)],
)
@log_route
def delete_profession(session: SessionDep, profession_id: uuid.UUID) -> Any:
    """
    Delete a profession.
    Requires admin authentication.
    """
    profession_service = ProfessionService(session)

    # Get existing profession
    profession = profession_service.get_profession_by_id(profession_id)
    if not profession:
        raise HTTPException(
            status_code=404,
            detail="Profession not found",
        )

    profession_service.delete_profession(profession)
    return {"message": "Profession deleted successfully"}


# ============================================================================
# Genders Endpoints (Read-only - genders are static/hardcoded)
# ============================================================================


@router.get("/genders")
@log_route
def get_genders() -> Any:
    """
    Get list of genders for dropdown options.
    Public endpoint - no authentication required.
    Returns hardcoded gender values (no database call).
    """
    gender_service = GenderService()
    genders = gender_service.get_genders()
    return genders


@router.get("/genders/{gender_id}", response_model=GenderDetailPublic)
@log_route
def get_gender_by_id(gender_id: uuid.UUID) -> Any:
    """
    Get a specific gender by ID.
    Public endpoint - no authentication required.
    Returns hardcoded gender values (no database call).
    """
    gender_service = GenderService()
    gender = gender_service.get_gender_by_id(gender_id)

    if not gender:
        raise HTTPException(
            status_code=404,
            detail="Gender not found",
        )

    return gender

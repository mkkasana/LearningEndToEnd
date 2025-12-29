"""Person metadata API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import SessionDep, get_current_active_superuser
from app.schemas.person import (
    GenderCreate,
    GenderDetailPublic,
    GenderUpdate,
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
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def create_profession(session: SessionDep, profession_in: ProfessionCreate) -> Any:
    """
    Create a new profession.
    Requires superuser authentication.
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
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def update_profession(
    session: SessionDep,
    profession_id: uuid.UUID,
    profession_in: ProfessionUpdate,
) -> Any:
    """
    Update a profession.
    Requires superuser authentication.
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
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def delete_profession(session: SessionDep, profession_id: uuid.UUID) -> Any:
    """
    Delete a profession.
    Requires superuser authentication.
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
# Genders Endpoints
# ============================================================================


@router.get("/genders")
@log_route
def get_genders(session: SessionDep) -> Any:
    """
    Get list of genders for dropdown options.
    Public endpoint - no authentication required.
    """
    gender_service = GenderService(session)
    genders = gender_service.get_genders()
    return genders


@router.get("/genders/{gender_id}", response_model=GenderDetailPublic)
@log_route
def get_gender_by_id(session: SessionDep, gender_id: uuid.UUID) -> Any:
    """
    Get a specific gender by ID.
    Public endpoint - no authentication required.
    """
    gender_service = GenderService(session)
    gender = gender_service.get_gender_by_id(gender_id)

    if not gender:
        raise HTTPException(
            status_code=404,
            detail="Gender not found",
        )

    return gender


@router.post(
    "/genders",
    response_model=GenderDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def create_gender(session: SessionDep, gender_in: GenderCreate) -> Any:
    """
    Create a new gender.
    Requires superuser authentication.
    """
    gender_service = GenderService(session)

    # Check if gender code already exists
    if gender_service.code_exists(gender_in.code):
        raise HTTPException(
            status_code=400,
            detail=f"Gender with code '{gender_in.code.upper()}' already exists",
        )

    gender = gender_service.create_gender(gender_in)
    return gender


@router.patch(
    "/genders/{gender_id}",
    response_model=GenderDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def update_gender(
    session: SessionDep,
    gender_id: uuid.UUID,
    gender_in: GenderUpdate,
) -> Any:
    """
    Update a gender.
    Requires superuser authentication.
    """
    gender_service = GenderService(session)

    # Get existing gender
    gender = gender_service.get_gender_by_id(gender_id)
    if not gender:
        raise HTTPException(
            status_code=404,
            detail="Gender not found",
        )

    # Check if new code conflicts with existing gender
    if gender_in.code:
        if gender_service.code_exists(gender_in.code, exclude_gender_id=gender_id):
            raise HTTPException(
                status_code=400,
                detail=f"Gender with code '{gender_in.code.upper()}' already exists",
            )

    updated_gender = gender_service.update_gender(gender, gender_in)
    return updated_gender


@router.delete(
    "/genders/{gender_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def delete_gender(session: SessionDep, gender_id: uuid.UUID) -> Any:
    """
    Delete a gender.
    Requires superuser authentication.
    """
    gender_service = GenderService(session)

    # Get existing gender
    gender = gender_service.get_gender_by_id(gender_id)
    if not gender:
        raise HTTPException(
            status_code=404,
            detail="Gender not found",
        )

    gender_service.delete_gender(gender)
    return {"message": "Gender deleted successfully"}

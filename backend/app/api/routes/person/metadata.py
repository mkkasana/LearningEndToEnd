"""Person metadata API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import SessionDep, get_current_active_superuser
from app.schemas.person import (
    ProfessionCreate,
    ProfessionDetailPublic,
    ProfessionUpdate,
)
from app.services.person import ProfessionService

router = APIRouter(
    prefix="/person",
    tags=["person-metadata"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# Professions Endpoints
# ============================================================================


@router.get("/professions")
def get_professions(session: SessionDep) -> Any:
    """
    Get list of professions for dropdown options.
    Public endpoint - no authentication required.
    """
    profession_service = ProfessionService(session)
    professions = profession_service.get_professions()
    return professions


@router.get("/professions/{profession_id}", response_model=ProfessionDetailPublic)
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

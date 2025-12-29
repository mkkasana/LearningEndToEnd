"""Religion metadata API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import SessionDep, get_current_active_superuser
from app.schemas.religion import (
    ReligionCategoryCreate,
    ReligionCategoryDetailPublic,
    ReligionCategoryUpdate,
    ReligionCreate,
    ReligionDetailPublic,
    ReligionSubCategoryCreate,
    ReligionSubCategoryDetailPublic,
    ReligionSubCategoryUpdate,
    ReligionUpdate,
)
from app.services.religion import (
    ReligionCategoryService,
    ReligionService,
    ReligionSubCategoryService,
)
from app.utils.logging_decorator import log_route

router = APIRouter(
    prefix="/religion",
    tags=["religion-metadata"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# Religions Endpoints
# ============================================================================


@router.get("/religions")
@log_route
def get_religions(session: SessionDep) -> Any:
    """
    Get list of religions for dropdown options.
    Public endpoint - no authentication required.
    """
    religion_service = ReligionService(session)
    religions = religion_service.get_religions()
    return religions


@router.get("/religions/{religion_id}", response_model=ReligionDetailPublic)
@log_route
def get_religion_by_id(session: SessionDep, religion_id: uuid.UUID) -> Any:
    """
    Get a specific religion by ID.
    Public endpoint - no authentication required.
    """
    religion_service = ReligionService(session)
    religion = religion_service.get_religion_by_id(religion_id)

    if not religion:
        raise HTTPException(
            status_code=404,
            detail="Religion not found",
        )

    return religion


@router.post(
    "/religions",
    response_model=ReligionDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def create_religion(session: SessionDep, religion_in: ReligionCreate) -> Any:
    """
    Create a new religion.
    Requires superuser authentication.
    """
    religion_service = ReligionService(session)

    # Check if religion code already exists
    if religion_service.code_exists(religion_in.code):
        raise HTTPException(
            status_code=400,
            detail=f"Religion with code '{religion_in.code.upper()}' already exists",
        )

    religion = religion_service.create_religion(religion_in)
    return religion


@router.patch(
    "/religions/{religion_id}",
    response_model=ReligionDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def update_religion(
    session: SessionDep,
    religion_id: uuid.UUID,
    religion_in: ReligionUpdate,
) -> Any:
    """
    Update a religion.
    Requires superuser authentication.
    """
    religion_service = ReligionService(session)

    # Get existing religion
    religion = religion_service.get_religion_by_id(religion_id)
    if not religion:
        raise HTTPException(
            status_code=404,
            detail="Religion not found",
        )

    # Check if new code conflicts with existing religion
    if religion_in.code:
        if religion_service.code_exists(
            religion_in.code, exclude_religion_id=religion_id
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Religion with code '{religion_in.code.upper()}' already exists",
            )

    updated_religion = religion_service.update_religion(religion, religion_in)
    return updated_religion


@router.delete(
    "/religions/{religion_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def delete_religion(session: SessionDep, religion_id: uuid.UUID) -> Any:
    """
    Delete a religion.
    Requires superuser authentication.
    """
    religion_service = ReligionService(session)

    # Get existing religion
    religion = religion_service.get_religion_by_id(religion_id)
    if not religion:
        raise HTTPException(
            status_code=404,
            detail="Religion not found",
        )

    religion_service.delete_religion(religion)
    return {"message": "Religion deleted successfully"}


# ============================================================================
# Religion Categories Endpoints
# ============================================================================


@router.get("/religion/{religion_id}/categories")
@log_route
def get_categories_by_religion(session: SessionDep, religion_id: uuid.UUID) -> Any:
    """
    Get list of categories for a specific religion.
    Public endpoint - no authentication required.
    """
    # Verify religion exists
    religion_service = ReligionService(session)
    religion = religion_service.get_religion_by_id(religion_id)
    if not religion:
        raise HTTPException(
            status_code=404,
            detail="Religion not found",
        )

    # Get categories for the religion
    category_service = ReligionCategoryService(session)
    categories = category_service.get_categories_by_religion(religion_id)
    return categories


@router.get("/categories/{category_id}", response_model=ReligionCategoryDetailPublic)
@log_route
def get_category_by_id(session: SessionDep, category_id: uuid.UUID) -> Any:
    """
    Get a specific category by ID.
    Public endpoint - no authentication required.
    """
    category_service = ReligionCategoryService(session)
    category = category_service.get_category_by_id(category_id)

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category


@router.post(
    "/categories",
    response_model=ReligionCategoryDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def create_category(session: SessionDep, category_in: ReligionCategoryCreate) -> Any:
    """
    Create a new religion category.
    Requires superuser authentication.
    """
    # Verify religion exists
    religion_service = ReligionService(session)
    religion = religion_service.get_religion_by_id(category_in.religion_id)
    if not religion:
        raise HTTPException(
            status_code=404,
            detail="Religion not found",
        )

    category_service = ReligionCategoryService(session)

    # Check if category code already exists in this religion
    if category_in.code and category_service.code_exists(
        category_in.code, category_in.religion_id
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Category with code '{category_in.code.upper()}' already exists in this religion",
        )

    category = category_service.create_category(category_in)
    return category


@router.patch(
    "/categories/{category_id}",
    response_model=ReligionCategoryDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def update_category(
    session: SessionDep,
    category_id: uuid.UUID,
    category_in: ReligionCategoryUpdate,
) -> Any:
    """
    Update a religion category.
    Requires superuser authentication.
    """
    category_service = ReligionCategoryService(session)

    # Get existing category
    category = category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    # Check if new code conflicts with existing category in the same religion
    if category_in.code:
        if category_service.code_exists(
            category_in.code, category.religion_id, exclude_category_id=category_id
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Category with code '{category_in.code.upper()}' already exists in this religion",
            )

    updated_category = category_service.update_category(category, category_in)
    return updated_category


@router.delete(
    "/categories/{category_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def delete_category(session: SessionDep, category_id: uuid.UUID) -> Any:
    """
    Delete a religion category.
    Requires superuser authentication.
    """
    category_service = ReligionCategoryService(session)

    # Get existing category
    category = category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    category_service.delete_category(category)
    return {"message": "Category deleted successfully"}


# ============================================================================
# Religion Sub-Categories Endpoints
# ============================================================================


@router.get("/category/{category_id}/sub-categories")
@log_route
def get_sub_categories_by_category(session: SessionDep, category_id: uuid.UUID) -> Any:
    """
    Get list of sub-categories for a specific category.
    Public endpoint - no authentication required.
    """
    # Verify category exists
    category_service = ReligionCategoryService(session)
    category = category_service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    # Get sub-categories for the category
    sub_category_service = ReligionSubCategoryService(session)
    sub_categories = sub_category_service.get_sub_categories_by_category(category_id)
    return sub_categories


@router.get(
    "/sub-categories/{sub_category_id}", response_model=ReligionSubCategoryDetailPublic
)
@log_route
def get_sub_category_by_id(session: SessionDep, sub_category_id: uuid.UUID) -> Any:
    """
    Get a specific sub-category by ID.
    Public endpoint - no authentication required.
    """
    sub_category_service = ReligionSubCategoryService(session)
    sub_category = sub_category_service.get_sub_category_by_id(sub_category_id)

    if not sub_category:
        raise HTTPException(
            status_code=404,
            detail="Sub-category not found",
        )

    return sub_category


@router.post(
    "/sub-categories",
    response_model=ReligionSubCategoryDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def create_sub_category(
    session: SessionDep, sub_category_in: ReligionSubCategoryCreate
) -> Any:
    """
    Create a new religion sub-category.
    Requires superuser authentication.
    """
    # Verify category exists
    category_service = ReligionCategoryService(session)
    category = category_service.get_category_by_id(sub_category_in.category_id)
    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    sub_category_service = ReligionSubCategoryService(session)

    # Check if sub-category code already exists in this category
    if sub_category_in.code and sub_category_service.code_exists(
        sub_category_in.code, sub_category_in.category_id
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Sub-category with code '{sub_category_in.code.upper()}' already exists in this category",
        )

    sub_category = sub_category_service.create_sub_category(sub_category_in)
    return sub_category


@router.patch(
    "/sub-categories/{sub_category_id}",
    response_model=ReligionSubCategoryDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def update_sub_category(
    session: SessionDep,
    sub_category_id: uuid.UUID,
    sub_category_in: ReligionSubCategoryUpdate,
) -> Any:
    """
    Update a religion sub-category.
    Requires superuser authentication.
    """
    sub_category_service = ReligionSubCategoryService(session)

    # Get existing sub-category
    sub_category = sub_category_service.get_sub_category_by_id(sub_category_id)
    if not sub_category:
        raise HTTPException(
            status_code=404,
            detail="Sub-category not found",
        )

    # Check if new code conflicts with existing sub-category in the same category
    if sub_category_in.code:
        if sub_category_service.code_exists(
            sub_category_in.code,
            sub_category.category_id,
            exclude_sub_category_id=sub_category_id,
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Sub-category with code '{sub_category_in.code.upper()}' already exists in this category",
            )

    updated_sub_category = sub_category_service.update_sub_category(
        sub_category, sub_category_in
    )
    return updated_sub_category


@router.delete(
    "/sub-categories/{sub_category_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
@log_route
def delete_sub_category(session: SessionDep, sub_category_id: uuid.UUID) -> Any:
    """
    Delete a religion sub-category.
    Requires superuser authentication.
    """
    sub_category_service = ReligionSubCategoryService(session)

    # Get existing sub-category
    sub_category = sub_category_service.get_sub_category_by_id(sub_category_id)
    if not sub_category:
        raise HTTPException(
            status_code=404,
            detail="Sub-category not found",
        )

    sub_category_service.delete_sub_category(sub_category)
    return {"message": "Sub-category deleted successfully"}

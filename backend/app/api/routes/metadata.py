import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import SessionDep, get_current_active_superuser
from app.schemas.country import CountryCreate, CountryDetailPublic, CountryUpdate
from app.services.country_service import CountryService

router = APIRouter(prefix="/metadata", tags=["metadata"])


@router.get("/address/countries")
def get_countries(session: SessionDep) -> Any:
    """
    Get list of countries for dropdown options.
    Public endpoint - no authentication required.
    """
    country_service = CountryService(session)
    countries = country_service.get_countries()
    return countries


@router.post(
    "/address/countries",
    response_model=CountryDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_country(session: SessionDep, country_in: CountryCreate) -> Any:
    """
    Create a new country.
    Requires superuser authentication.
    """
    country_service = CountryService(session)
    
    # Check if country code already exists
    if country_service.code_exists(country_in.code):
        raise HTTPException(
            status_code=400,
            detail=f"Country with code '{country_in.code.upper()}' already exists",
        )
    
    country = country_service.create_country(country_in)
    return country


@router.patch(
    "/address/countries/{country_id}",
    response_model=CountryDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_country(
    session: SessionDep,
    country_id: uuid.UUID,
    country_in: CountryUpdate,
) -> Any:
    """
    Update a country.
    Requires superuser authentication.
    """
    country_service = CountryService(session)
    
    # Get existing country
    country = country_service.get_country_by_id(country_id)
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found",
        )
    
    # Check if new code conflicts with existing country
    if country_in.code:
        if country_service.code_exists(country_in.code, exclude_country_id=country_id):
            raise HTTPException(
                status_code=400,
                detail=f"Country with code '{country_in.code.upper()}' already exists",
            )
    
    updated_country = country_service.update_country(country, country_in)
    return updated_country

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import SessionDep, get_current_active_superuser
from app.schemas.country import CountryCreate, CountryDetailPublic, CountryUpdate
from app.schemas.state import StateCreate, StateDetailPublic, StateUpdate
from app.services.country_service import CountryService
from app.services.state_service import StateService

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


# ============================================================================
# States Endpoints
# ============================================================================


@router.get("/address/country/{country_id}/states")
def get_states_by_country(session: SessionDep, country_id: uuid.UUID) -> Any:
    """
    Get list of states for a specific country.
    Public endpoint - no authentication required.
    """
    # Verify country exists
    country_service = CountryService(session)
    country = country_service.get_country_by_id(country_id)
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found",
        )

    # Get states for the country
    state_service = StateService(session)
    states = state_service.get_states_by_country(country_id)
    return states


@router.post(
    "/address/states",
    response_model=StateDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_state(session: SessionDep, state_in: StateCreate) -> Any:
    """
    Create a new state.
    Requires superuser authentication.
    """
    # Verify country exists
    country_service = CountryService(session)
    country = country_service.get_country_by_id(state_in.country_id)
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found",
        )

    state_service = StateService(session)

    # Check if state code already exists in this country
    if state_in.code and state_service.code_exists(state_in.code, state_in.country_id):
        raise HTTPException(
            status_code=400,
            detail=f"State with code '{state_in.code.upper()}' already exists in this country",
        )

    state = state_service.create_state(state_in)
    return state


@router.patch(
    "/address/states/{state_id}",
    response_model=StateDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_state(
    session: SessionDep,
    state_id: uuid.UUID,
    state_in: StateUpdate,
) -> Any:
    """
    Update a state.
    Requires superuser authentication.
    """
    state_service = StateService(session)

    # Get existing state
    state = state_service.get_state_by_id(state_id)
    if not state:
        raise HTTPException(
            status_code=404,
            detail="State not found",
        )

    # Check if new code conflicts with existing state in the same country
    if state_in.code:
        if state_service.code_exists(
            state_in.code, state.country_id, exclude_state_id=state_id
        ):
            raise HTTPException(
                status_code=400,
                detail=f"State with code '{state_in.code.upper()}' already exists in this country",
            )

    updated_state = state_service.update_state(state, state_in)
    return updated_state

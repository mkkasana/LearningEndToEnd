import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import SessionDep, get_current_active_superuser
from app.schemas.address import (
    CountryCreate,
    CountryDetailPublic,
    CountryUpdate,
    DistrictCreate,
    DistrictDetailPublic,
    DistrictUpdate,
    LocalityCreate,
    LocalityDetailPublic,
    LocalityUpdate,
    StateCreate,
    StateDetailPublic,
    StateUpdate,
    SubDistrictCreate,
    SubDistrictDetailPublic,
    SubDistrictUpdate,
)
from app.services.address import (
    CountryService,
    DistrictService,
    LocalityService,
    StateService,
    SubDistrictService,
)

router = APIRouter(
    prefix="/address",
    tags=["address-metadata"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# Countries Endpoints
# ============================================================================


@router.get("/countries")
def get_countries(session: SessionDep) -> Any:
    """
    Get list of countries for dropdown options.
    Public endpoint - no authentication required.
    """
    country_service = CountryService(session)
    countries = country_service.get_countries()
    return countries


@router.get("/countries/{country_id}", response_model=CountryDetailPublic)
def get_country_by_id(session: SessionDep, country_id: uuid.UUID) -> Any:
    """
    Get a specific country by ID.
    Public endpoint - no authentication required.
    """
    country_service = CountryService(session)
    country = country_service.get_country_by_id(country_id)
    
    if not country:
        raise HTTPException(
            status_code=404,
            detail="Country not found",
        )
    
    return country


@router.post(
    "/countries",
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
    "/countries/{country_id}",
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


@router.delete(
    "/countries/{country_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_country(session: SessionDep, country_id: uuid.UUID) -> Any:
    """
    Delete a country.
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

    country_service.delete_country(country)
    return {"message": "Country deleted successfully"}


# ============================================================================
# States Endpoints
# ============================================================================


@router.get("/country/{country_id}/states")
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


@router.get("/states/{state_id}", response_model=StateDetailPublic)
def get_state_by_id(session: SessionDep, state_id: uuid.UUID) -> Any:
    """
    Get a specific state by ID.
    Public endpoint - no authentication required.
    """
    state_service = StateService(session)
    state = state_service.get_state_by_id(state_id)
    
    if not state:
        raise HTTPException(
            status_code=404,
            detail="State not found",
        )
    
    return state


@router.post(
    "/states",
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
    "/states/{state_id}",
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


@router.delete(
    "/states/{state_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_state(session: SessionDep, state_id: uuid.UUID) -> Any:
    """
    Delete a state.
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

    state_service.delete_state(state)
    return {"message": "State deleted successfully"}


# ============================================================================
# Districts Endpoints
# ============================================================================


@router.get("/state/{state_id}/districts")
def get_districts_by_state(session: SessionDep, state_id: uuid.UUID) -> Any:
    """
    Get list of districts for a specific state.
    Public endpoint - no authentication required.
    """
    # Verify state exists
    state_service = StateService(session)
    state = state_service.get_state_by_id(state_id)
    if not state:
        raise HTTPException(
            status_code=404,
            detail="State not found",
        )

    # Get districts for the state
    district_service = DistrictService(session)
    districts = district_service.get_districts_by_state(state_id)
    return districts


@router.get("/districts/{district_id}", response_model=DistrictDetailPublic)
def get_district_by_id(session: SessionDep, district_id: uuid.UUID) -> Any:
    """
    Get a specific district by ID.
    Public endpoint - no authentication required.
    """
    district_service = DistrictService(session)
    district = district_service.get_district_by_id(district_id)

    if not district:
        raise HTTPException(
            status_code=404,
            detail="District not found",
        )

    return district


@router.post(
    "/districts",
    response_model=DistrictDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_district(session: SessionDep, district_in: DistrictCreate) -> Any:
    """
    Create a new district.
    Requires superuser authentication.
    """
    # Verify state exists
    state_service = StateService(session)
    state = state_service.get_state_by_id(district_in.state_id)
    if not state:
        raise HTTPException(
            status_code=404,
            detail="State not found",
        )

    district_service = DistrictService(session)

    # Check if district code already exists in this state
    if district_in.code and district_service.code_exists(
        district_in.code, district_in.state_id
    ):
        raise HTTPException(
            status_code=400,
            detail=f"District with code '{district_in.code.upper()}' already exists in this state",
        )

    district = district_service.create_district(district_in)
    return district


@router.patch(
    "/districts/{district_id}",
    response_model=DistrictDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_district(
    session: SessionDep,
    district_id: uuid.UUID,
    district_in: DistrictUpdate,
) -> Any:
    """
    Update a district.
    Requires superuser authentication.
    """
    district_service = DistrictService(session)

    # Get existing district
    district = district_service.get_district_by_id(district_id)
    if not district:
        raise HTTPException(
            status_code=404,
            detail="District not found",
        )

    # Check if new code conflicts with existing district in the same state
    if district_in.code:
        if district_service.code_exists(
            district_in.code, district.state_id, exclude_district_id=district_id
        ):
            raise HTTPException(
                status_code=400,
                detail=f"District with code '{district_in.code.upper()}' already exists in this state",
            )

    updated_district = district_service.update_district(district, district_in)
    return updated_district


@router.delete(
    "/districts/{district_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_district(session: SessionDep, district_id: uuid.UUID) -> Any:
    """
    Delete a district.
    Requires superuser authentication.
    """
    district_service = DistrictService(session)

    # Get existing district
    district = district_service.get_district_by_id(district_id)
    if not district:
        raise HTTPException(
            status_code=404,
            detail="District not found",
        )

    district_service.delete_district(district)
    return {"message": "District deleted successfully"}


# ============================================================================
# Sub-Districts (Tehsils) Endpoints
# ============================================================================


@router.get("/district/{district_id}/sub-districts")
def get_sub_districts_by_district(session: SessionDep, district_id: uuid.UUID) -> Any:
    """
    Get list of sub-districts (tehsils/counties) for a specific district.
    Public endpoint - no authentication required.
    """
    # Verify district exists
    district_service = DistrictService(session)
    district = district_service.get_district_by_id(district_id)
    if not district:
        raise HTTPException(
            status_code=404,
            detail="District not found",
        )

    # Get sub-districts for the district
    sub_district_service = SubDistrictService(session)
    sub_districts = sub_district_service.get_sub_districts_by_district(district_id)
    return sub_districts


@router.get("/sub-districts/{sub_district_id}", response_model=SubDistrictDetailPublic)
def get_sub_district_by_id(session: SessionDep, sub_district_id: uuid.UUID) -> Any:
    """
    Get a specific sub-district by ID.
    Public endpoint - no authentication required.
    """
    sub_district_service = SubDistrictService(session)
    sub_district = sub_district_service.get_sub_district_by_id(sub_district_id)

    if not sub_district:
        raise HTTPException(
            status_code=404,
            detail="Sub-district not found",
        )

    return sub_district


@router.post(
    "/sub-districts",
    response_model=SubDistrictDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_sub_district(session: SessionDep, sub_district_in: SubDistrictCreate) -> Any:
    """
    Create a new sub-district (tehsil/county).
    Requires superuser authentication.
    """
    # Verify district exists
    district_service = DistrictService(session)
    district = district_service.get_district_by_id(sub_district_in.district_id)
    if not district:
        raise HTTPException(
            status_code=404,
            detail="District not found",
        )

    sub_district_service = SubDistrictService(session)

    # Check if sub-district code already exists in this district
    if sub_district_in.code and sub_district_service.code_exists(
        sub_district_in.code, sub_district_in.district_id
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Sub-district with code '{sub_district_in.code.upper()}' already exists in this district",
        )

    sub_district = sub_district_service.create_sub_district(sub_district_in)
    return sub_district


@router.patch(
    "/sub-districts/{sub_district_id}",
    response_model=SubDistrictDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_sub_district(
    session: SessionDep,
    sub_district_id: uuid.UUID,
    sub_district_in: SubDistrictUpdate,
) -> Any:
    """
    Update a sub-district (tehsil/county).
    Requires superuser authentication.
    """
    sub_district_service = SubDistrictService(session)

    # Get existing sub-district
    sub_district = sub_district_service.get_sub_district_by_id(sub_district_id)
    if not sub_district:
        raise HTTPException(
            status_code=404,
            detail="Sub-district not found",
        )

    # Check if new code conflicts with existing sub-district in the same district
    if sub_district_in.code:
        if sub_district_service.code_exists(
            sub_district_in.code,
            sub_district.district_id,
            exclude_sub_district_id=sub_district_id,
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Sub-district with code '{sub_district_in.code.upper()}' already exists in this district",
            )

    updated_sub_district = sub_district_service.update_sub_district(
        sub_district, sub_district_in
    )
    return updated_sub_district


@router.delete(
    "/sub-districts/{sub_district_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_sub_district(session: SessionDep, sub_district_id: uuid.UUID) -> Any:
    """
    Delete a sub-district (tehsil/county).
    Requires superuser authentication.
    """
    sub_district_service = SubDistrictService(session)

    # Get existing sub-district
    sub_district = sub_district_service.get_sub_district_by_id(sub_district_id)
    if not sub_district:
        raise HTTPException(
            status_code=404,
            detail="Sub-district not found",
        )

    sub_district_service.delete_sub_district(sub_district)
    return {"message": "Sub-district deleted successfully"}


# ============================================================================
# Localities (Villages) Endpoints
# ============================================================================


@router.get("/sub-district/{sub_district_id}/localities")
def get_localities_by_sub_district(
    session: SessionDep, sub_district_id: uuid.UUID
) -> Any:
    """
    Get list of localities (villages) for a specific sub-district.
    Public endpoint - no authentication required.
    """
    # Verify sub-district exists
    sub_district_service = SubDistrictService(session)
    sub_district = sub_district_service.get_sub_district_by_id(sub_district_id)
    if not sub_district:
        raise HTTPException(
            status_code=404,
            detail="Sub-district not found",
        )

    # Get localities for the sub-district
    locality_service = LocalityService(session)
    localities = locality_service.get_localities_by_sub_district(sub_district_id)
    return localities


@router.get("/localities/{locality_id}", response_model=LocalityDetailPublic)
def get_locality_by_id(session: SessionDep, locality_id: uuid.UUID) -> Any:
    """
    Get a specific locality by ID.
    Public endpoint - no authentication required.
    """
    locality_service = LocalityService(session)
    locality = locality_service.get_locality_by_id(locality_id)

    if not locality:
        raise HTTPException(
            status_code=404,
            detail="Locality not found",
        )

    return locality


@router.post(
    "/localities",
    response_model=LocalityDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_locality(session: SessionDep, locality_in: LocalityCreate) -> Any:
    """
    Create a new locality (village).
    Requires superuser authentication.
    """
    # Verify sub-district exists
    sub_district_service = SubDistrictService(session)
    sub_district = sub_district_service.get_sub_district_by_id(
        locality_in.sub_district_id
    )
    if not sub_district:
        raise HTTPException(
            status_code=404,
            detail="Sub-district not found",
        )

    locality_service = LocalityService(session)

    # Check if locality code already exists in this sub-district
    if locality_in.code and locality_service.code_exists(
        locality_in.code, locality_in.sub_district_id
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Locality with code '{locality_in.code.upper()}' already exists in this sub-district",
        )

    locality = locality_service.create_locality(locality_in)
    return locality


@router.patch(
    "/localities/{locality_id}",
    response_model=LocalityDetailPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_locality(
    session: SessionDep,
    locality_id: uuid.UUID,
    locality_in: LocalityUpdate,
) -> Any:
    """
    Update a locality (village).
    Requires superuser authentication.
    """
    locality_service = LocalityService(session)

    # Get existing locality
    locality = locality_service.get_locality_by_id(locality_id)
    if not locality:
        raise HTTPException(
            status_code=404,
            detail="Locality not found",
        )

    # Check if new code conflicts with existing locality in the same sub-district
    if locality_in.code:
        if locality_service.code_exists(
            locality_in.code,
            locality.sub_district_id,
            exclude_locality_id=locality_id,
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Locality with code '{locality_in.code.upper()}' already exists in this sub-district",
            )

    updated_locality = locality_service.update_locality(locality, locality_in)
    return updated_locality


@router.delete(
    "/localities/{locality_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_locality(session: SessionDep, locality_id: uuid.UUID) -> Any:
    """
    Delete a locality (village).
    Requires superuser authentication.
    """
    locality_service = LocalityService(session)

    # Get existing locality
    locality = locality_service.get_locality_by_id(locality_id)
    if not locality:
        raise HTTPException(
            status_code=404,
            detail="Locality not found",
        )

    locality_service.delete_locality(locality)
    return {"message": "Locality deleted successfully"}

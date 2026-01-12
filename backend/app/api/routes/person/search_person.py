"""Person search API routes for global person search functionality."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.schemas.person.person_search import (
    PersonSearchFilterRequest,
    PersonSearchResponse,
)
from app.services.person.person_search_service import PersonSearchService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/search", response_model=PersonSearchResponse)
def search_persons(
    session: SessionDep,
    current_user: CurrentUser,
    request: PersonSearchFilterRequest,
) -> Any:
    """
    Search for persons with optional filters and pagination.

    This endpoint provides global person search functionality for the Search page.
    It supports filtering by:
    - Address (country, state, district, sub-district, locality)
    - Religion (religion, category, sub-category)
    - Demographics (gender, birth year range)
    - Name (fuzzy matching with 40% threshold)

    Results are paginated with skip/limit parameters.

    **Request Body:**
    - country_id, state_id, district_id, sub_district_id: Required address filters
    - locality_id: Optional locality filter
    - religion_id, religion_category_id: Required religion filters
    - religion_sub_category_id: Optional religion sub-category filter
    - gender_id: Optional gender filter
    - birth_year_from, birth_year_to: Optional birth year range
    - first_name, last_name: Optional name filters (fuzzy matching)
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 20, max: 100)

    **Response:**
    - results: List of matching persons
    - total: Total count of matching persons (for pagination UI)
    - skip: Number of records skipped
    - limit: Maximum records per page

    _Requirements: 10.1, 10.2_
    """
    logger.info(
        f"Global person search request from user {current_user.email}: "
        f"address=({request.country_id}, {request.state_id}, {request.district_id}), "
        f"religion={request.religion_id}, "
        f"name=({request.first_name}, {request.last_name}), "
        f"skip={request.skip}, limit={request.limit}"
    )

    try:
        search_service = PersonSearchService(session)
        response = search_service.search_persons(request)

        logger.info(
            f"Search returned {len(response.results)} results "
            f"(total: {response.total}) for user {current_user.email}"
        )
        return response

    except ValueError as e:
        logger.error(
            f"Validation error in global person search for user {current_user.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            f"Unexpected error in global person search for user {current_user.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching for persons",
        )

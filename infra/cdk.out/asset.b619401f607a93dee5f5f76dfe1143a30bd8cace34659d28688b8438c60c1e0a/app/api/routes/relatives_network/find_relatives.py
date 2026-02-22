"""Relatives Network API routes for finding relatives within a family network."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.schemas.relatives_network import (
    RelativesNetworkRequest,
    RelativesNetworkResponse,
)
from app.services.relatives_network import RelativesNetworkService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/find", response_model=RelativesNetworkResponse)
def find_relatives(
    session: SessionDep,
    current_user: CurrentUser,
    request: RelativesNetworkRequest,
) -> Any:
    """
    Find relatives within a family network up to a specified depth.

    Performs BFS traversal from the specified person through family relationships,
    applying filters for living status, gender, and address, and returns a list
    of relatives with their details.

    **Request Body:**
    - person_id: The person to find relatives for (UUID)
    - depth: Search depth - number of relationship hops (default: 3, min: 1)
    - depth_mode: 'up_to' returns all relatives from depth 1 to N,
                  'only_at' returns only relatives exactly at depth N (default: 'up_to')
    - living_only: If True, exclude deceased relatives (default: True)
    - gender_id: Filter by gender ID (optional)
    - country_id: Filter by country ID (optional)
    - state_id: Filter by state ID (optional)
    - district_id: Filter by district ID (optional)
    - sub_district_id: Filter by sub-district ID (optional)
    - locality_id: Filter by locality ID (optional)

    **Returns:**
    - person_id: The person ID from the request
    - total_count: Total number of relatives found
    - depth: The depth value used in the search
    - depth_mode: The depth mode used ('up_to' or 'only_at')
    - relatives: List of relatives with person details and depth information

    **Errors:**
    - 404: Person not found
    - 400: Invalid depth_mode (must be 'up_to' or 'only_at')
    """
    logger.info(
        f"Relatives network request from user {current_user.email}: "
        f"person={request.person_id}, depth={request.depth}, "
        f"depth_mode={request.depth_mode}, living_only={request.living_only}"
    )

    try:
        service = RelativesNetworkService(session)
        result = service.find_relatives(request)

        logger.info(
            f"Relatives network result: total_count={result.total_count}, "
            f"depth={result.depth}, depth_mode={result.depth_mode}"
        )
        return result

    except HTTPException:
        # Re-raise HTTP exceptions (404 for person not found, 400 for invalid params)
        raise
    except Exception as e:
        logger.exception(
            f"Unexpected error in relatives network for user {current_user.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred while finding relatives",
        )

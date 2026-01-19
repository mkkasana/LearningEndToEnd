"""Partner Match API routes for finding potential marriage matches."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.schemas.partner_match import PartnerMatchRequest, PartnerMatchResponse
from app.services.partner_match import PartnerMatchService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/find", response_model=PartnerMatchResponse)
def find_partner_matches(
    session: SessionDep,
    current_user: CurrentUser,
    request: PartnerMatchRequest,
) -> Any:
    """
    Find potential partner matches for a seeker within their family network.

    Performs BFS traversal from the seeker through family relationships,
    applying cultural/religious compatibility filters, and returns a
    tree-structured graph showing all visited persons with eligible matches flagged.

    **Request Body:**
    - seeker_person_id: The person looking for matches (UUID)
    - target_gender_code: Gender code to search for ('MALE' or 'FEMALE')
    - birth_year_min: Minimum birth year filter (optional)
    - birth_year_max: Maximum birth year filter (optional)
    - include_religion_ids: Include only candidates with these religion IDs (optional)
    - include_category_ids: Include only candidates with these category IDs (optional)
    - include_sub_category_ids: Include only candidates with these sub-category IDs (optional)
    - exclude_sub_category_ids: Exclude candidates with these sub-category IDs/gotras (optional)
    - max_depth: Maximum BFS traversal depth (default: 5)

    **Returns:**
    - seeker_id: The seeker person ID from the request
    - total_matches: Total number of eligible matches found
    - matches: List of person IDs of eligible match candidates
    - exploration_graph: Graph of all visited persons keyed by person_id
    """
    logger.info(
        f"Partner match request from user {current_user.email}: "
        f"seeker={request.seeker_person_id}, target_gender={request.target_gender_code}, "
        f"max_depth={request.max_depth}"
    )

    try:
        service = PartnerMatchService(session)
        result = service.find_matches(request)

        logger.info(
            f"Partner match result: total_matches={result.total_matches}, "
            f"visited_nodes={len(result.exploration_graph)}"
        )
        return result

    except HTTPException:
        # Re-raise HTTP exceptions (404 for seeker not found, 400 for invalid params)
        raise
    except Exception as e:
        logger.exception(
            f"Unexpected error in partner match for user {current_user.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred while finding partner matches",
        )

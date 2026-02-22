"""Lineage Path API routes for finding relationship paths between persons."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.schemas.lineage_path import LineagePathRequest, LineagePathResponse
from app.services.lineage_path import LineagePathService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/find", response_model=LineagePathResponse)
def find_lineage_path(
    session: SessionDep,
    current_user: CurrentUser,
    request: LineagePathRequest,
) -> Any:
    """
    Find the lineage path between two persons.

    Uses Bidirectional BFS to find the shortest path through family relationships.
    Returns a graph structure with person nodes and their connections.

    **Request Body:**
    - person_a_id: First person's UUID
    - person_b_id: Second person's UUID

    **Returns:**
    - connection_found: Whether a connection was found
    - message: Result description
    - common_ancestor_id: Common ancestor person ID (if found)
    - graph: Dictionary of person nodes keyed by person_id
    - path_a_to_common: Person IDs from person A to common ancestor
    - path_b_to_common: Person IDs from person B to common ancestor
    """
    logger.info(
        f"Lineage path request from user {current_user.email}: "
        f"person_a={request.person_a_id}, person_b={request.person_b_id}"
    )

    try:
        service = LineagePathService(session)
        result = service.find_path(request.person_a_id, request.person_b_id)

        logger.info(
            f"Lineage path result: connection_found={result.connection_found}, "
            f"common_ancestor={result.common_ancestor_id}"
        )
        return result

    except HTTPException:
        # Re-raise HTTP exceptions (404 for person not found)
        raise
    except Exception as e:
        logger.exception(
            f"Unexpected error in lineage path for user {current_user.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred while finding the lineage path",
        )

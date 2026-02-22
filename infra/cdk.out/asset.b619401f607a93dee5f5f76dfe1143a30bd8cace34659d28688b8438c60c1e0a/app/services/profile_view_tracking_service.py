"""Service for profile view tracking business logic."""

import logging
import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.profile_view_tracking import ProfileViewTracking
from app.repositories.profile_view_tracking_repository import (
    ProfileViewTrackingRepository,
)

logger = logging.getLogger(__name__)


class ProfileViewTrackingService:
    """Service for profile view tracking business logic."""

    def __init__(self, session: Session):
        self.repo = ProfileViewTrackingRepository(session)
        self.session = session

    def record_view(
        self,
        viewer_person_id: uuid.UUID,
        viewed_person_id: uuid.UUID,
    ) -> None:
        """
        Record a profile view event.

        If a non-aggregated record exists for this viewer-viewed pair,
        increment the count. Otherwise, create a new record.

        Args:
            viewer_person_id: UUID of the person viewing the profile
            viewed_person_id: UUID of the person whose profile is being viewed
        """
        try:
            # Don't record self-views
            if viewer_person_id == viewed_person_id:
                logger.debug(f"Skipping self-view for person {viewer_person_id}")
                return

            # Check for existing non-aggregated record
            existing = self.repo.get_non_aggregated_view(
                viewer_person_id,
                viewed_person_id,
            )

            if existing:
                # Increment existing record
                existing.view_count += 1
                existing.last_viewed_at = datetime.utcnow()
                existing.updated_at = datetime.utcnow()
                self.repo.update(existing)
                logger.info(
                    f"Incremented view count to {existing.view_count} "
                    f"for person {viewed_person_id} by {viewer_person_id}"
                )
            else:
                # Create new record
                view_record = ProfileViewTracking(
                    viewer_person_id=viewer_person_id,
                    viewed_person_id=viewed_person_id,
                    view_count=1,
                    is_aggregated=False,
                )
                self.repo.create(view_record)
                logger.info(
                    f"Created new view record for person {viewed_person_id} "
                    f"by {viewer_person_id}"
                )

        except Exception as e:
            # Log error but don't fail the request
            logger.error(
                f"Error recording profile view: {e}",
                exc_info=True,
            )

    def get_total_views(self, person_id: uuid.UUID) -> int:
        """
        Get total view count for a person.

        Args:
            person_id: UUID of the person to get view count for

        Returns:
            Total view count (sum of all view_count values)
        """
        return self.repo.get_total_views_for_person(person_id)

    def get_total_views_bulk(
        self,
        person_ids: list[uuid.UUID],
    ) -> dict[uuid.UUID, int]:
        """
        Get total view counts for multiple persons.

        Args:
            person_ids: List of person UUIDs to get view counts for

        Returns:
            Dictionary mapping person_id to total_view_count
        """
        if not person_ids:
            return {}
        return self.repo.get_total_views_for_persons(person_ids)

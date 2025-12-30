"""Repository for profile view tracking data access."""

import uuid

from sqlmodel import Session, func, select

from app.db_models.profile_view_tracking import ProfileViewTracking
from app.repositories.base import BaseRepository


class ProfileViewTrackingRepository(BaseRepository[ProfileViewTracking]):
    """Repository for profile view tracking data access."""

    def __init__(self, session: Session):
        super().__init__(ProfileViewTracking, session)

    def get_non_aggregated_view(
        self,
        viewer_person_id: uuid.UUID,
        viewed_person_id: uuid.UUID,
    ) -> ProfileViewTracking | None:
        """Get existing non-aggregated view record for viewer-viewed pair.
        
        Args:
            viewer_person_id: UUID of the person who viewed the profile
            viewed_person_id: UUID of the person whose profile was viewed
            
        Returns:
            ProfileViewTracking record if found, None otherwise
        """
        statement = select(ProfileViewTracking).where(
            ProfileViewTracking.viewer_person_id == viewer_person_id,
            ProfileViewTracking.viewed_person_id == viewed_person_id,
            ProfileViewTracking.is_aggregated == False,  # noqa: E712
        )
        return self.session.exec(statement).first()

    def get_total_views_for_person(self, person_id: uuid.UUID) -> int:
        """Get total view count for a person (sum of all view_count).
        
        Args:
            person_id: UUID of the person whose views to count
            
        Returns:
            Total view count (sum of all view_count values)
        """
        statement = select(func.sum(ProfileViewTracking.view_count)).where(
            ProfileViewTracking.viewed_person_id == person_id
        )
        result = self.session.exec(statement).first()
        return result if result is not None else 0

    def get_total_views_for_persons(
        self,
        person_ids: list[uuid.UUID],
    ) -> dict[uuid.UUID, int]:
        """Get total view counts for multiple persons.
        
        Args:
            person_ids: List of person UUIDs to get view counts for
            
        Returns:
            Dictionary mapping person_id to total_view_count
        """
        if not person_ids:
            return {}

        statement = (
            select(
                ProfileViewTracking.viewed_person_id,
                func.sum(ProfileViewTracking.view_count).label("total_views"),
            )
            .where(ProfileViewTracking.viewed_person_id.in_(person_ids))
            .group_by(ProfileViewTracking.viewed_person_id)
        )

        results = self.session.exec(statement).all()
        return {person_id: int(total_views) for person_id, total_views in results}

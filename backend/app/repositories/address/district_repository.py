import logging
from uuid import UUID

from sqlmodel import Session, select

from app.db_models.address import District
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class DistrictRepository(BaseRepository[District]):
    """Repository for District data access"""

    def __init__(self, session: Session):
        super().__init__(District, session)

    def get_by_state(self, state_id: UUID) -> list[District]:
        """Get all active districts for a specific state, ordered by name"""
        logger.debug(f"Querying districts for state: {state_id}")
        statement = (
            select(District)
            .where(District.state_id == state_id)
            .where(District.is_active)
            .order_by(District.name)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} districts for state {state_id}")
        return results

    def get_by_code(self, code: str, state_id: UUID) -> District | None:
        """Get district by code within a specific state"""
        logger.debug(f"Querying district by code: {code}, state_id: {state_id}")
        statement = select(District).where(
            District.code == code, District.state_id == state_id
        )
        result = self.session.exec(statement).first()
        if result:
            logger.debug(f"District found: {result.name} (code: {code})")
        else:
            logger.debug(f"No district found with code: {code}")
        return result

    def count_by_state(self, state_id: UUID) -> int:
        """Count districts for a specific state"""
        from sqlmodel import func

        logger.debug(f"Counting districts for state: {state_id}")
        statement = (
            select(func.count())
            .select_from(District)
            .where(District.state_id == state_id)
        )
        count = self.session.exec(statement).one()
        logger.debug(f"State {state_id} has {count} districts")
        return count

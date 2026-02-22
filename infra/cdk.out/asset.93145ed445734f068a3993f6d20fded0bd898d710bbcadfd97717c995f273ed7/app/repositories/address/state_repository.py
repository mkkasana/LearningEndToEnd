import logging
from uuid import UUID

from sqlmodel import Session, select

from app.db_models.address import State
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class StateRepository(BaseRepository[State]):
    """Repository for State data access"""

    def __init__(self, session: Session):
        super().__init__(State, session)

    def get_by_country(self, country_id: UUID) -> list[State]:
        """Get all active states for a specific country, ordered by name"""
        logger.debug(f"Querying states for country: {country_id}")
        statement = (
            select(State)
            .where(State.country_id == country_id)
            .where(State.is_active)
            .order_by(State.name)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} states for country {country_id}")
        return results

    def get_by_code(self, code: str, country_id: UUID) -> State | None:
        """Get state by code within a specific country"""
        logger.debug(f"Querying state by code: {code}, country_id: {country_id}")
        statement = select(State).where(
            State.code == code, State.country_id == country_id
        )
        result = self.session.exec(statement).first()
        if result:
            logger.debug(f"State found: {result.name} (code: {code})")
        else:
            logger.debug(f"No state found with code: {code}")
        return result

    def count_by_country(self, country_id: UUID) -> int:
        """Count states for a specific country"""
        from sqlmodel import func

        logger.debug(f"Counting states for country: {country_id}")
        statement = (
            select(func.count())
            .select_from(State)
            .where(State.country_id == country_id)
        )
        count = self.session.exec(statement).one()
        logger.debug(f"Country {country_id} has {count} states")
        return count

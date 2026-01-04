"""Life Event repository."""

import logging
import uuid

from sqlmodel import Session, desc, func, select

from app.db_models.person.person_life_event import PersonLifeEvent
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class LifeEventRepository(BaseRepository[PersonLifeEvent]):
    """Repository for life event data access."""

    def __init__(self, session: Session):
        super().__init__(PersonLifeEvent, session)

    def get_by_person(
        self, person_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[PersonLifeEvent]:
        """Get all life events for a person, sorted by date descending.

        Sorting: year DESC, month DESC NULLS LAST, date DESC NULLS LAST
        """
        logger.debug(f"Querying life events for person: {person_id}")
        statement = (
            select(PersonLifeEvent)
            .where(PersonLifeEvent.person_id == person_id)
            .order_by(
                desc(PersonLifeEvent.event_year),
                desc(PersonLifeEvent.event_month).nulls_last(),
                desc(PersonLifeEvent.event_date).nulls_last(),
            )
            .offset(skip)
            .limit(limit)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} life events for person {person_id}")
        return results

    def count_by_person(self, person_id: uuid.UUID) -> int:
        """Count life events for a person."""
        logger.debug(f"Counting life events for person: {person_id}")
        statement = (
            select(func.count())
            .select_from(PersonLifeEvent)
            .where(PersonLifeEvent.person_id == person_id)
        )
        count = self.session.exec(statement).one()
        logger.debug(f"Found {count} life events for person {person_id}")
        return count

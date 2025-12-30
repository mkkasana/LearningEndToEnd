"""Person Profession repository."""

import logging
import uuid

from sqlmodel import Session, desc, select

from app.db_models.person.person_profession import PersonProfession
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PersonProfessionRepository(BaseRepository[PersonProfession]):
    """Repository for person profession data access."""

    def __init__(self, session: Session):
        super().__init__(PersonProfession, session)

    def get_by_person_id(self, person_id: uuid.UUID) -> list[PersonProfession]:
        """Get all professions for a person."""
        logger.debug(f"Querying professions for person: {person_id}")
        statement = (
            select(PersonProfession)
            .where(PersonProfession.person_id == person_id)
            .order_by(desc(PersonProfession.start_date))
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} professions for person {person_id}")
        return results

    def get_current_profession(self, person_id: uuid.UUID) -> PersonProfession | None:
        """Get current profession for a person."""
        logger.debug(f"Querying current profession for person: {person_id}")
        statement = select(PersonProfession).where(
            PersonProfession.person_id == person_id, PersonProfession.is_current
        )
        result = self.session.exec(statement).first()
        if result:
            logger.debug(
                f"Current profession found for person {person_id} (ID: {result.id})"
            )
        else:
            logger.debug(f"No current profession found for person {person_id}")
        return result

    def clear_current_professions(self, person_id: uuid.UUID) -> None:
        """Clear is_current flag for all professions of a person."""
        logger.debug(f"Clearing current professions for person: {person_id}")
        statement = select(PersonProfession).where(
            PersonProfession.person_id == person_id
        )
        professions = self.session.exec(statement).all()
        count = 0
        for profession in professions:
            profession.is_current = False
            self.session.add(profession)
            count += 1
        self.session.commit()
        logger.debug(f"Cleared {count} current professions for person {person_id}")

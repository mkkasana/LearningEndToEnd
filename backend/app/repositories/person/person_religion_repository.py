"""Person Religion repository."""

import logging
import uuid

from sqlmodel import Session, select

from app.db_models.person.person_religion import PersonReligion
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PersonReligionRepository(BaseRepository[PersonReligion]):
    """Repository for person religion data access."""

    def __init__(self, session: Session):
        super().__init__(PersonReligion, session)

    def get_by_person_id(self, person_id: uuid.UUID) -> PersonReligion | None:
        """Get religion for a person."""
        logger.debug(f"Querying religion for person: {person_id}")
        statement = select(PersonReligion).where(PersonReligion.person_id == person_id)
        result = self.session.exec(statement).first()
        if result:
            logger.debug(f"Religion found for person {person_id} (ID: {result.id})")
        else:
            logger.debug(f"No religion found for person {person_id}")
        return result

    def person_has_religion(self, person_id: uuid.UUID) -> bool:
        """Check if person has religion record."""
        logger.debug(f"Checking if person has religion: {person_id}")
        has_religion = self.get_by_person_id(person_id) is not None
        logger.debug(f"Person {person_id} has religion: {has_religion}")
        return has_religion

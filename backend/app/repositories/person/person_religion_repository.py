"""Person Religion repository."""

import uuid

from sqlmodel import Session, select

from app.db_models.person.person_religion import PersonReligion
from app.repositories.base import BaseRepository


class PersonReligionRepository(BaseRepository[PersonReligion]):
    """Repository for person religion data access."""

    def __init__(self, session: Session):
        super().__init__(PersonReligion, session)

    def get_by_person_id(self, person_id: uuid.UUID) -> PersonReligion | None:
        """Get religion for a person."""
        statement = select(PersonReligion).where(PersonReligion.person_id == person_id)
        return self.session.exec(statement).first()

    def person_has_religion(self, person_id: uuid.UUID) -> bool:
        """Check if person has religion record."""
        return self.get_by_person_id(person_id) is not None

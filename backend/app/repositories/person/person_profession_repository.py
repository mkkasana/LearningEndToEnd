"""Person Profession repository."""

import uuid

from sqlmodel import Session, select

from app.db_models.person.person_profession import PersonProfession
from app.repositories.base import BaseRepository


class PersonProfessionRepository(BaseRepository[PersonProfession]):
    """Repository for person profession data access."""

    def __init__(self, session: Session):
        super().__init__(PersonProfession, session)

    def get_by_person_id(self, person_id: uuid.UUID) -> list[PersonProfession]:
        """Get all professions for a person."""
        statement = (
            select(PersonProfession)
            .where(PersonProfession.person_id == person_id)
            .order_by(PersonProfession.start_date.desc())
        )
        return list(self.session.exec(statement).all())

    def get_current_profession(self, person_id: uuid.UUID) -> PersonProfession | None:
        """Get current profession for a person."""
        statement = select(PersonProfession).where(
            PersonProfession.person_id == person_id, PersonProfession.is_current == True
        )
        return self.session.exec(statement).first()

    def clear_current_professions(self, person_id: uuid.UUID) -> None:
        """Clear is_current flag for all professions of a person."""
        statement = select(PersonProfession).where(
            PersonProfession.person_id == person_id
        )
        professions = self.session.exec(statement).all()
        for profession in professions:
            profession.is_current = False
            self.session.add(profession)
        self.session.commit()

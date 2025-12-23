"""Person repository."""

import uuid

from sqlmodel import Session, select

from app.db_models.person.person import Person
from app.repositories.base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    """Repository for person data access."""

    def __init__(self, session: Session):
        super().__init__(Person, session)

    def get_by_user_id(self, user_id: uuid.UUID) -> Person | None:
        """Get person by user ID."""
        statement = select(Person).where(Person.user_id == user_id)
        return self.session.exec(statement).first()

    def user_has_person(self, user_id: uuid.UUID) -> bool:
        """Check if user already has a person record."""
        return self.get_by_user_id(user_id) is not None

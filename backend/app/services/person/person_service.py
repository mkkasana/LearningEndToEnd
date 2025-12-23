"""Person service."""

import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person import Person
from app.repositories.person.person_repository import PersonRepository
from app.schemas.person import PersonCreate, PersonPublic, PersonUpdate


class PersonService:
    """Service for person business logic."""

    def __init__(self, session: Session):
        self.person_repo = PersonRepository(session)

    def get_person_by_user_id(self, user_id: uuid.UUID) -> Person | None:
        """Get person by user ID."""
        return self.person_repo.get_by_user_id(user_id)

    def create_person(self, person_create: PersonCreate) -> Person:
        """Create a new person."""
        person = Person(**person_create.model_dump())
        return self.person_repo.create(person)

    def update_person(self, person: Person, person_update: PersonUpdate) -> Person:
        """Update a person."""
        update_data = person_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(person, key, value)
        person.updated_at = datetime.utcnow()
        return self.person_repo.update(person)

    def delete_person(self, person: Person) -> None:
        """Delete a person."""
        self.person_repo.delete(person)

    def user_has_person(self, user_id: uuid.UUID) -> bool:
        """Check if user already has a person record."""
        return self.person_repo.user_has_person(user_id)

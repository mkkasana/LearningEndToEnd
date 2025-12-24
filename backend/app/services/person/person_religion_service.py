"""Person Religion service."""

import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person_religion import PersonReligion
from app.repositories.person.person_religion_repository import PersonReligionRepository
from app.schemas.person.person_religion import (
    PersonReligionCreate,
    PersonReligionUpdate,
)


class PersonReligionService:
    """Service for person religion business logic."""

    def __init__(self, session: Session):
        self.person_religion_repo = PersonReligionRepository(session)

    def get_by_person_id(self, person_id: uuid.UUID) -> PersonReligion | None:
        """Get religion for a person."""
        return self.person_religion_repo.get_by_person_id(person_id)

    def create_person_religion(
        self, person_id: uuid.UUID, religion_create: PersonReligionCreate
    ) -> PersonReligion:
        """Create person religion."""
        person_religion = PersonReligion(
            person_id=person_id, **religion_create.model_dump()
        )
        return self.person_religion_repo.create(person_religion)

    def update_person_religion(
        self, person_religion: PersonReligion, religion_update: PersonReligionUpdate
    ) -> PersonReligion:
        """Update person religion."""
        update_data = religion_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(person_religion, key, value)
        person_religion.updated_at = datetime.utcnow()
        return self.person_religion_repo.update(person_religion)

    def delete_person_religion(self, person_religion: PersonReligion) -> None:
        """Delete person religion."""
        self.person_religion_repo.delete(person_religion)

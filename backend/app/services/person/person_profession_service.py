"""Person Profession service."""

import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person_profession import PersonProfession
from app.repositories.person.person_profession_repository import (
    PersonProfessionRepository,
)
from app.schemas.person import PersonProfessionCreate, PersonProfessionUpdate


class PersonProfessionService:
    """Service for person profession business logic."""

    def __init__(self, session: Session):
        self.profession_repo = PersonProfessionRepository(session)

    def get_professions_by_person(self, person_id: uuid.UUID) -> list[PersonProfession]:
        """Get all professions for a person."""
        return self.profession_repo.get_by_person_id(person_id)

    def get_profession_by_id(self, profession_id: uuid.UUID) -> PersonProfession | None:
        """Get profession by ID."""
        return self.profession_repo.get_by_id(profession_id)

    def create_profession(
        self, person_id: uuid.UUID, profession_create: PersonProfessionCreate
    ) -> PersonProfession:
        """Create a new profession for a person."""
        # If marking as current, clear other current professions
        if profession_create.is_current:
            self.profession_repo.clear_current_professions(person_id)

        profession = PersonProfession(
            person_id=person_id, **profession_create.model_dump()
        )
        return self.profession_repo.create(profession)

    def update_profession(
        self, profession: PersonProfession, profession_update: PersonProfessionUpdate
    ) -> PersonProfession:
        """Update a profession."""
        update_data = profession_update.model_dump(exclude_unset=True)

        # If marking as current, clear other current professions
        if update_data.get("is_current"):
            self.profession_repo.clear_current_professions(profession.person_id)

        for key, value in update_data.items():
            setattr(profession, key, value)
        profession.updated_at = datetime.utcnow()
        return self.profession_repo.update(profession)

    def delete_profession(self, profession: PersonProfession) -> None:
        """Delete a profession."""
        self.profession_repo.delete(profession)

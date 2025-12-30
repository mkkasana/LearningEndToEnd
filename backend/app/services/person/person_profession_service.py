"""Person Profession service."""

import logging
import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person_profession import PersonProfession
from app.repositories.person.person_profession_repository import (
    PersonProfessionRepository,
)
from app.schemas.person import PersonProfessionCreate, PersonProfessionUpdate

logger = logging.getLogger(__name__)


class PersonProfessionService:
    """Service for person profession business logic."""

    def __init__(self, session: Session):
        self.profession_repo = PersonProfessionRepository(session)

    def get_professions_by_person(self, person_id: uuid.UUID) -> list[PersonProfession]:
        """Get all professions for a person."""
        logger.debug(f"Fetching professions for person ID: {person_id}")
        professions = self.profession_repo.get_by_person_id(person_id)
        logger.debug(f"Found {len(professions)} profession(s) for person {person_id}")
        return professions

    def get_profession_by_id(self, profession_id: uuid.UUID) -> PersonProfession | None:
        """Get profession by ID."""
        logger.debug(f"Fetching profession by ID: {profession_id}")
        profession = self.profession_repo.get_by_id(profession_id)
        if profession:
            logger.debug(f"Profession found: ID {profession_id}")
        else:
            logger.debug(f"Profession not found: ID {profession_id}")
        return profession

    def create_profession(
        self, person_id: uuid.UUID, profession_create: PersonProfessionCreate
    ) -> PersonProfession:
        """Create a new profession for a person."""
        logger.info(
            f"Creating profession for person ID: {person_id}, is_current={profession_create.is_current}"
        )

        # If marking as current, clear other current professions
        if profession_create.is_current:
            logger.debug(f"Clearing other current professions for person {person_id}")
            self.profession_repo.clear_current_professions(person_id)

        profession = PersonProfession(
            person_id=person_id, **profession_create.model_dump()
        )
        created_profession = self.profession_repo.create(profession)
        logger.info(
            f"Profession created successfully: ID {created_profession.id} for person {person_id}"
        )
        return created_profession

    def update_profession(
        self, profession: PersonProfession, profession_update: PersonProfessionUpdate
    ) -> PersonProfession:
        """Update a profession."""
        logger.info(
            f"Updating profession: ID {profession.id} for person {profession.person_id}"
        )
        update_data = profession_update.model_dump(exclude_unset=True)

        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(
                f"Updating fields for profession {profession.id}: {update_fields}"
            )

        # If marking as current, clear other current professions
        if update_data.get("is_current"):
            logger.debug(
                f"Clearing other current professions for person {profession.person_id}"
            )
            self.profession_repo.clear_current_professions(profession.person_id)

        for key, value in update_data.items():
            setattr(profession, key, value)
        profession.updated_at = datetime.utcnow()
        updated_profession = self.profession_repo.update(profession)
        logger.info(f"Profession updated successfully: ID {updated_profession.id}")
        return updated_profession

    def delete_profession(self, profession: PersonProfession) -> None:
        """Delete a profession."""
        logger.warning(
            f"Deleting profession: ID {profession.id} for person {profession.person_id}"
        )
        self.profession_repo.delete(profession)
        logger.info(f"Profession deleted successfully: ID {profession.id}")

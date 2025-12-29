"""Person service."""

import logging
import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person import Person
from app.repositories.person.person_repository import PersonRepository
from app.schemas.person import PersonCreate, PersonUpdate

logger = logging.getLogger(__name__)


class PersonService:
    """Service for person business logic."""

    def __init__(self, session: Session):
        self.person_repo = PersonRepository(session)

    def get_person_by_user_id(self, user_id: uuid.UUID) -> Person | None:
        """Get person by user ID."""
        logger.debug(f"Fetching person for user ID: {user_id}")
        person = self.person_repo.get_by_user_id(user_id)
        if person:
            logger.debug(
                f"Person found: {person.first_name} {person.last_name} "
                f"(Person ID: {person.id}, User ID: {user_id})"
            )
        else:
            logger.debug(f"No person found for user ID: {user_id}")
        return person

    def create_person(self, person_create: PersonCreate) -> Person:
        """Create a new person."""
        logger.info(
            f"Creating person: {person_create.first_name} {person_create.last_name}, "
            f"gender_id={person_create.gender_id}, user_id={person_create.user_id}"
        )
        person = Person(**person_create.model_dump())
        created_person = self.person_repo.create(person)
        logger.info(
            f"Person created successfully: {created_person.first_name} {created_person.last_name} "
            f"(ID: {created_person.id}), is_primary={created_person.is_primary}"
        )
        return created_person

    def update_person(self, person: Person, person_update: PersonUpdate) -> Person:
        """Update a person."""
        logger.info(
            f"Updating person: {person.first_name} {person.last_name} (ID: {person.id})"
        )
        update_data = person_update.model_dump(exclude_unset=True)

        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(f"Updating fields for person {person.id}: {update_fields}")

        for key, value in update_data.items():
            setattr(person, key, value)
        person.updated_at = datetime.utcnow()

        updated_person = self.person_repo.update(person)
        logger.info(
            f"Person updated successfully: {updated_person.first_name} {updated_person.last_name} "
            f"(ID: {updated_person.id})"
        )
        return updated_person

    def delete_person(self, person: Person) -> None:
        """Delete a person."""
        logger.warning(
            f"Deleting person: {person.first_name} {person.last_name} (ID: {person.id})"
        )
        self.person_repo.delete(person)
        logger.info(
            f"Person deleted successfully: {person.first_name} {person.last_name} (ID: {person.id})"
        )

    def user_has_person(self, user_id: uuid.UUID) -> bool:
        """Check if user already has a person record."""
        logger.debug(f"Checking if user has person record: user_id={user_id}")
        has_person = self.person_repo.user_has_person(user_id)
        logger.debug(f"User {user_id} has person: {has_person}")
        return has_person

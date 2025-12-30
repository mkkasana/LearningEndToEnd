"""Person repository."""

import logging
import uuid

from sqlmodel import Session, select

from app.db_models.person.person import Person
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PersonRepository(BaseRepository[Person]):
    """Repository for person data access."""

    def __init__(self, session: Session):
        super().__init__(Person, session)

    def get_by_user_id(self, user_id: uuid.UUID) -> Person | None:
        """Get person by user ID."""
        logger.debug(f"Querying person by user_id: {user_id}")
        statement = select(Person).where(Person.user_id == user_id)
        result = self.session.exec(statement).first()
        if result:
            logger.debug(
                f"Person found for user_id {user_id}: {result.first_name} {result.last_name} (ID: {result.id})"
            )
        else:
            logger.debug(f"No person found for user_id: {user_id}")
        return result

    def user_has_person(self, user_id: uuid.UUID) -> bool:
        """Check if user already has a person record."""
        logger.debug(f"Checking if user has person record: {user_id}")
        has_person = self.get_by_user_id(user_id) is not None
        logger.debug(f"User {user_id} has person record: {has_person}")
        return has_person

    def get_by_creator(self, creator_user_id: uuid.UUID) -> list[Person]:
        """Get all persons created by a specific user."""
        logger.debug(f"Querying persons by creator_user_id: {creator_user_id}")
        statement = select(Person).where(Person.created_by_user_id == creator_user_id)
        results = list(self.session.exec(statement).all())
        logger.debug(f"Found {len(results)} persons created by user {creator_user_id}")
        return results

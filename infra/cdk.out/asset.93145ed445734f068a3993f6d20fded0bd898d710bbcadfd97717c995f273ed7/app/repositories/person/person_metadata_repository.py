"""Person Metadata repository."""

import logging
import uuid

from sqlmodel import Session, select

from app.db_models.person.person_metadata import PersonMetadata
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PersonMetadataRepository(BaseRepository[PersonMetadata]):
    """Repository for person metadata data access."""

    def __init__(self, session: Session):
        super().__init__(PersonMetadata, session)

    def get_by_person_id(self, person_id: uuid.UUID) -> PersonMetadata | None:
        """Get metadata for a person."""
        logger.debug(f"Querying metadata for person: {person_id}")
        statement = select(PersonMetadata).where(PersonMetadata.person_id == person_id)
        result = self.session.exec(statement).first()
        if result:
            logger.debug(f"Metadata found for person {person_id} (ID: {result.id})")
        else:
            logger.debug(f"No metadata found for person {person_id}")
        return result

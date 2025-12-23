"""Person Metadata repository."""

import uuid

from sqlmodel import Session, select

from app.db_models.person.person_metadata import PersonMetadata
from app.repositories.base import BaseRepository


class PersonMetadataRepository(BaseRepository[PersonMetadata]):
    """Repository for person metadata data access."""

    def __init__(self, session: Session):
        super().__init__(PersonMetadata, session)

    def get_by_person_id(self, person_id: uuid.UUID) -> PersonMetadata | None:
        """Get metadata for a person."""
        statement = select(PersonMetadata).where(PersonMetadata.person_id == person_id)
        return self.session.exec(statement).first()

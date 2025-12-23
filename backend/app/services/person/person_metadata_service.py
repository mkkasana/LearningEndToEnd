"""Person Metadata service."""

import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person_metadata import PersonMetadata
from app.repositories.person.person_metadata_repository import PersonMetadataRepository
from app.schemas.person import PersonMetadataCreate, PersonMetadataUpdate


class PersonMetadataService:
    """Service for person metadata business logic."""

    def __init__(self, session: Session):
        self.metadata_repo = PersonMetadataRepository(session)

    def get_metadata_by_person(self, person_id: uuid.UUID) -> PersonMetadata | None:
        """Get metadata for a person."""
        return self.metadata_repo.get_by_person_id(person_id)

    def create_metadata(
        self, person_id: uuid.UUID, metadata_create: PersonMetadataCreate
    ) -> PersonMetadata:
        """Create metadata for a person."""
        metadata = PersonMetadata(person_id=person_id, **metadata_create.model_dump())
        return self.metadata_repo.create(metadata)

    def update_metadata(
        self, metadata: PersonMetadata, metadata_update: PersonMetadataUpdate
    ) -> PersonMetadata:
        """Update person metadata."""
        update_data = metadata_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(metadata, key, value)
        metadata.updated_at = datetime.utcnow()
        return self.metadata_repo.update(metadata)

    def delete_metadata(self, metadata: PersonMetadata) -> None:
        """Delete person metadata."""
        self.metadata_repo.delete(metadata)

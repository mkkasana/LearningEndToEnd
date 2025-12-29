"""Person Metadata service."""

import logging
import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person_metadata import PersonMetadata
from app.repositories.person.person_metadata_repository import PersonMetadataRepository
from app.schemas.person import PersonMetadataCreate, PersonMetadataUpdate

logger = logging.getLogger(__name__)


class PersonMetadataService:
    """Service for person metadata business logic."""

    def __init__(self, session: Session):
        self.metadata_repo = PersonMetadataRepository(session)

    def get_metadata_by_person(self, person_id: uuid.UUID) -> PersonMetadata | None:
        """Get metadata for a person."""
        logger.debug(f"Fetching metadata for person ID: {person_id}")
        metadata = self.metadata_repo.get_by_person_id(person_id)
        if metadata:
            logger.debug(f"Metadata found for person {person_id}")
        else:
            logger.debug(f"Metadata not found for person {person_id}")
        return metadata

    def create_metadata(
        self, person_id: uuid.UUID, metadata_create: PersonMetadataCreate
    ) -> PersonMetadata:
        """Create metadata for a person."""
        logger.info(f"Creating metadata for person ID: {person_id}")
        metadata = PersonMetadata(person_id=person_id, **metadata_create.model_dump())
        created_metadata = self.metadata_repo.create(metadata)
        logger.info(f"Metadata created successfully: ID {created_metadata.id} for person {person_id}")
        return created_metadata

    def update_metadata(
        self, metadata: PersonMetadata, metadata_update: PersonMetadataUpdate
    ) -> PersonMetadata:
        """Update person metadata."""
        logger.info(f"Updating metadata: ID {metadata.id} for person {metadata.person_id}")
        update_data = metadata_update.model_dump(exclude_unset=True)
        
        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(f"Updating fields for metadata {metadata.id}: {update_fields}")
        
        for key, value in update_data.items():
            setattr(metadata, key, value)
        metadata.updated_at = datetime.utcnow()
        updated_metadata = self.metadata_repo.update(metadata)
        logger.info(f"Metadata updated successfully: ID {updated_metadata.id}")
        return updated_metadata

    def delete_metadata(self, metadata: PersonMetadata) -> None:
        """Delete person metadata."""
        logger.warning(f"Deleting metadata: ID {metadata.id} for person {metadata.person_id}")
        self.metadata_repo.delete(metadata)
        logger.info(f"Metadata deleted successfully: ID {metadata.id}")

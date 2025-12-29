"""Religion service."""

import logging
import uuid

from sqlmodel import Session

from app.db_models.religion.religion import Religion
from app.repositories.religion.religion_repository import ReligionRepository
from app.schemas.religion import ReligionCreate, ReligionPublic, ReligionUpdate

logger = logging.getLogger(__name__)


class ReligionService:
    """Service for religion business logic."""

    def __init__(self, session: Session):
        self.religion_repo = ReligionRepository(session)

    def get_religions(self) -> list[ReligionPublic]:
        """Get all active religions."""
        logger.debug("Fetching all active religions")
        religions = self.religion_repo.get_active_religions()
        logger.debug(f"Found {len(religions)} active religions")
        return [ReligionPublic(religionId=r.id, religionName=r.name) for r in religions]

    def get_religion_by_id(self, religion_id: uuid.UUID) -> Religion | None:
        """Get religion by ID."""
        logger.debug(f"Fetching religion by ID: {religion_id}")
        religion = self.religion_repo.get_by_id(religion_id)
        if religion:
            logger.debug(f"Religion found: {religion.name} (ID: {religion_id})")
        else:
            logger.debug(f"Religion not found: ID {religion_id}")
        return religion

    def create_religion(self, religion_create: ReligionCreate) -> Religion:
        """Create a new religion."""
        logger.info(f"Creating religion: {religion_create.name} (code: {religion_create.code})")
        religion = Religion(**religion_create.model_dump())
        religion.code = religion.code.upper()
        created_religion = self.religion_repo.create(religion)
        logger.info(f"Religion created successfully: {created_religion.name} (ID: {created_religion.id})")
        return created_religion

    def update_religion(
        self, religion: Religion, religion_update: ReligionUpdate
    ) -> Religion:
        """Update a religion."""
        logger.info(f"Updating religion: {religion.name} (ID: {religion.id})")
        update_data = religion_update.model_dump(exclude_unset=True)
        
        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(f"Updating fields for religion {religion.id}: {update_fields}")
        
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()
        for key, value in update_data.items():
            setattr(religion, key, value)
        updated_religion = self.religion_repo.update(religion)
        logger.info(f"Religion updated successfully: {updated_religion.name} (ID: {updated_religion.id})")
        return updated_religion

    def delete_religion(self, religion: Religion) -> None:
        """Delete a religion."""
        logger.warning(f"Deleting religion: {religion.name} (ID: {religion.id})")
        self.religion_repo.delete(religion)
        logger.info(f"Religion deleted successfully: {religion.name} (ID: {religion.id})")

    def code_exists(
        self, code: str, exclude_religion_id: uuid.UUID | None = None
    ) -> bool:
        """Check if religion code exists."""
        logger.debug(f"Checking if religion code exists: {code}")
        exists = self.religion_repo.code_exists(code, exclude_religion_id)
        if exists:
            logger.debug(f"Religion code already exists: {code}")
        else:
            logger.debug(f"Religion code does not exist: {code}")
        return exists

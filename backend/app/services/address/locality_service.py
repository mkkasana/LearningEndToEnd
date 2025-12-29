import logging
from uuid import UUID

from sqlmodel import Session

from app.db_models.address import Locality
from app.repositories.address import LocalityRepository
from app.schemas.address.locality import (
    LocalityCreate,
    LocalityPublic,
    LocalityUpdate,
)

logger = logging.getLogger(__name__)


class LocalityService:
    """Service for locality metadata operations"""

    def __init__(self, session: Session):
        self.session = session
        self.locality_repo = LocalityRepository(session)

    def get_localities_by_sub_district(
        self, sub_district_id: UUID
    ) -> list[LocalityPublic]:
        """Get all active localities for a sub-district formatted for API response"""
        logger.debug(f"Fetching localities for sub-district ID: {sub_district_id}")
        localities = self.locality_repo.get_by_sub_district(sub_district_id)
        logger.debug(f"Found {len(localities)} localities for sub-district {sub_district_id}")
        return [
            LocalityPublic(localityId=locality.id, localityName=locality.name)
            for locality in localities
        ]

    def get_locality_by_id(self, locality_id: UUID) -> Locality | None:
        """Get locality by ID"""
        logger.debug(f"Fetching locality by ID: {locality_id}")
        locality = self.locality_repo.get_by_id(locality_id)
        if locality:
            logger.debug(f"Locality found: {locality.name} (ID: {locality_id})")
        else:
            logger.debug(f"Locality not found: ID {locality_id}")
        return locality

    def create_locality(self, locality_in: LocalityCreate) -> Locality:
        """Create a new locality"""
        logger.info(f"Creating locality: {locality_in.name} for sub-district {locality_in.sub_district_id}")
        locality = Locality(
            name=locality_in.name,
            code=locality_in.code.upper() if locality_in.code else None,
            sub_district_id=locality_in.sub_district_id,
            is_active=locality_in.is_active,
        )
        created_locality = self.locality_repo.create(locality)
        logger.info(f"Locality created successfully: {created_locality.name} (ID: {created_locality.id})")
        return created_locality

    def update_locality(
        self, locality: Locality, locality_update: LocalityUpdate
    ) -> Locality:
        """Update locality information"""
        logger.info(f"Updating locality: {locality.name} (ID: {locality.id})")
        update_data = locality_update.model_dump(exclude_unset=True)
        
        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(f"Updating fields for locality {locality.id}: {update_fields}")

        # Ensure code is uppercase if provided
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()

        locality.sqlmodel_update(update_data)
        updated_locality = self.locality_repo.update(locality)
        logger.info(f"Locality updated successfully: {updated_locality.name} (ID: {updated_locality.id})")
        return updated_locality

    def code_exists(
        self,
        code: str,
        sub_district_id: UUID,
        exclude_locality_id: UUID | None = None,
    ) -> bool:
        """Check if locality code exists within a sub-district, optionally excluding a specific locality"""
        if not code:
            return False
        logger.debug(f"Checking if locality code exists: {code} in sub-district {sub_district_id}")
        existing_locality = self.locality_repo.get_by_code(
            code.upper(), sub_district_id
        )
        if not existing_locality:
            logger.debug(f"Locality code does not exist: {code}")
            return False
        if exclude_locality_id and existing_locality.id == exclude_locality_id:
            logger.debug(f"Locality code exists but excluded from check: {code}")
            return False
        logger.debug(f"Locality code already exists: {code}")
        return True

    def delete_locality(self, locality: Locality) -> None:
        """Delete a locality"""
        logger.warning(f"Deleting locality: {locality.name} (ID: {locality.id})")
        self.locality_repo.delete(locality)
        logger.info(f"Locality deleted successfully: {locality.name} (ID: {locality.id})")

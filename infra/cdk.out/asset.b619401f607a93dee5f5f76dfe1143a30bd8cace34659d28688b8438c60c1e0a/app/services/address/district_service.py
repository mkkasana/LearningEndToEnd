import logging
from uuid import UUID

from sqlmodel import Session

from app.db_models.address import District
from app.repositories.address import DistrictRepository
from app.schemas.address.district import DistrictCreate, DistrictPublic, DistrictUpdate

logger = logging.getLogger(__name__)


class DistrictService:
    """Service for district metadata operations"""

    def __init__(self, session: Session):
        self.session = session
        self.district_repo = DistrictRepository(session)

    def get_districts_by_state(self, state_id: UUID) -> list[DistrictPublic]:
        """Get all active districts for a state formatted for API response"""
        logger.debug(f"Fetching districts for state ID: {state_id}")
        districts = self.district_repo.get_by_state(state_id)
        logger.debug(f"Found {len(districts)} districts for state {state_id}")
        return [
            DistrictPublic(districtId=district.id, districtName=district.name)
            for district in districts
        ]

    def get_district_by_id(self, district_id: UUID) -> District | None:
        """Get district by ID"""
        logger.debug(f"Fetching district by ID: {district_id}")
        district = self.district_repo.get_by_id(district_id)
        if district:
            logger.debug(f"District found: {district.name} (ID: {district_id})")
        else:
            logger.debug(f"District not found: ID {district_id}")
        return district

    def create_district(self, district_in: DistrictCreate) -> District:
        """Create a new district"""
        logger.info(
            f"Creating district: {district_in.name} for state {district_in.state_id}"
        )
        district = District(
            name=district_in.name,
            code=district_in.code.upper() if district_in.code else None,
            state_id=district_in.state_id,
            is_active=district_in.is_active,
        )
        created_district = self.district_repo.create(district)
        logger.info(
            f"District created successfully: {created_district.name} (ID: {created_district.id})"
        )
        return created_district

    def update_district(
        self, district: District, district_update: DistrictUpdate
    ) -> District:
        """Update district information"""
        logger.info(f"Updating district: {district.name} (ID: {district.id})")
        update_data = district_update.model_dump(exclude_unset=True)

        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(f"Updating fields for district {district.id}: {update_fields}")

        # Ensure code is uppercase if provided
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()

        district.sqlmodel_update(update_data)
        updated_district = self.district_repo.update(district)
        logger.info(
            f"District updated successfully: {updated_district.name} (ID: {updated_district.id})"
        )
        return updated_district

    def code_exists(
        self, code: str, state_id: UUID, exclude_district_id: UUID | None = None
    ) -> bool:
        """Check if district code exists within a state, optionally excluding a specific district"""
        if not code:
            return False
        logger.debug(f"Checking if district code exists: {code} in state {state_id}")
        existing_district = self.district_repo.get_by_code(code.upper(), state_id)
        if not existing_district:
            logger.debug(f"District code does not exist: {code}")
            return False
        if exclude_district_id and existing_district.id == exclude_district_id:
            logger.debug(f"District code exists but excluded from check: {code}")
            return False
        logger.debug(f"District code already exists: {code}")
        return True

    def delete_district(self, district: District) -> None:
        """Delete a district"""
        logger.warning(f"Deleting district: {district.name} (ID: {district.id})")
        self.district_repo.delete(district)
        logger.info(
            f"District deleted successfully: {district.name} (ID: {district.id})"
        )

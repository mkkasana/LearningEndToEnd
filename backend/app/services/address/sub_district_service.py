import logging
from uuid import UUID

from sqlmodel import Session

from app.db_models.address import SubDistrict
from app.repositories.address import SubDistrictRepository
from app.schemas.address.sub_district import (
    SubDistrictCreate,
    SubDistrictPublic,
    SubDistrictUpdate,
)

logger = logging.getLogger(__name__)


class SubDistrictService:
    """Service for sub-district metadata operations"""

    def __init__(self, session: Session):
        self.session = session
        self.sub_district_repo = SubDistrictRepository(session)

    def get_sub_districts_by_district(
        self, district_id: UUID
    ) -> list[SubDistrictPublic]:
        """Get all active sub-districts for a district formatted for API response"""
        logger.debug(f"Fetching sub-districts for district ID: {district_id}")
        sub_districts = self.sub_district_repo.get_by_district(district_id)
        logger.debug(
            f"Found {len(sub_districts)} sub-districts for district {district_id}"
        )
        return [
            SubDistrictPublic(tehsilId=sub_district.id, tehsilName=sub_district.name)
            for sub_district in sub_districts
        ]

    def get_sub_district_by_id(self, sub_district_id: UUID) -> SubDistrict | None:
        """Get sub-district by ID"""
        logger.debug(f"Fetching sub-district by ID: {sub_district_id}")
        sub_district = self.sub_district_repo.get_by_id(sub_district_id)
        if sub_district:
            logger.debug(
                f"Sub-district found: {sub_district.name} (ID: {sub_district_id})"
            )
        else:
            logger.debug(f"Sub-district not found: ID {sub_district_id}")
        return sub_district

    def create_sub_district(self, sub_district_in: SubDistrictCreate) -> SubDistrict:
        """Create a new sub-district"""
        logger.info(
            f"Creating sub-district: {sub_district_in.name} for district {sub_district_in.district_id}"
        )
        sub_district = SubDistrict(
            name=sub_district_in.name,
            code=sub_district_in.code.upper() if sub_district_in.code else None,
            district_id=sub_district_in.district_id,
            is_active=sub_district_in.is_active,
        )
        created_sub_district = self.sub_district_repo.create(sub_district)
        logger.info(
            f"Sub-district created successfully: {created_sub_district.name} (ID: {created_sub_district.id})"
        )
        return created_sub_district

    def update_sub_district(
        self, sub_district: SubDistrict, sub_district_update: SubDistrictUpdate
    ) -> SubDistrict:
        """Update sub-district information"""
        logger.info(
            f"Updating sub-district: {sub_district.name} (ID: {sub_district.id})"
        )
        update_data = sub_district_update.model_dump(exclude_unset=True)

        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(
                f"Updating fields for sub-district {sub_district.id}: {update_fields}"
            )

        # Ensure code is uppercase if provided
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()

        sub_district.sqlmodel_update(update_data)
        updated_sub_district = self.sub_district_repo.update(sub_district)
        logger.info(
            f"Sub-district updated successfully: {updated_sub_district.name} (ID: {updated_sub_district.id})"
        )
        return updated_sub_district

    def code_exists(
        self,
        code: str,
        district_id: UUID,
        exclude_sub_district_id: UUID | None = None,
    ) -> bool:
        """Check if sub-district code exists within a district, optionally excluding a specific sub-district"""
        if not code:
            return False
        logger.debug(
            f"Checking if sub-district code exists: {code} in district {district_id}"
        )
        existing_sub_district = self.sub_district_repo.get_by_code(
            code.upper(), district_id
        )
        if not existing_sub_district:
            logger.debug(f"Sub-district code does not exist: {code}")
            return False
        if (
            exclude_sub_district_id
            and existing_sub_district.id == exclude_sub_district_id
        ):
            logger.debug(f"Sub-district code exists but excluded from check: {code}")
            return False
        logger.debug(f"Sub-district code already exists: {code}")
        return True

    def delete_sub_district(self, sub_district: SubDistrict) -> None:
        """Delete a sub-district"""
        logger.warning(
            f"Deleting sub-district: {sub_district.name} (ID: {sub_district.id})"
        )
        self.sub_district_repo.delete(sub_district)
        logger.info(
            f"Sub-district deleted successfully: {sub_district.name} (ID: {sub_district.id})"
        )

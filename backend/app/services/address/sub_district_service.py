from uuid import UUID

from sqlmodel import Session

from app.db_models.address import SubDistrict
from app.repositories.address import SubDistrictRepository
from app.schemas.address.sub_district import (
    SubDistrictCreate,
    SubDistrictPublic,
    SubDistrictUpdate,
)


class SubDistrictService:
    """Service for sub-district metadata operations"""

    def __init__(self, session: Session):
        self.session = session
        self.sub_district_repo = SubDistrictRepository(session)

    def get_sub_districts_by_district(self, district_id: UUID) -> list[SubDistrictPublic]:
        """Get all active sub-districts for a district formatted for API response"""
        sub_districts = self.sub_district_repo.get_by_district(district_id)
        return [
            SubDistrictPublic(tehsilId=sub_district.id, tehsilName=sub_district.name)
            for sub_district in sub_districts
        ]

    def get_sub_district_by_id(self, sub_district_id: UUID) -> SubDistrict | None:
        """Get sub-district by ID"""
        return self.sub_district_repo.get_by_id(sub_district_id)

    def create_sub_district(self, sub_district_in: SubDistrictCreate) -> SubDistrict:
        """Create a new sub-district"""
        sub_district = SubDistrict(
            name=sub_district_in.name,
            code=sub_district_in.code.upper() if sub_district_in.code else None,
            district_id=sub_district_in.district_id,
            is_active=sub_district_in.is_active,
        )
        return self.sub_district_repo.create(sub_district)

    def update_sub_district(
        self, sub_district: SubDistrict, sub_district_update: SubDistrictUpdate
    ) -> SubDistrict:
        """Update sub-district information"""
        update_data = sub_district_update.model_dump(exclude_unset=True)

        # Ensure code is uppercase if provided
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()

        sub_district.sqlmodel_update(update_data)
        return self.sub_district_repo.update(sub_district)

    def code_exists(
        self,
        code: str,
        district_id: UUID,
        exclude_sub_district_id: UUID | None = None,
    ) -> bool:
        """Check if sub-district code exists within a district, optionally excluding a specific sub-district"""
        if not code:
            return False
        existing_sub_district = self.sub_district_repo.get_by_code(
            code.upper(), district_id
        )
        if not existing_sub_district:
            return False
        if (
            exclude_sub_district_id
            and existing_sub_district.id == exclude_sub_district_id
        ):
            return False
        return True

    def delete_sub_district(self, sub_district: SubDistrict) -> None:
        """Delete a sub-district"""
        self.sub_district_repo.delete(sub_district)

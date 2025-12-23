from uuid import UUID

from sqlmodel import Session

from app.db_models.address import District
from app.repositories.address import DistrictRepository
from app.schemas.address.district import DistrictCreate, DistrictPublic, DistrictUpdate


class DistrictService:
    """Service for district metadata operations"""

    def __init__(self, session: Session):
        self.session = session
        self.district_repo = DistrictRepository(session)

    def get_districts_by_state(self, state_id: UUID) -> list[DistrictPublic]:
        """Get all active districts for a state formatted for API response"""
        districts = self.district_repo.get_by_state(state_id)
        return [
            DistrictPublic(districtId=district.id, districtName=district.name)
            for district in districts
        ]

    def get_district_by_id(self, district_id: UUID) -> District | None:
        """Get district by ID"""
        return self.district_repo.get_by_id(district_id)

    def create_district(self, district_in: DistrictCreate) -> District:
        """Create a new district"""
        district = District(
            name=district_in.name,
            code=district_in.code.upper() if district_in.code else None,
            state_id=district_in.state_id,
            is_active=district_in.is_active,
        )
        return self.district_repo.create(district)

    def update_district(
        self, district: District, district_update: DistrictUpdate
    ) -> District:
        """Update district information"""
        update_data = district_update.model_dump(exclude_unset=True)

        # Ensure code is uppercase if provided
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()

        district.sqlmodel_update(update_data)
        return self.district_repo.update(district)

    def code_exists(
        self, code: str, state_id: UUID, exclude_district_id: UUID | None = None
    ) -> bool:
        """Check if district code exists within a state, optionally excluding a specific district"""
        if not code:
            return False
        existing_district = self.district_repo.get_by_code(code.upper(), state_id)
        if not existing_district:
            return False
        if exclude_district_id and existing_district.id == exclude_district_id:
            return False
        return True

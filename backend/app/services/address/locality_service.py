from uuid import UUID

from sqlmodel import Session

from app.db_models.address import Locality
from app.repositories.address import LocalityRepository
from app.schemas.address.locality import (
    LocalityCreate,
    LocalityPublic,
    LocalityUpdate,
)


class LocalityService:
    """Service for locality metadata operations"""

    def __init__(self, session: Session):
        self.session = session
        self.locality_repo = LocalityRepository(session)

    def get_localities_by_sub_district(
        self, sub_district_id: UUID
    ) -> list[LocalityPublic]:
        """Get all active localities for a sub-district formatted for API response"""
        localities = self.locality_repo.get_by_sub_district(sub_district_id)
        return [
            LocalityPublic(localityId=locality.id, localityName=locality.name)
            for locality in localities
        ]

    def get_locality_by_id(self, locality_id: UUID) -> Locality | None:
        """Get locality by ID"""
        return self.locality_repo.get_by_id(locality_id)

    def create_locality(self, locality_in: LocalityCreate) -> Locality:
        """Create a new locality"""
        locality = Locality(
            name=locality_in.name,
            code=locality_in.code.upper() if locality_in.code else None,
            sub_district_id=locality_in.sub_district_id,
            is_active=locality_in.is_active,
        )
        return self.locality_repo.create(locality)

    def update_locality(
        self, locality: Locality, locality_update: LocalityUpdate
    ) -> Locality:
        """Update locality information"""
        update_data = locality_update.model_dump(exclude_unset=True)

        # Ensure code is uppercase if provided
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()

        locality.sqlmodel_update(update_data)
        return self.locality_repo.update(locality)

    def code_exists(
        self,
        code: str,
        sub_district_id: UUID,
        exclude_locality_id: UUID | None = None,
    ) -> bool:
        """Check if locality code exists within a sub-district, optionally excluding a specific locality"""
        if not code:
            return False
        existing_locality = self.locality_repo.get_by_code(code.upper(), sub_district_id)
        if not existing_locality:
            return False
        if exclude_locality_id and existing_locality.id == exclude_locality_id:
            return False
        return True

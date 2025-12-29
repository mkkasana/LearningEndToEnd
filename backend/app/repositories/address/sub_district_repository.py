from uuid import UUID

from sqlmodel import Session, select

from app.db_models.address import SubDistrict
from app.repositories.base import BaseRepository


class SubDistrictRepository(BaseRepository[SubDistrict]):
    """Repository for SubDistrict data access"""

    def __init__(self, session: Session):
        super().__init__(SubDistrict, session)

    def get_by_district(self, district_id: UUID) -> list[SubDistrict]:
        """Get all active sub-districts for a specific district, ordered by name"""
        statement = (
            select(SubDistrict)
            .where(SubDistrict.district_id == district_id)
            .where(SubDistrict.is_active)
            .order_by(SubDistrict.name)
        )
        return list(self.session.exec(statement).all())

    def get_by_code(self, code: str, district_id: UUID) -> SubDistrict | None:
        """Get sub-district by code within a specific district"""
        statement = select(SubDistrict).where(
            SubDistrict.code == code, SubDistrict.district_id == district_id
        )
        return self.session.exec(statement).first()

    def count_by_district(self, district_id: UUID) -> int:
        """Count sub-districts for a specific district"""
        from sqlmodel import func

        statement = (
            select(func.count())
            .select_from(SubDistrict)
            .where(SubDistrict.district_id == district_id)
        )
        return self.session.exec(statement).one()

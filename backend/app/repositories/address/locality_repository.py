from uuid import UUID

from sqlmodel import Session, select

from app.db_models.address import Locality
from app.repositories.base import BaseRepository


class LocalityRepository(BaseRepository[Locality]):
    """Repository for Locality data access"""

    def __init__(self, session: Session):
        super().__init__(Locality, session)

    def get_by_sub_district(self, sub_district_id: UUID) -> list[Locality]:
        """Get all active localities for a specific sub-district, ordered by name"""
        statement = (
            select(Locality)
            .where(Locality.sub_district_id == sub_district_id)
            .where(Locality.is_active)
            .order_by(Locality.name)
        )
        return list(self.session.exec(statement).all())

    def get_by_code(self, code: str, sub_district_id: UUID) -> Locality | None:
        """Get locality by code within a specific sub-district"""
        statement = select(Locality).where(
            Locality.code == code, Locality.sub_district_id == sub_district_id
        )
        return self.session.exec(statement).first()

    def count_by_sub_district(self, sub_district_id: UUID) -> int:
        """Count localities for a specific sub-district"""
        from sqlmodel import func

        statement = (
            select(func.count())
            .select_from(Locality)
            .where(Locality.sub_district_id == sub_district_id)
        )
        return self.session.exec(statement).one()

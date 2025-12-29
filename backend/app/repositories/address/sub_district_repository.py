import logging
from uuid import UUID

from sqlmodel import Session, select

from app.db_models.address import SubDistrict
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class SubDistrictRepository(BaseRepository[SubDistrict]):
    """Repository for SubDistrict data access"""

    def __init__(self, session: Session):
        super().__init__(SubDistrict, session)

    def get_by_district(self, district_id: UUID) -> list[SubDistrict]:
        """Get all active sub-districts for a specific district, ordered by name"""
        logger.debug(f"Querying sub-districts for district: {district_id}")
        statement = (
            select(SubDistrict)
            .where(SubDistrict.district_id == district_id)
            .where(SubDistrict.is_active)
            .order_by(SubDistrict.name)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} sub-districts for district {district_id}")
        return results

    def get_by_code(self, code: str, district_id: UUID) -> SubDistrict | None:
        """Get sub-district by code within a specific district"""
        logger.debug(f"Querying sub-district by code: {code}, district_id: {district_id}")
        statement = select(SubDistrict).where(
            SubDistrict.code == code, SubDistrict.district_id == district_id
        )
        result = self.session.exec(statement).first()
        if result:
            logger.debug(f"Sub-district found: {result.name} (code: {code})")
        else:
            logger.debug(f"No sub-district found with code: {code}")
        return result

    def count_by_district(self, district_id: UUID) -> int:
        """Count sub-districts for a specific district"""
        from sqlmodel import func

        logger.debug(f"Counting sub-districts for district: {district_id}")
        statement = (
            select(func.count())
            .select_from(SubDistrict)
            .where(SubDistrict.district_id == district_id)
        )
        count = self.session.exec(statement).one()
        logger.debug(f"District {district_id} has {count} sub-districts")
        return count

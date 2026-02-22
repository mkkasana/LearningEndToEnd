import logging
from uuid import UUID

from sqlmodel import Session, select

from app.db_models.address import Locality
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class LocalityRepository(BaseRepository[Locality]):
    """Repository for Locality data access"""

    def __init__(self, session: Session):
        super().__init__(Locality, session)

    def get_by_sub_district(self, sub_district_id: UUID) -> list[Locality]:
        """Get all active localities for a specific sub-district, ordered by name"""
        logger.debug(f"Querying localities for sub-district: {sub_district_id}")
        statement = (
            select(Locality)
            .where(Locality.sub_district_id == sub_district_id)
            .where(Locality.is_active)
            .order_by(Locality.name)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(
            f"Retrieved {len(results)} localities for sub-district {sub_district_id}"
        )
        return results

    def get_by_code(self, code: str, sub_district_id: UUID) -> Locality | None:
        """Get locality by code within a specific sub-district"""
        logger.debug(
            f"Querying locality by code: {code}, sub_district_id: {sub_district_id}"
        )
        statement = select(Locality).where(
            Locality.code == code, Locality.sub_district_id == sub_district_id
        )
        result = self.session.exec(statement).first()
        if result:
            logger.debug(f"Locality found: {result.name} (code: {code})")
        else:
            logger.debug(f"No locality found with code: {code}")
        return result

    def count_by_sub_district(self, sub_district_id: UUID) -> int:
        """Count localities for a specific sub-district"""
        from sqlmodel import func

        logger.debug(f"Counting localities for sub-district: {sub_district_id}")
        statement = (
            select(func.count())
            .select_from(Locality)
            .where(Locality.sub_district_id == sub_district_id)
        )
        count = self.session.exec(statement).one()
        logger.debug(f"Sub-district {sub_district_id} has {count} localities")
        return count

import logging

from sqlmodel import Session, select

from app.db_models.address import Country
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class CountryRepository(BaseRepository[Country]):
    """Repository for Country data access"""

    def __init__(self, session: Session):
        super().__init__(Country, session)

    def get_active_countries(self) -> list[Country]:
        """Get all active countries ordered by name"""
        logger.debug("Querying all active countries")
        statement = select(Country).where(Country.is_active).order_by(Country.name)
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} active countries")
        return results

    def get_by_code(self, code: str) -> Country | None:
        """Get country by ISO code"""
        logger.debug(f"Querying country by code: {code}")
        statement = select(Country).where(Country.code == code)
        result = self.session.exec(statement).first()
        if result:
            logger.debug(f"Country found: {result.name} (code: {code})")
        else:
            logger.debug(f"No country found with code: {code}")
        return result

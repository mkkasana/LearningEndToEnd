from sqlmodel import Session, select

from app.db_models.address import Country
from app.repositories.base import BaseRepository


class CountryRepository(BaseRepository[Country]):
    """Repository for Country data access"""

    def __init__(self, session: Session):
        super().__init__(Country, session)

    def get_active_countries(self) -> list[Country]:
        """Get all active countries ordered by name"""
        statement = select(Country).where(Country.is_active == True).order_by(Country.name)
        return list(self.session.exec(statement).all())

    def get_by_code(self, code: str) -> Country | None:
        """Get country by ISO code"""
        statement = select(Country).where(Country.code == code)
        return self.session.exec(statement).first()

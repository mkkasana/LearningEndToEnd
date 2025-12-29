"""Gender repository."""

import logging
import uuid

from sqlmodel import Session, select

from app.db_models.person.gender import Gender
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class GenderRepository(BaseRepository[Gender]):
    """Repository for gender data access."""

    def __init__(self, session: Session):
        super().__init__(Gender, session)

    def get_active_genders(self) -> list[Gender]:
        """Get all active genders sorted by name."""
        logger.debug("Querying all active genders")
        statement = select(Gender).where(Gender.is_active).order_by(Gender.name)
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} active genders")
        return results

    def get_by_code(self, code: str) -> Gender | None:
        """Get gender by code."""
        logger.debug(f"Querying gender by code: {code}")
        statement = select(Gender).where(Gender.code == code.upper())
        result = self.session.exec(statement).first()
        if result:
            logger.debug(f"Gender found: {result.name} (code: {code})")
        else:
            logger.debug(f"No gender found with code: {code}")
        return result

    def code_exists(
        self, code: str, exclude_gender_id: uuid.UUID | None = None
    ) -> bool:
        """Check if gender code already exists."""
        logger.debug(f"Checking if gender code exists: {code}, exclude_id={exclude_gender_id}")
        statement = select(Gender).where(Gender.code == code.upper())
        if exclude_gender_id:
            statement = statement.where(Gender.id != exclude_gender_id)
        exists = self.session.exec(statement).first() is not None
        logger.debug(f"Gender code {code} exists: {exists}")
        return exists

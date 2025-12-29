"""Religion Category repository."""

import logging
import uuid

from sqlmodel import Session, select

from app.db_models.religion.religion_category import ReligionCategory
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ReligionCategoryRepository(BaseRepository[ReligionCategory]):
    """Repository for religion category data access."""

    def __init__(self, session: Session):
        super().__init__(ReligionCategory, session)

    def get_categories_by_religion(
        self, religion_id: uuid.UUID
    ) -> list[ReligionCategory]:
        """Get all active categories for a specific religion sorted by name."""
        logger.debug(f"Querying categories for religion: {religion_id}")
        statement = (
            select(ReligionCategory)
            .where(ReligionCategory.religion_id == religion_id)
            .where(ReligionCategory.is_active)
            .order_by(ReligionCategory.name)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} categories for religion {religion_id}")
        return results

    def code_exists(
        self,
        code: str,
        religion_id: uuid.UUID,
        exclude_category_id: uuid.UUID | None = None,
    ) -> bool:
        """Check if category code already exists within the same religion."""
        logger.debug(f"Checking if category code exists: {code}, religion_id={religion_id}, exclude_id={exclude_category_id}")
        statement = select(ReligionCategory).where(
            ReligionCategory.code == code.upper(),
            ReligionCategory.religion_id == religion_id,
        )
        if exclude_category_id:
            statement = statement.where(ReligionCategory.id != exclude_category_id)
        exists = self.session.exec(statement).first() is not None
        logger.debug(f"Category code {code} exists: {exists}")
        return exists

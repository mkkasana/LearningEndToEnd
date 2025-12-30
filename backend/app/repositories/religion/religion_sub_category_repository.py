"""Religion Sub-Category repository."""

import logging
import uuid

from sqlmodel import Session, select

from app.db_models.religion.religion_sub_category import ReligionSubCategory
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ReligionSubCategoryRepository(BaseRepository[ReligionSubCategory]):
    """Repository for religion sub-category data access."""

    def __init__(self, session: Session):
        super().__init__(ReligionSubCategory, session)

    def get_sub_categories_by_category(
        self, category_id: uuid.UUID
    ) -> list[ReligionSubCategory]:
        """Get all active sub-categories for a specific category sorted by name."""
        logger.debug(f"Querying sub-categories for category: {category_id}")
        statement = (
            select(ReligionSubCategory)
            .where(ReligionSubCategory.category_id == category_id)
            .where(ReligionSubCategory.is_active)
            .order_by(ReligionSubCategory.name)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(
            f"Retrieved {len(results)} sub-categories for category {category_id}"
        )
        return results

    def code_exists(
        self,
        code: str,
        category_id: uuid.UUID,
        exclude_sub_category_id: uuid.UUID | None = None,
    ) -> bool:
        """Check if sub-category code already exists within the same category."""
        logger.debug(
            f"Checking if sub-category code exists: {code}, category_id={category_id}, exclude_id={exclude_sub_category_id}"
        )
        statement = select(ReligionSubCategory).where(
            ReligionSubCategory.code == code.upper(),
            ReligionSubCategory.category_id == category_id,
        )
        if exclude_sub_category_id:
            statement = statement.where(
                ReligionSubCategory.id != exclude_sub_category_id
            )
        exists = self.session.exec(statement).first() is not None
        logger.debug(f"Sub-category code {code} exists: {exists}")
        return exists

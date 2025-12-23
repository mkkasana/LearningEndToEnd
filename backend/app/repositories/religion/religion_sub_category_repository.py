"""Religion Sub-Category repository."""

import uuid

from sqlmodel import select, Session

from app.db_models.religion.religion_sub_category import ReligionSubCategory
from app.repositories.base import BaseRepository


class ReligionSubCategoryRepository(BaseRepository[ReligionSubCategory]):
    """Repository for religion sub-category data access."""

    def __init__(self, session: Session):
        super().__init__(ReligionSubCategory, session)

    def get_sub_categories_by_category(self, category_id: uuid.UUID) -> list[ReligionSubCategory]:
        """Get all active sub-categories for a specific category sorted by name."""
        statement = (
            select(ReligionSubCategory)
            .where(ReligionSubCategory.category_id == category_id)
            .where(ReligionSubCategory.is_active == True)
            .order_by(ReligionSubCategory.name)
        )
        return list(self.session.exec(statement).all())

    def code_exists(
        self,
        code: str,
        category_id: uuid.UUID,
        exclude_sub_category_id: uuid.UUID | None = None,
    ) -> bool:
        """Check if sub-category code already exists within the same category."""
        statement = select(ReligionSubCategory).where(
            ReligionSubCategory.code == code.upper(),
            ReligionSubCategory.category_id == category_id,
        )
        if exclude_sub_category_id:
            statement = statement.where(ReligionSubCategory.id != exclude_sub_category_id)
        return self.session.exec(statement).first() is not None

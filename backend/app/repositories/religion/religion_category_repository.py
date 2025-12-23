"""Religion Category repository."""

import uuid

from sqlmodel import select, Session

from app.db_models.religion.religion_category import ReligionCategory
from app.repositories.base import BaseRepository


class ReligionCategoryRepository(BaseRepository[ReligionCategory]):
    """Repository for religion category data access."""

    def __init__(self, session: Session):
        super().__init__(ReligionCategory, session)

    def get_categories_by_religion(self, religion_id: uuid.UUID) -> list[ReligionCategory]:
        """Get all active categories for a specific religion sorted by name."""
        statement = (
            select(ReligionCategory)
            .where(ReligionCategory.religion_id == religion_id)
            .where(ReligionCategory.is_active == True)
            .order_by(ReligionCategory.name)
        )
        return list(self.session.exec(statement).all())

    def code_exists(
        self,
        code: str,
        religion_id: uuid.UUID,
        exclude_category_id: uuid.UUID | None = None,
    ) -> bool:
        """Check if category code already exists within the same religion."""
        statement = select(ReligionCategory).where(
            ReligionCategory.code == code.upper(),
            ReligionCategory.religion_id == religion_id,
        )
        if exclude_category_id:
            statement = statement.where(ReligionCategory.id != exclude_category_id)
        return self.session.exec(statement).first() is not None

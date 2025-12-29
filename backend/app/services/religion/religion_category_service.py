"""Religion Category service."""

import uuid

from sqlmodel import Session

from app.db_models.religion.religion_category import ReligionCategory
from app.repositories.religion.religion_category_repository import (
    ReligionCategoryRepository,
)
from app.schemas.religion import (
    ReligionCategoryCreate,
    ReligionCategoryPublic,
    ReligionCategoryUpdate,
)


class ReligionCategoryService:
    """Service for religion category business logic."""

    def __init__(self, session: Session):
        self.category_repo = ReligionCategoryRepository(session)

    def get_categories_by_religion(
        self, religion_id: uuid.UUID
    ) -> list[ReligionCategoryPublic]:
        """Get all active categories for a religion."""
        categories = self.category_repo.get_categories_by_religion(religion_id)
        return [
            ReligionCategoryPublic(categoryId=c.id, categoryName=c.name)
            for c in categories
        ]

    def get_category_by_id(self, category_id: uuid.UUID) -> ReligionCategory | None:
        """Get category by ID."""
        return self.category_repo.get_by_id(category_id)

    def create_category(
        self, category_create: ReligionCategoryCreate
    ) -> ReligionCategory:
        """Create a new religion category."""
        category = ReligionCategory(**category_create.model_dump())
        if category.code:
            category.code = category.code.upper()
        return self.category_repo.create(category)

    def update_category(
        self, category: ReligionCategory, category_update: ReligionCategoryUpdate
    ) -> ReligionCategory:
        """Update a religion category."""
        update_data = category_update.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()
        for key, value in update_data.items():
            setattr(category, key, value)
        return self.category_repo.update(category)

    def delete_category(self, category: ReligionCategory) -> None:
        """Delete a religion category."""
        self.category_repo.delete(category)

    def code_exists(
        self,
        code: str,
        religion_id: uuid.UUID,
        exclude_category_id: uuid.UUID | None = None,
    ) -> bool:
        """Check if category code exists within the same religion."""
        return self.category_repo.code_exists(code, religion_id, exclude_category_id)

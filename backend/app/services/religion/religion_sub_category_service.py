"""Religion Sub-Category service."""

import uuid

from sqlmodel import Session

from app.db_models.religion.religion_sub_category import ReligionSubCategory
from app.repositories.religion.religion_sub_category_repository import (
    ReligionSubCategoryRepository,
)
from app.schemas.religion import (
    ReligionSubCategoryCreate,
    ReligionSubCategoryPublic,
    ReligionSubCategoryUpdate,
)


class ReligionSubCategoryService:
    """Service for religion sub-category business logic."""

    def __init__(self, session: Session):
        self.sub_category_repo = ReligionSubCategoryRepository(session)

    def get_sub_categories_by_category(
        self, category_id: uuid.UUID
    ) -> list[ReligionSubCategoryPublic]:
        """Get all active sub-categories for a category."""
        sub_categories = self.sub_category_repo.get_sub_categories_by_category(
            category_id
        )
        return [
            ReligionSubCategoryPublic(subCategoryId=sc.id, subCategoryName=sc.name)
            for sc in sub_categories
        ]

    def get_sub_category_by_id(
        self, sub_category_id: uuid.UUID
    ) -> ReligionSubCategory | None:
        """Get sub-category by ID."""
        return self.sub_category_repo.get_by_id(sub_category_id)

    def create_sub_category(
        self, sub_category_create: ReligionSubCategoryCreate
    ) -> ReligionSubCategory:
        """Create a new religion sub-category."""
        sub_category = ReligionSubCategory(**sub_category_create.model_dump())
        if sub_category.code:
            sub_category.code = sub_category.code.upper()
        return self.sub_category_repo.create(sub_category)

    def update_sub_category(
        self,
        sub_category: ReligionSubCategory,
        sub_category_update: ReligionSubCategoryUpdate,
    ) -> ReligionSubCategory:
        """Update a religion sub-category."""
        update_data = sub_category_update.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()
        for key, value in update_data.items():
            setattr(sub_category, key, value)
        return self.sub_category_repo.update(sub_category)

    def delete_sub_category(self, sub_category: ReligionSubCategory) -> None:
        """Delete a religion sub-category."""
        self.sub_category_repo.delete(sub_category)

    def code_exists(
        self,
        code: str,
        category_id: uuid.UUID,
        exclude_sub_category_id: uuid.UUID | None = None,
    ) -> bool:
        """Check if sub-category code exists within the same category."""
        return self.sub_category_repo.code_exists(
            code, category_id, exclude_sub_category_id
        )

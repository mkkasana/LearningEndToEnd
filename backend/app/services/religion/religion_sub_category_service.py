"""Religion Sub-Category service."""

import logging
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

logger = logging.getLogger(__name__)


class ReligionSubCategoryService:
    """Service for religion sub-category business logic."""

    def __init__(self, session: Session):
        self.sub_category_repo = ReligionSubCategoryRepository(session)

    def get_sub_categories_by_category(
        self, category_id: uuid.UUID
    ) -> list[ReligionSubCategoryPublic]:
        """Get all active sub-categories for a category."""
        logger.debug(f"Fetching sub-categories for religion category ID: {category_id}")
        sub_categories = self.sub_category_repo.get_sub_categories_by_category(
            category_id
        )
        logger.debug(f"Found {len(sub_categories)} sub-categories for category {category_id}")
        return [
            ReligionSubCategoryPublic(subCategoryId=sc.id, subCategoryName=sc.name)
            for sc in sub_categories
        ]

    def get_sub_category_by_id(
        self, sub_category_id: uuid.UUID
    ) -> ReligionSubCategory | None:
        """Get sub-category by ID."""
        logger.debug(f"Fetching religion sub-category by ID: {sub_category_id}")
        sub_category = self.sub_category_repo.get_by_id(sub_category_id)
        if sub_category:
            logger.debug(f"Religion sub-category found: {sub_category.name} (ID: {sub_category_id})")
        else:
            logger.debug(f"Religion sub-category not found: ID {sub_category_id}")
        return sub_category

    def create_sub_category(
        self, sub_category_create: ReligionSubCategoryCreate
    ) -> ReligionSubCategory:
        """Create a new religion sub-category."""
        logger.info(f"Creating religion sub-category: {sub_category_create.name} for category {sub_category_create.religion_category_id}")
        sub_category = ReligionSubCategory(**sub_category_create.model_dump())
        if sub_category.code:
            sub_category.code = sub_category.code.upper()
        created_sub_category = self.sub_category_repo.create(sub_category)
        logger.info(f"Religion sub-category created successfully: {created_sub_category.name} (ID: {created_sub_category.id})")
        return created_sub_category

    def update_sub_category(
        self,
        sub_category: ReligionSubCategory,
        sub_category_update: ReligionSubCategoryUpdate,
    ) -> ReligionSubCategory:
        """Update a religion sub-category."""
        logger.info(f"Updating religion sub-category: {sub_category.name} (ID: {sub_category.id})")
        update_data = sub_category_update.model_dump(exclude_unset=True)
        
        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(f"Updating fields for religion sub-category {sub_category.id}: {update_fields}")
        
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()
        for key, value in update_data.items():
            setattr(sub_category, key, value)
        updated_sub_category = self.sub_category_repo.update(sub_category)
        logger.info(f"Religion sub-category updated successfully: {updated_sub_category.name} (ID: {updated_sub_category.id})")
        return updated_sub_category

    def delete_sub_category(self, sub_category: ReligionSubCategory) -> None:
        """Delete a religion sub-category."""
        logger.warning(f"Deleting religion sub-category: {sub_category.name} (ID: {sub_category.id})")
        self.sub_category_repo.delete(sub_category)
        logger.info(f"Religion sub-category deleted successfully: {sub_category.name} (ID: {sub_category.id})")

    def code_exists(
        self,
        code: str,
        category_id: uuid.UUID,
        exclude_sub_category_id: uuid.UUID | None = None,
    ) -> bool:
        """Check if sub-category code exists within the same category."""
        logger.debug(f"Checking if religion sub-category code exists: {code} in category {category_id}")
        exists = self.sub_category_repo.code_exists(
            code, category_id, exclude_sub_category_id
        )
        if exists:
            logger.debug(f"Religion sub-category code already exists: {code}")
        else:
            logger.debug(f"Religion sub-category code does not exist: {code}")
        return exists

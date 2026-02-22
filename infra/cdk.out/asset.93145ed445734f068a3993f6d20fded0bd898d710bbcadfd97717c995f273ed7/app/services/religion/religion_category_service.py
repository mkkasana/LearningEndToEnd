"""Religion Category service."""

import logging
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

logger = logging.getLogger(__name__)


class ReligionCategoryService:
    """Service for religion category business logic."""

    def __init__(self, session: Session):
        self.category_repo = ReligionCategoryRepository(session)

    def get_categories_by_religion(
        self, religion_id: uuid.UUID
    ) -> list[ReligionCategoryPublic]:
        """Get all active categories for a religion."""
        logger.debug(f"Fetching categories for religion ID: {religion_id}")
        categories = self.category_repo.get_categories_by_religion(religion_id)
        logger.debug(f"Found {len(categories)} categories for religion {religion_id}")
        return [
            ReligionCategoryPublic(categoryId=c.id, categoryName=c.name)
            for c in categories
        ]

    def get_category_by_id(self, category_id: uuid.UUID) -> ReligionCategory | None:
        """Get category by ID."""
        logger.debug(f"Fetching religion category by ID: {category_id}")
        category = self.category_repo.get_by_id(category_id)
        if category:
            logger.debug(
                f"Religion category found: {category.name} (ID: {category_id})"
            )
        else:
            logger.debug(f"Religion category not found: ID {category_id}")
        return category

    def create_category(
        self, category_create: ReligionCategoryCreate
    ) -> ReligionCategory:
        """Create a new religion category."""
        logger.info(
            f"Creating religion category: {category_create.name} for religion {category_create.religion_id}"
        )
        category = ReligionCategory(**category_create.model_dump())
        if category.code:
            category.code = category.code.upper()
        created_category = self.category_repo.create(category)
        logger.info(
            f"Religion category created successfully: {created_category.name} (ID: {created_category.id})"
        )
        return created_category

    def update_category(
        self, category: ReligionCategory, category_update: ReligionCategoryUpdate
    ) -> ReligionCategory:
        """Update a religion category."""
        logger.info(f"Updating religion category: {category.name} (ID: {category.id})")
        update_data = category_update.model_dump(exclude_unset=True)

        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(
                f"Updating fields for religion category {category.id}: {update_fields}"
            )

        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()
        for key, value in update_data.items():
            setattr(category, key, value)
        updated_category = self.category_repo.update(category)
        logger.info(
            f"Religion category updated successfully: {updated_category.name} (ID: {updated_category.id})"
        )
        return updated_category

    def delete_category(self, category: ReligionCategory) -> None:
        """Delete a religion category."""
        logger.warning(
            f"Deleting religion category: {category.name} (ID: {category.id})"
        )
        self.category_repo.delete(category)
        logger.info(
            f"Religion category deleted successfully: {category.name} (ID: {category.id})"
        )

    def code_exists(
        self,
        code: str,
        religion_id: uuid.UUID,
        exclude_category_id: uuid.UUID | None = None,
    ) -> bool:
        """Check if category code exists within the same religion."""
        logger.debug(
            f"Checking if religion category code exists: {code} in religion {religion_id}"
        )
        exists = self.category_repo.code_exists(code, religion_id, exclude_category_id)
        if exists:
            logger.debug(f"Religion category code already exists: {code}")
        else:
            logger.debug(f"Religion category code does not exist: {code}")
        return exists

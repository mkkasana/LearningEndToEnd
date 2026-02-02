"""Person Religion service."""

import logging
import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person_religion import PersonReligion
from app.repositories.person.person_religion_repository import PersonReligionRepository
from app.repositories.religion.religion_category_repository import (
    ReligionCategoryRepository,
)
from app.repositories.religion.religion_repository import ReligionRepository
from app.repositories.religion.religion_sub_category_repository import (
    ReligionSubCategoryRepository,
)
from app.schemas.person.person_religion import (
    PersonReligionCreate,
    PersonReligionUpdate,
)

logger = logging.getLogger(__name__)


class PersonReligionService:
    """Service for person religion business logic."""

    def __init__(self, session: Session):
        self.session = session
        self.person_religion_repo = PersonReligionRepository(session)

    def get_by_person_id(self, person_id: uuid.UUID) -> PersonReligion | None:
        """Get religion for a person."""
        return self.person_religion_repo.get_by_person_id(person_id)

    def create_person_religion(
        self, person_id: uuid.UUID, religion_create: PersonReligionCreate
    ) -> PersonReligion:
        """Create person religion."""
        person_religion = PersonReligion(
            person_id=person_id, **religion_create.model_dump()
        )
        return self.person_religion_repo.create(person_religion)

    def update_person_religion(
        self, person_religion: PersonReligion, religion_update: PersonReligionUpdate
    ) -> PersonReligion:
        """Update person religion."""
        update_data = religion_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(person_religion, key, value)
        person_religion.updated_at = datetime.utcnow()
        return self.person_religion_repo.update(person_religion)

    def delete_person_religion(self, person_religion: PersonReligion) -> None:
        """Delete person religion."""
        self.person_religion_repo.delete(person_religion)

    def get_formatted_religion(self, person_id: uuid.UUID) -> str | None:
        """Get formatted religion string for display."""
        logger.debug(f"Getting formatted religion for person: {person_id}")
        person_religion = self.person_religion_repo.get_by_person_id(person_id)
        if not person_religion:
            logger.debug(f"No religion found for person {person_id}")
            return None

        # Initialize repositories for religion lookups
        religion_repo = ReligionRepository(self.session)
        category_repo = ReligionCategoryRepository(self.session)
        sub_category_repo = ReligionSubCategoryRepository(self.session)

        # Build religion string from available parts
        parts = []

        # Get religion name
        religion = religion_repo.get_by_id(person_religion.religion_id)
        if religion:
            parts.append(religion.name)

        # Get category name
        if person_religion.religion_category_id:
            category = category_repo.get_by_id(person_religion.religion_category_id)
            if category:
                parts.append(category.name)

        # Get sub-category name
        if person_religion.religion_sub_category_id:
            sub_category = sub_category_repo.get_by_id(
                person_religion.religion_sub_category_id
            )
            if sub_category:
                parts.append(sub_category.name)

        formatted = " - ".join(parts) if parts else None
        logger.debug(f"Formatted religion for person {person_id}: {formatted}")
        return formatted

"""Gender service."""

import uuid

from sqlmodel import Session

from app.db_models.person.gender import Gender
from app.repositories.person.gender_repository import GenderRepository
from app.schemas.person import GenderCreate, GenderPublic, GenderUpdate


class GenderService:
    """Service for gender business logic."""

    def __init__(self, session: Session):
        self.gender_repo = GenderRepository(session)

    def get_genders(self) -> list[GenderPublic]:
        """Get all active genders."""
        genders = self.gender_repo.get_active_genders()
        return [
            GenderPublic(genderId=g.id, genderName=g.name, genderCode=g.code)
            for g in genders
        ]

    def get_gender_by_id(self, gender_id: uuid.UUID) -> Gender | None:
        """Get gender by ID."""
        return self.gender_repo.get_by_id(gender_id)

    def get_gender_by_code(self, code: str) -> Gender | None:
        """Get gender by code."""
        return self.gender_repo.get_by_code(code)

    def create_gender(self, gender_create: GenderCreate) -> Gender:
        """Create a new gender."""
        gender = Gender(**gender_create.model_dump())
        gender.code = gender.code.upper()
        return self.gender_repo.create(gender)

    def update_gender(self, gender: Gender, gender_update: GenderUpdate) -> Gender:
        """Update a gender."""
        update_data = gender_update.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()
        for key, value in update_data.items():
            setattr(gender, key, value)
        return self.gender_repo.update(gender)

    def delete_gender(self, gender: Gender) -> None:
        """Delete a gender."""
        self.gender_repo.delete(gender)

    def code_exists(
        self, code: str, exclude_gender_id: uuid.UUID | None = None
    ) -> bool:
        """Check if gender code exists."""
        return self.gender_repo.code_exists(code, exclude_gender_id)

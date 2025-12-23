"""Profession service."""

import uuid

from sqlmodel import Session

from app.db_models.person.profession import Profession
from app.repositories.person.profession_repository import ProfessionRepository
from app.schemas.person import ProfessionCreate, ProfessionPublic, ProfessionUpdate


class ProfessionService:
    """Service for profession business logic."""

    def __init__(self, session: Session):
        self.profession_repo = ProfessionRepository(session)

    def get_professions(self) -> list[ProfessionPublic]:
        """Get all active professions."""
        professions = self.profession_repo.get_active_professions()
        return [
            ProfessionPublic(
                professionId=p.id,
                professionName=p.name,
                professionDescription=p.description,
                professionWeight=p.weight,
            )
            for p in professions
        ]

    def get_profession_by_id(self, profession_id: uuid.UUID) -> Profession | None:
        """Get profession by ID."""
        return self.profession_repo.get_by_id(profession_id)

    def create_profession(self, profession_create: ProfessionCreate) -> Profession:
        """Create a new profession."""
        profession = Profession(**profession_create.model_dump())
        return self.profession_repo.create(profession)

    def update_profession(
        self, profession: Profession, profession_update: ProfessionUpdate
    ) -> Profession:
        """Update a profession."""
        update_data = profession_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profession, key, value)
        return self.profession_repo.update(profession)

    def delete_profession(self, profession: Profession) -> None:
        """Delete a profession."""
        self.profession_repo.delete(profession)

    def name_exists(
        self, name: str, exclude_profession_id: uuid.UUID | None = None
    ) -> bool:
        """Check if profession name exists."""
        return self.profession_repo.name_exists(name, exclude_profession_id)

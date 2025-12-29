"""Religion service."""

import uuid

from sqlmodel import Session

from app.db_models.religion.religion import Religion
from app.repositories.religion.religion_repository import ReligionRepository
from app.schemas.religion import ReligionCreate, ReligionPublic, ReligionUpdate


class ReligionService:
    """Service for religion business logic."""

    def __init__(self, session: Session):
        self.religion_repo = ReligionRepository(session)

    def get_religions(self) -> list[ReligionPublic]:
        """Get all active religions."""
        religions = self.religion_repo.get_active_religions()
        return [ReligionPublic(religionId=r.id, religionName=r.name) for r in religions]

    def get_religion_by_id(self, religion_id: uuid.UUID) -> Religion | None:
        """Get religion by ID."""
        return self.religion_repo.get_by_id(religion_id)

    def create_religion(self, religion_create: ReligionCreate) -> Religion:
        """Create a new religion."""
        religion = Religion(**religion_create.model_dump())
        religion.code = religion.code.upper()
        return self.religion_repo.create(religion)

    def update_religion(
        self, religion: Religion, religion_update: ReligionUpdate
    ) -> Religion:
        """Update a religion."""
        update_data = religion_update.model_dump(exclude_unset=True)
        if "code" in update_data and update_data["code"]:
            update_data["code"] = update_data["code"].upper()
        for key, value in update_data.items():
            setattr(religion, key, value)
        return self.religion_repo.update(religion)

    def delete_religion(self, religion: Religion) -> None:
        """Delete a religion."""
        self.religion_repo.delete(religion)

    def code_exists(
        self, code: str, exclude_religion_id: uuid.UUID | None = None
    ) -> bool:
        """Check if religion code exists."""
        return self.religion_repo.code_exists(code, exclude_religion_id)

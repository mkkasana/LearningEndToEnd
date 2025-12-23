"""Profession repository."""

import uuid

from sqlmodel import select, Session

from app.db_models.person.profession import Profession
from app.repositories.base import BaseRepository


class ProfessionRepository(BaseRepository[Profession]):
    """Repository for profession data access."""

    def __init__(self, session: Session):
        super().__init__(Profession, session)

    def get_active_professions(self) -> list[Profession]:
        """Get all active professions sorted by weight (descending) then name."""
        statement = (
            select(Profession)
            .where(Profession.is_active == True)
            .order_by(Profession.weight.desc(), Profession.name)
        )
        return list(self.session.exec(statement).all())

    def name_exists(self, name: str, exclude_profession_id: uuid.UUID | None = None) -> bool:
        """Check if profession name already exists."""
        statement = select(Profession).where(Profession.name == name)
        if exclude_profession_id:
            statement = statement.where(Profession.id != exclude_profession_id)
        return self.session.exec(statement).first() is not None

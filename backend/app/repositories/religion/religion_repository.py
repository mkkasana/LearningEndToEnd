"""Religion repository."""

import uuid

from sqlmodel import select, Session

from app.db_models.religion.religion import Religion
from app.repositories.base import BaseRepository


class ReligionRepository(BaseRepository[Religion]):
    """Repository for religion data access."""

    def __init__(self, session: Session):
        super().__init__(Religion, session)

    def get_active_religions(self) -> list[Religion]:
        """Get all active religions sorted by name."""
        statement = select(Religion).where(Religion.is_active == True).order_by(Religion.name)
        return list(self.session.exec(statement).all())

    def code_exists(self, code: str, exclude_religion_id: uuid.UUID | None = None) -> bool:
        """Check if religion code already exists."""
        statement = select(Religion).where(Religion.code == code.upper())
        if exclude_religion_id:
            statement = statement.where(Religion.id != exclude_religion_id)
        return self.session.exec(statement).first() is not None

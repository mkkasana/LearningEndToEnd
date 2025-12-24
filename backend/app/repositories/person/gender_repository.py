"""Gender repository."""

import uuid

from sqlmodel import Session, select

from app.db_models.person.gender import Gender
from app.repositories.base import BaseRepository


class GenderRepository(BaseRepository[Gender]):
    """Repository for gender data access."""

    def __init__(self, session: Session):
        super().__init__(Gender, session)

    def get_active_genders(self) -> list[Gender]:
        """Get all active genders sorted by name."""
        statement = (
            select(Gender).where(Gender.is_active == True).order_by(Gender.name)
        )
        return list(self.session.exec(statement).all())

    def get_by_code(self, code: str) -> Gender | None:
        """Get gender by code."""
        statement = select(Gender).where(Gender.code == code.upper())
        return self.session.exec(statement).first()

    def code_exists(
        self, code: str, exclude_gender_id: uuid.UUID | None = None
    ) -> bool:
        """Check if gender code already exists."""
        statement = select(Gender).where(Gender.code == code.upper())
        if exclude_gender_id:
            statement = statement.where(Gender.id != exclude_gender_id)
        return self.session.exec(statement).first() is not None

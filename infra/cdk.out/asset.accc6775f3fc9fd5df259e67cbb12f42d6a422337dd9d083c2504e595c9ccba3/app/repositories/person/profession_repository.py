"""Profession repository."""

import logging
import uuid

from sqlmodel import Session, desc, select

from app.db_models.person.profession import Profession
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ProfessionRepository(BaseRepository[Profession]):
    """Repository for profession data access."""

    def __init__(self, session: Session):
        super().__init__(Profession, session)

    def get_active_professions(self) -> list[Profession]:
        """Get all active professions sorted by weight (descending) then name."""
        logger.debug("Querying all active professions")
        statement = (
            select(Profession)
            .where(Profession.is_active)
            .order_by(desc(Profession.weight), Profession.name)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} active professions")
        return results

    def name_exists(
        self, name: str, exclude_profession_id: uuid.UUID | None = None
    ) -> bool:
        """Check if profession name already exists."""
        logger.debug(
            f"Checking if profession name exists: {name}, exclude_id={exclude_profession_id}"
        )
        statement = select(Profession).where(Profession.name == name)
        if exclude_profession_id:
            statement = statement.where(Profession.id != exclude_profession_id)
        exists = self.session.exec(statement).first() is not None
        logger.debug(f"Profession name '{name}' exists: {exists}")
        return exists

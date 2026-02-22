"""Religion repository."""

import logging
import uuid

from sqlmodel import Session, select

from app.db_models.religion.religion import Religion
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ReligionRepository(BaseRepository[Religion]):
    """Repository for religion data access."""

    def __init__(self, session: Session):
        super().__init__(Religion, session)

    def get_active_religions(self) -> list[Religion]:
        """Get all active religions sorted by name."""
        logger.debug("Querying all active religions")
        statement = select(Religion).where(Religion.is_active).order_by(Religion.name)
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} active religions")
        return results

    def code_exists(
        self, code: str, exclude_religion_id: uuid.UUID | None = None
    ) -> bool:
        """Check if religion code already exists."""
        logger.debug(
            f"Checking if religion code exists: {code}, exclude_id={exclude_religion_id}"
        )
        statement = select(Religion).where(Religion.code == code.upper())
        if exclude_religion_id:
            statement = statement.where(Religion.id != exclude_religion_id)
        exists = self.session.exec(statement).first() is not None
        logger.debug(f"Religion code {code} exists: {exists}")
        return exists

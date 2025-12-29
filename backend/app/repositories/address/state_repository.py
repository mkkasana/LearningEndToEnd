from uuid import UUID

from sqlmodel import Session, select

from app.db_models.address import State
from app.repositories.base import BaseRepository


class StateRepository(BaseRepository[State]):
    """Repository for State data access"""

    def __init__(self, session: Session):
        super().__init__(State, session)

    def get_by_country(self, country_id: UUID) -> list[State]:
        """Get all active states for a specific country, ordered by name"""
        statement = (
            select(State)
            .where(State.country_id == country_id)
            .where(State.is_active)
            .order_by(State.name)
        )
        return list(self.session.exec(statement).all())

    def get_by_code(self, code: str, country_id: UUID) -> State | None:
        """Get state by code within a specific country"""
        statement = select(State).where(
            State.code == code, State.country_id == country_id
        )
        return self.session.exec(statement).first()

    def count_by_country(self, country_id: UUID) -> int:
        """Count states for a specific country"""
        from sqlmodel import func

        statement = (
            select(func.count())
            .select_from(State)
            .where(State.country_id == country_id)
        )
        return self.session.exec(statement).one()

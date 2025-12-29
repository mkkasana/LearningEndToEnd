from uuid import UUID

from sqlmodel import Session, select

from app.db_models.address import District
from app.repositories.base import BaseRepository


class DistrictRepository(BaseRepository[District]):
    """Repository for District data access"""

    def __init__(self, session: Session):
        super().__init__(District, session)

    def get_by_state(self, state_id: UUID) -> list[District]:
        """Get all active districts for a specific state, ordered by name"""
        statement = (
            select(District)
            .where(District.state_id == state_id)
            .where(District.is_active)
            .order_by(District.name)
        )
        return list(self.session.exec(statement).all())

    def get_by_code(self, code: str, state_id: UUID) -> District | None:
        """Get district by code within a specific state"""
        statement = select(District).where(
            District.code == code, District.state_id == state_id
        )
        return self.session.exec(statement).first()

    def count_by_state(self, state_id: UUID) -> int:
        """Count districts for a specific state"""
        from sqlmodel import func

        statement = (
            select(func.count())
            .select_from(District)
            .where(District.state_id == state_id)
        )
        return self.session.exec(statement).one()

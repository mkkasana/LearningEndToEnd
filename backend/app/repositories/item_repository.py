from uuid import UUID

from sqlmodel import Session, func, select

from app.db_models.item import Item
from app.repositories.base import BaseRepository


class ItemRepository(BaseRepository[Item]):
    """Repository for Item data access"""

    def __init__(self, session: Session):
        super().__init__(Item, session)

    def get_by_owner(
        self, owner_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Item]:
        """Get all items for a specific owner"""
        statement = (
            select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
        )
        return list(self.session.exec(statement).all())

    def count_by_owner(self, owner_id: UUID) -> int:
        """Count items for a specific owner"""
        statement = (
            select(func.count()).select_from(Item).where(Item.owner_id == owner_id)
        )
        return self.session.exec(statement).one()

    def delete_by_owner(self, owner_id: UUID) -> None:
        """Delete all items for a specific owner"""
        from sqlmodel import col, delete

        statement = delete(Item).where(col(Item.owner_id) == owner_id)
        self.session.exec(statement)
        self.session.commit()

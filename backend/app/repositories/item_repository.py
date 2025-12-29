import logging
from uuid import UUID

from sqlmodel import Session, func, select

from app.db_models.item import Item
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ItemRepository(BaseRepository[Item]):
    """Repository for Item data access"""

    def __init__(self, session: Session):
        super().__init__(Item, session)

    def get_by_owner(
        self, owner_id: UUID, skip: int = 0, limit: int = 100
    ) -> list[Item]:
        """Get all items for a specific owner"""
        logger.debug(f"Querying items by owner_id: {owner_id}, skip={skip}, limit={limit}")
        statement = (
            select(Item).where(Item.owner_id == owner_id).offset(skip).limit(limit)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} items for owner {owner_id}")
        return results

    def count_by_owner(self, owner_id: UUID) -> int:
        """Count items for a specific owner"""
        logger.debug(f"Counting items for owner: {owner_id}")
        statement = (
            select(func.count()).select_from(Item).where(Item.owner_id == owner_id)
        )
        count = self.session.exec(statement).one()
        logger.debug(f"Owner {owner_id} has {count} items")
        return count

    def delete_by_owner(self, owner_id: UUID) -> None:
        """Delete all items for a specific owner"""
        from sqlmodel import col, delete

        logger.debug(f"Deleting all items for owner: {owner_id}")
        statement = delete(Item).where(col(Item.owner_id) == owner_id)
        self.session.exec(statement)
        self.session.commit()
        logger.debug(f"Deleted all items for owner: {owner_id}")

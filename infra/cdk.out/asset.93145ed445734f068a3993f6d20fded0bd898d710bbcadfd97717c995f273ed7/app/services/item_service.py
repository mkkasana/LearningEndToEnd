import logging
from uuid import UUID

from sqlmodel import Session

from app.db_models.item import Item
from app.db_models.user import User
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate

logger = logging.getLogger(__name__)


class ItemService:
    """Service for item business logic"""

    def __init__(self, session: Session):
        self.session = session
        self.item_repo = ItemRepository(session)

    def get_item_by_id(self, item_id: UUID) -> Item | None:
        """Get item by ID"""
        logger.debug(f"Fetching item by ID: {item_id}")
        item = self.item_repo.get_by_id(item_id)
        if item:
            logger.info(f"Item found: {item.title} (ID: {item.id})")
        else:
            logger.info(f"Item not found: ID {item_id}")
        return item

    def get_items(
        self, user: User, skip: int = 0, limit: int = 100
    ) -> tuple[list[Item], int]:
        """Get paginated items based on user permissions"""
        logger.debug(
            f"Fetching items for user: {user.email} (ID: {user.id}), "
            f"skip={skip}, limit={limit}"
        )
        if user.is_superuser:
            logger.debug("User is superuser, fetching all items")
            items = self.item_repo.get_all(skip=skip, limit=limit)
            count = self.item_repo.count()
        else:
            logger.debug(f"Fetching items owned by user: {user.id}")
            items = self.item_repo.get_by_owner(user.id, skip=skip, limit=limit)
            count = self.item_repo.count_by_owner(user.id)
        logger.info(f"Retrieved {len(items)} items (total: {count})")
        return items, count

    def create_item(self, item_create: ItemCreate, owner_id: UUID) -> Item:
        """Create a new item"""
        logger.info(f"Creating item: {item_create.title} for owner: {owner_id}")
        try:
            item = Item(
                title=item_create.title,
                description=item_create.description,
                owner_id=owner_id,
            )
            created_item = self.item_repo.create(item)
            logger.info(f"Item created: {created_item.title} (ID: {created_item.id})")
            return created_item
        except Exception:
            logger.error(
                f"Failed to create item: {item_create.title} for owner: {owner_id}",
                exc_info=True,
            )
            raise

    def update_item(self, item: Item, item_update: ItemUpdate) -> Item:
        """Update an item"""
        logger.info(f"Updating item: {item.title} (ID: {item.id})")
        try:
            update_data = item_update.model_dump(exclude_unset=True)
            item.sqlmodel_update(update_data)
            updated_item = self.item_repo.update(item)
            logger.info(f"Item updated: {updated_item.title} (ID: {updated_item.id})")
            return updated_item
        except Exception:
            logger.error(
                f"Failed to update item: {item.title} (ID: {item.id})", exc_info=True
            )
            raise

    def delete_item(self, item: Item) -> None:
        """Delete an item"""
        logger.info(f"Deleting item: {item.title} (ID: {item.id})")
        try:
            self.item_repo.delete(item)
            logger.info(f"Item deleted: {item.title} (ID: {item.id})")
        except Exception:
            logger.error(
                f"Failed to delete item: {item.title} (ID: {item.id})", exc_info=True
            )
            raise

    def user_can_access_item(self, user: User, item: Item) -> bool:
        """Check if user has permission to access item"""
        can_access = user.is_superuser or item.owner_id == user.id
        if can_access:
            logger.debug(
                f"User {user.email} (ID: {user.id}) has access to item: "
                f"{item.title} (ID: {item.id})"
            )
        else:
            logger.warning(
                f"User {user.email} (ID: {user.id}) denied access to item: "
                f"{item.title} (ID: {item.id})"
            )
        return can_access

    def delete_items_by_owner(self, owner_id: UUID) -> None:
        """Delete all items for a specific owner"""
        logger.info(f"Deleting all items for owner: {owner_id}")
        try:
            self.item_repo.delete_by_owner(owner_id)
            logger.info(f"All items deleted for owner: {owner_id}")
        except Exception:
            logger.error(f"Failed to delete items for owner: {owner_id}", exc_info=True)
            raise

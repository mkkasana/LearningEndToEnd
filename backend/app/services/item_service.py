from uuid import UUID

from sqlmodel import Session

from app.db_models.item import Item
from app.db_models.user import User
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    """Service for item business logic"""

    def __init__(self, session: Session):
        self.session = session
        self.item_repo = ItemRepository(session)

    def get_item_by_id(self, item_id: UUID) -> Item | None:
        """Get item by ID"""
        return self.item_repo.get_by_id(item_id)

    def get_items(
        self, user: User, skip: int = 0, limit: int = 100
    ) -> tuple[list[Item], int]:
        """Get paginated items based on user permissions"""
        if user.is_superuser:
            items = self.item_repo.get_all(skip=skip, limit=limit)
            count = self.item_repo.count()
        else:
            items = self.item_repo.get_by_owner(user.id, skip=skip, limit=limit)
            count = self.item_repo.count_by_owner(user.id)
        return items, count

    def create_item(self, item_create: ItemCreate, owner_id: UUID) -> Item:
        """Create a new item"""
        item = Item(
            title=item_create.title,
            description=item_create.description,
            owner_id=owner_id,
        )
        return self.item_repo.create(item)

    def update_item(self, item: Item, item_update: ItemUpdate) -> Item:
        """Update an item"""
        update_data = item_update.model_dump(exclude_unset=True)
        item.sqlmodel_update(update_data)
        return self.item_repo.update(item)

    def delete_item(self, item: Item) -> None:
        """Delete an item"""
        self.item_repo.delete(item)

    def user_can_access_item(self, user: User, item: Item) -> bool:
        """Check if user has permission to access item"""
        return user.is_superuser or item.owner_id == user.id

    def delete_items_by_owner(self, owner_id: UUID) -> None:
        """Delete all items for a specific owner"""
        self.item_repo.delete_by_owner(owner_id)

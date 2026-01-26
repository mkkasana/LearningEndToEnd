from uuid import UUID

from sqlmodel import Session

from app.models import Item
from app.schemas.item import ItemCreate
from app.services.item_service import ItemService
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_item(db: Session, owner_id: UUID | None = None) -> Item:
    """Create a random item for testing.
    
    Args:
        db: Database session
        owner_id: Optional owner ID. If not provided, creates a random user as owner.
    
    Returns:
        Created Item instance
    """
    if owner_id is None:
        user = create_random_user(db)
        owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item_in = ItemCreate(title=title, description=description)
    item_service = ItemService(db)
    return item_service.create_item(item_in, owner_id)

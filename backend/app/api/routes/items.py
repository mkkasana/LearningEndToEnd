import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.core.exceptions import PermissionDeniedError, ResourceNotFoundError
from app.schemas.common import Message
from app.schemas.item import ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.services.item_service import ItemService

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
def read_items(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    item_service = ItemService(session)
    items, count = item_service.get_items(current_user, skip=skip, limit=limit)
    return ItemsPublic(data=items, count=count)


@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get item by ID.
    """
    item_service = ItemService(session)
    item = item_service.get_item_by_id(id)
    
    if not item:
        raise ResourceNotFoundError("Item")
    
    if not item_service.user_can_access_item(current_user, item):
        raise PermissionDeniedError()
    
    return item


@router.post("/", response_model=ItemPublic)
def create_item(
    *, session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
) -> Any:
    """
    Create new item.
    """
    item_service = ItemService(session)
    item = item_service.create_item(item_in, current_user.id)
    return item


@router.put("/{id}", response_model=ItemPublic)
def update_item(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    item_in: ItemUpdate,
) -> Any:
    """
    Update an item.
    """
    item_service = ItemService(session)
    item = item_service.get_item_by_id(id)
    
    if not item:
        raise ResourceNotFoundError("Item")
    
    if not item_service.user_can_access_item(current_user, item):
        raise PermissionDeniedError()
    
    item = item_service.update_item(item, item_in)
    return item


@router.delete("/{id}")
def delete_item(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an item.
    """
    item_service = ItemService(session)
    item = item_service.get_item_by_id(id)
    
    if not item:
        raise ResourceNotFoundError("Item")
    
    if not item_service.user_can_access_item(current_user, item):
        raise PermissionDeniedError()
    
    item_service.delete_item(item)
    return Message(message="Item deleted successfully")

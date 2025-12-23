from fastapi import APIRouter

from app.api.routes import auth, items, private, users, utils
from app.api.routes.address import metadata as address_metadata
from app.core.config import settings

api_router = APIRouter()

# Clean architecture routes
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(items.router)
api_router.include_router(utils.router)

# Address metadata routes
api_router.include_router(address_metadata.router, prefix="/metadata")


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)

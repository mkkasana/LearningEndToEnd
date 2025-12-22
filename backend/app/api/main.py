from fastapi import APIRouter

from app.api.routes import auth, items, metadata, private, users, utils
from app.core.config import settings

api_router = APIRouter()

# Clean architecture routes
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(items.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(metadata.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)

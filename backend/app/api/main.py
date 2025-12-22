from fastapi import APIRouter

from app.api.routes import auth, items, items_new, login, private, users, users_new, utils
from app.core.config import settings

api_router = APIRouter()

# New clean architecture routes
api_router.include_router(auth.router)
api_router.include_router(users_new.router, prefix="/v2")  # Temporary v2 prefix for testing
api_router.include_router(items_new.router, prefix="/v2")  # Temporary v2 prefix for testing

# Legacy routes (will be removed after full migration)
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)

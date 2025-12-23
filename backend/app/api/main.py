from fastapi import APIRouter

from app.api.routes import auth, items, private, users, utils
from app.api.routes.address import metadata as address_metadata
from app.api.routes.person import metadata as person_metadata
from app.api.routes.person import person as person_routes
from app.api.routes.religion import metadata as religion_metadata
from app.core.config import settings

api_router = APIRouter()

# Clean architecture routes
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(items.router)
api_router.include_router(utils.router)

# Metadata routes
api_router.include_router(address_metadata.router, prefix="/metadata")
api_router.include_router(religion_metadata.router, prefix="/metadata")
api_router.include_router(person_metadata.router, prefix="/metadata")

# Person routes
api_router.include_router(person_routes.router, prefix="/person", tags=["person"])


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)

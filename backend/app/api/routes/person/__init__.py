"""Person API routes."""

from app.api.routes.person.metadata import router as metadata_router
from app.api.routes.person.person import router as person_router

__all__ = ["metadata_router", "person_router"]

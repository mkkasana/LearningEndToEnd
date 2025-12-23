"""Person schemas."""

from app.schemas.person.gender import (
    GenderCreate,
    GenderDetailPublic,
    GenderPublic,
    GenderUpdate,
)
from app.schemas.person.profession import (
    ProfessionCreate,
    ProfessionDetailPublic,
    ProfessionPublic,
    ProfessionUpdate,
)

__all__ = [
    "GenderCreate",
    "GenderDetailPublic",
    "GenderPublic",
    "GenderUpdate",
    "ProfessionCreate",
    "ProfessionDetailPublic",
    "ProfessionPublic",
    "ProfessionUpdate",
]

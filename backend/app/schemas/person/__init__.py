"""Person schemas."""

from app.schemas.person.gender import (
    GenderCreate,
    GenderDetailPublic,
    GenderPublic,
    GenderUpdate,
)
from app.schemas.person.person import PersonCreate, PersonPublic, PersonUpdate
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
    "PersonCreate",
    "PersonPublic",
    "PersonUpdate",
    "ProfessionCreate",
    "ProfessionDetailPublic",
    "ProfessionPublic",
    "ProfessionUpdate",
]

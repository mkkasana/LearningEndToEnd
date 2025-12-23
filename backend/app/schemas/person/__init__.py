"""Person schemas."""

from app.schemas.person.gender import (
    GenderCreate,
    GenderDetailPublic,
    GenderPublic,
    GenderUpdate,
)
from app.schemas.person.person import PersonCreate, PersonPublic, PersonUpdate
from app.schemas.person.person_address import (
    PersonAddressCreate,
    PersonAddressPublic,
    PersonAddressUpdate,
)
from app.schemas.person.person_profession import (
    PersonProfessionCreate,
    PersonProfessionPublic,
    PersonProfessionUpdate,
)
from app.schemas.person.person_relationship import (
    PersonRelationshipCreate,
    PersonRelationshipPublic,
    PersonRelationshipUpdate,
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
    "PersonAddressCreate",
    "PersonAddressPublic",
    "PersonAddressUpdate",
    "PersonCreate",
    "PersonProfessionCreate",
    "PersonProfessionPublic",
    "PersonProfessionUpdate",
    "PersonPublic",
    "PersonRelationshipCreate",
    "PersonRelationshipPublic",
    "PersonRelationshipUpdate",
    "PersonUpdate",
    "ProfessionCreate",
    "ProfessionDetailPublic",
    "ProfessionPublic",
    "ProfessionUpdate",
]

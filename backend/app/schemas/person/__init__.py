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
from app.schemas.person.person_metadata import (
    PersonMetadataCreate,
    PersonMetadataPublic,
    PersonMetadataUpdate,
)
from app.schemas.person.person_profession import (
    PersonProfessionCreate,
    PersonProfessionPublic,
    PersonProfessionUpdate,
)
from app.schemas.person.person_relationship import (
    PersonDetails,
    PersonRelationshipCreate,
    PersonRelationshipPublic,
    PersonRelationshipsWithDetailsResponse,
    PersonRelationshipUpdate,
    PersonRelationshipWithDetails,
)
from app.schemas.person.person_religion import (
    PersonReligionCreate,
    PersonReligionPublic,
    PersonReligionUpdate,
)
from app.schemas.person.person_contribution import PersonContributionPublic
from app.schemas.person.person_discovery import PersonDiscoveryResult
from app.schemas.person.person_search import PersonMatchResult, PersonSearchRequest
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
    "PersonContributionPublic",
    "PersonCreate",
    "PersonDetails",
    "PersonDiscoveryResult",
    "PersonMatchResult",
    "PersonMetadataCreate",
    "PersonMetadataPublic",
    "PersonMetadataUpdate",
    "PersonProfessionCreate",
    "PersonProfessionPublic",
    "PersonProfessionUpdate",
    "PersonPublic",
    "PersonRelationshipCreate",
    "PersonRelationshipPublic",
    "PersonRelationshipUpdate",
    "PersonRelationshipWithDetails",
    "PersonRelationshipsWithDetailsResponse",
    "PersonReligionCreate",
    "PersonReligionPublic",
    "PersonReligionUpdate",
    "PersonSearchRequest",
    "PersonUpdate",
    "ProfessionCreate",
    "ProfessionDetailPublic",
    "ProfessionPublic",
    "ProfessionUpdate",
]

"""Person repositories."""

from app.repositories.person.gender_repository import GenderRepository
from app.repositories.person.person_address_repository import PersonAddressRepository
from app.repositories.person.person_metadata_repository import PersonMetadataRepository
from app.repositories.person.person_profession_repository import (
    PersonProfessionRepository,
)
from app.repositories.person.person_relationship_repository import (
    PersonRelationshipRepository,
)
from app.repositories.person.person_repository import PersonRepository
from app.repositories.person.profession_repository import ProfessionRepository

__all__ = [
    "GenderRepository",
    "PersonAddressRepository",
    "PersonMetadataRepository",
    "PersonProfessionRepository",
    "PersonRelationshipRepository",
    "PersonRepository",
    "ProfessionRepository",
]

"""Person repositories."""

from app.repositories.person.gender_repository import GenderRepository
from app.repositories.person.person_address_repository import PersonAddressRepository
from app.repositories.person.person_profession_repository import (
    PersonProfessionRepository,
)
from app.repositories.person.person_repository import PersonRepository
from app.repositories.person.profession_repository import ProfessionRepository

__all__ = [
    "GenderRepository",
    "PersonAddressRepository",
    "PersonProfessionRepository",
    "PersonRepository",
    "ProfessionRepository",
]

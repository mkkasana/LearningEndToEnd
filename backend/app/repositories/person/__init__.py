"""Person repositories."""

from app.repositories.person.gender_repository import GenderRepository
from app.repositories.person.person_repository import PersonRepository
from app.repositories.person.profession_repository import ProfessionRepository

__all__ = ["GenderRepository", "PersonRepository", "ProfessionRepository"]

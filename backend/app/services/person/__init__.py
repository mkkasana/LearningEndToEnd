"""Person services."""

from app.services.person.gender_service import GenderService
from app.services.person.person_service import PersonService
from app.services.person.profession_service import ProfessionService

__all__ = ["GenderService", "PersonService", "ProfessionService"]

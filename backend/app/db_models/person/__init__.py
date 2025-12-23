"""Person database models."""

from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.db_models.person.profession import Profession

__all__ = ["Gender", "Person", "Profession"]

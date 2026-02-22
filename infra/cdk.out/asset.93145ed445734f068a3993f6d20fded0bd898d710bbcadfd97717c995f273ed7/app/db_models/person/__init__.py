"""Person database models."""

from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_attachment_request import PersonAttachmentRequest
from app.db_models.person.person_life_event import PersonLifeEvent
from app.db_models.person.person_metadata import PersonMetadata
from app.db_models.person.person_profession import PersonProfession
from app.db_models.person.person_relationship import PersonRelationship
from app.db_models.person.person_religion import PersonReligion
from app.db_models.person.profession import Profession

__all__ = [
    "Gender",
    "Person",
    "PersonAddress",
    "PersonAttachmentRequest",
    "PersonLifeEvent",
    "PersonMetadata",
    "PersonProfession",
    "PersonRelationship",
    "PersonReligion",
    "Profession",
]

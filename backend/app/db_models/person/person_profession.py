"""Person Profession association database model."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel


class PersonProfession(SQLModel, table=True):
    """Person Profession model - Associates persons with professions over time."""

    __tablename__ = "person_profession_association"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    person_id: uuid.UUID = Field(
        foreign_key="person.user_id", index=True, description="Person reference"
    )
    profession_id: uuid.UUID = Field(
        foreign_key="person_profession.id", description="Profession reference"
    )
    start_date: date = Field(description="Profession start date")
    end_date: date | None = Field(default=None, description="Profession end date")
    is_current: bool = Field(default=False, description="Is this the current profession")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

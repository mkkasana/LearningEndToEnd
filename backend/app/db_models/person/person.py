"""Person database model."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel


class Person(SQLModel, table=True):
    """Person model - Core person information linked to user account."""

    __tablename__ = "person"

    user_id: uuid.UUID = Field(
        foreign_key="user.id", primary_key=True, description="User account reference"
    )
    first_name: str = Field(max_length=100, description="First name")
    middle_name: str | None = Field(
        default=None, max_length=100, description="Middle name"
    )
    last_name: str = Field(max_length=100, description="Last name")
    gender_id: uuid.UUID = Field(
        foreign_key="person_gender.id", description="Gender reference"
    )
    date_of_birth: date = Field(description="Date of birth")
    date_of_death: date | None = Field(default=None, description="Date of death")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

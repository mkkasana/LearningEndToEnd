"""Person database model."""

import uuid
from datetime import date, datetime

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

from app.enums.marital_status import MaritalStatus


class Person(SQLModel, table=True):
    """Person model - Core person information. Can be linked to a user or standalone for family tree."""

    __tablename__ = "person"

    # Primary key - unique identifier for each person
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique person identifier",
    )

    # Optional link to user account (nullable for family members without accounts)
    user_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="user.id",
        index=True,
        description="User account reference (nullable for non-users)",
    )

    # Track who created this person record
    created_by_user_id: uuid.UUID = Field(
        foreign_key="user.id",
        index=True,
        description="User who created this person record",
    )

    # Is this the primary person for the user account?
    is_primary: bool = Field(
        default=False, description="Is this the primary person for the user account"
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
    marital_status: MaritalStatus = Field(
        default=MaritalStatus.UNKNOWN,
        sa_column=sa.Column(
            sa.String(20),
            nullable=False,
            default="unknown",
        ),
        description="Person's marital status",
    )
    is_active: bool = Field(
        default=True,
        description="Whether person is active and visible in searches",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

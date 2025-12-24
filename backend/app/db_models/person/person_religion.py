"""Person Religion association database model."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class PersonReligion(SQLModel, table=True):
    """Person Religion model - Associates person with religion details."""

    __tablename__ = "person_religion"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    person_id: uuid.UUID = Field(
        foreign_key="person.user_id", index=True, unique=True, description="Person reference"
    )
    religion_id: uuid.UUID = Field(
        foreign_key="religion.id", description="Religion reference"
    )
    religion_category_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="religion_category.id",
        description="Religion category reference",
    )
    religion_sub_category_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="religion_sub_category.id",
        description="Religion sub-category reference",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )

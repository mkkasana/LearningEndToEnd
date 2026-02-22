"""Person contribution schemas."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel


class PersonContributionPublic(SQLModel):
    """Schema for person contribution with statistics."""

    id: uuid.UUID = Field(description="Person ID")
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    date_of_birth: date = Field(description="Date of birth")
    date_of_death: date | None = Field(default=None, description="Date of death")
    is_active: bool = Field(description="Whether the person is active")
    address: str = Field(description="Formatted address string")
    total_views: int = Field(description="Total profile view count")
    created_at: datetime = Field(description="Record creation timestamp")

"""Person discovery schemas for family member suggestions."""

import uuid
from datetime import date

from sqlmodel import Field, SQLModel


class PersonDiscoveryResult(SQLModel):
    """Result of family member discovery.

    Represents a person who is connected to the user's family members
    but not yet directly connected to the user, along with metadata
    about the inferred relationship and connection path.
    """

    # Person identification
    person_id: uuid.UUID = Field(description="Person ID")

    # Person details
    first_name: str = Field(description="First name")
    middle_name: str | None = Field(default=None, description="Middle name")
    last_name: str = Field(description="Last name")
    date_of_birth: date = Field(description="Date of birth")
    date_of_death: date | None = Field(default=None, description="Date of death")
    gender_id: uuid.UUID = Field(description="Gender ID")

    # Address information
    address_display: str | None = Field(
        default=None, description="Comma-separated address display string"
    )

    # Religion information
    religion_display: str | None = Field(
        default=None, description="Comma-separated religion display string"
    )

    # Discovery metadata
    inferred_relationship_type: str = Field(
        description="Relationship type ID (e.g., 'rel-6a0ede824d104' for Son)"
    )
    inferred_relationship_label: str = Field(
        description="Human-readable relationship label (e.g., 'Son', 'Daughter')"
    )
    connection_path: str = Field(
        description="Human-readable explanation of connection (e.g., 'Connected to your spouse Maria Garcia')"
    )

    # Sorting metadata
    proximity_score: int = Field(
        description="Relationship proximity (1 = direct connection, 2 = 2 degrees, etc.)"
    )
    relationship_priority: int = Field(
        description="Relationship type priority (1 = children, 2 = parents, 3 = spouses)"
    )

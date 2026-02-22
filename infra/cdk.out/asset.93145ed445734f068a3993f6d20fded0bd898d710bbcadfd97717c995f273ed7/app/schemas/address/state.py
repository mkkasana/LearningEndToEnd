import uuid

from sqlmodel import Field, SQLModel


class StateBase(SQLModel):
    """Base state properties"""

    name: str = Field(max_length=255, description="State name")
    code: str | None = Field(default=None, max_length=10, description="State code")
    is_active: bool = Field(default=True, description="Whether state is active")


class StateCreate(StateBase):
    """Schema for creating a new state"""

    country_id: uuid.UUID = Field(description="Country ID this state belongs to")


class StateUpdate(SQLModel):
    """Schema for updating a state (all fields optional)"""

    name: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=10)
    is_active: bool | None = None


class StatePublic(SQLModel):
    """State response schema for public API"""

    stateId: uuid.UUID
    stateName: str


class StateDetailPublic(StateBase):
    """Detailed state response with all fields"""

    id: uuid.UUID
    country_id: uuid.UUID


class StatesPublic(SQLModel):
    """List of states response"""

    data: list[StatePublic]

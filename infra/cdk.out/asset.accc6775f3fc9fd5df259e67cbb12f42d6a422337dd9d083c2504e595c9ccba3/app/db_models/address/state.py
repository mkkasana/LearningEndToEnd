import uuid

from sqlmodel import Field, SQLModel


class State(SQLModel, table=True):
    """State database model for metadata"""

    __tablename__ = "address_state"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    code: str | None = Field(default=None, max_length=10)  # State code (optional)
    country_id: uuid.UUID = Field(foreign_key="address_country.id", index=True)
    is_active: bool = Field(default=True)

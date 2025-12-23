import uuid

from sqlmodel import Field, SQLModel


class District(SQLModel, table=True):
    """District database model for metadata"""

    __tablename__ = "address_district"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    code: str | None = Field(default=None, max_length=10)  # District code (optional)
    state_id: uuid.UUID = Field(foreign_key="address_state.id", index=True)
    is_active: bool = Field(default=True)

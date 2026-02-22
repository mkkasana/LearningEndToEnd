import uuid

from sqlmodel import Field, SQLModel


class Country(SQLModel, table=True):
    """Country database model for metadata"""

    __tablename__ = "address_country"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True)
    code: str = Field(max_length=3, unique=True, index=True)  # ISO country code
    is_active: bool = Field(default=True)

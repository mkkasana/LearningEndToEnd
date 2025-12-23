import uuid

from sqlmodel import Field, SQLModel


class Locality(SQLModel, table=True):
    """Locality (Village/Locality) database model for metadata"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    code: str | None = Field(default=None, max_length=10)  # Locality code (optional)
    sub_district_id: uuid.UUID = Field(foreign_key="subdistrict.id", index=True)
    is_active: bool = Field(default=True)

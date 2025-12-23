import uuid

from sqlmodel import Field, SQLModel


class LocalityBase(SQLModel):
    """Base locality properties"""

    name: str = Field(max_length=255, description="Locality/Village name")
    code: str | None = Field(default=None, max_length=10, description="Locality code")
    is_active: bool = Field(default=True, description="Whether locality is active")


class LocalityCreate(LocalityBase):
    """Schema for creating a new locality"""

    sub_district_id: uuid.UUID = Field(
        description="Sub-district ID this locality belongs to"
    )


class LocalityUpdate(SQLModel):
    """Schema for updating a locality (all fields optional)"""

    name: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=10)
    is_active: bool | None = None


class LocalityPublic(SQLModel):
    """Locality response schema for public API"""

    localityId: uuid.UUID
    localityName: str


class LocalityDetailPublic(LocalityBase):
    """Detailed locality response with all fields"""

    id: uuid.UUID
    sub_district_id: uuid.UUID


class LocalitiesPublic(SQLModel):
    """List of localities response"""

    data: list[LocalityPublic]

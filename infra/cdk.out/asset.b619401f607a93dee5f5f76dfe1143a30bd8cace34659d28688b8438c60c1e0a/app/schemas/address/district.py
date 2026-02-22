import uuid

from sqlmodel import Field, SQLModel


class DistrictBase(SQLModel):
    """Base district properties"""

    name: str = Field(max_length=255, description="District name")
    code: str | None = Field(default=None, max_length=10, description="District code")
    is_active: bool = Field(default=True, description="Whether district is active")


class DistrictCreate(DistrictBase):
    """Schema for creating a new district"""

    state_id: uuid.UUID = Field(description="State ID this district belongs to")


class DistrictUpdate(SQLModel):
    """Schema for updating a district (all fields optional)"""

    name: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=10)
    is_active: bool | None = None


class DistrictPublic(SQLModel):
    """District response schema for public API"""

    districtId: uuid.UUID
    districtName: str


class DistrictDetailPublic(DistrictBase):
    """Detailed district response with all fields"""

    id: uuid.UUID
    state_id: uuid.UUID


class DistrictsPublic(SQLModel):
    """List of districts response"""

    data: list[DistrictPublic]

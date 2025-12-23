import uuid

from sqlmodel import Field, SQLModel


class SubDistrictBase(SQLModel):
    """Base sub-district properties"""

    name: str = Field(max_length=255, description="Sub-district/Tehsil name")
    code: str | None = Field(default=None, max_length=10, description="Sub-district code")
    is_active: bool = Field(default=True, description="Whether sub-district is active")


class SubDistrictCreate(SubDistrictBase):
    """Schema for creating a new sub-district"""

    district_id: uuid.UUID = Field(description="District ID this sub-district belongs to")


class SubDistrictUpdate(SQLModel):
    """Schema for updating a sub-district (all fields optional)"""

    name: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=10)
    is_active: bool | None = None


class SubDistrictPublic(SQLModel):
    """Sub-district response schema for public API"""

    tehsilId: uuid.UUID
    tehsilName: str


class SubDistrictDetailPublic(SubDistrictBase):
    """Detailed sub-district response with all fields"""

    id: uuid.UUID
    district_id: uuid.UUID


class SubDistrictsPublic(SQLModel):
    """List of sub-districts response"""

    data: list[SubDistrictPublic]

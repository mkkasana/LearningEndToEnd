import uuid

from sqlmodel import Field, SQLModel


class CountryBase(SQLModel):
    """Base country properties"""

    name: str = Field(max_length=255, description="Country name")
    code: str = Field(max_length=3, description="ISO country code (3 letters)")
    is_active: bool = Field(default=True, description="Whether country is active")


class CountryCreate(CountryBase):
    """Schema for creating a new country"""

    pass


class CountryUpdate(SQLModel):
    """Schema for updating a country (all fields optional)"""

    name: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=3)
    is_active: bool | None = None


class CountryPublic(SQLModel):
    """Country response schema"""

    countryId: uuid.UUID
    countryName: str


class CountryDetailPublic(CountryBase):
    """Detailed country response with all fields"""

    id: uuid.UUID


class CountriesPublic(SQLModel):
    """List of countries response"""

    data: list[CountryPublic]

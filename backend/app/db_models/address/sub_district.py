import uuid

from sqlmodel import Field, SQLModel


class SubDistrict(SQLModel, table=True):
    """Sub-district (Tehsil/County) database model for metadata"""

    __tablename__ = "address_sub_district"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    code: str | None = Field(default=None, max_length=10)  # Sub-district code (optional)
    district_id: uuid.UUID = Field(foreign_key="address_district.id", index=True)
    is_active: bool = Field(default=True)

"""Person Complete Details schemas for the Person Details Panel."""

import uuid
from datetime import date

from sqlmodel import SQLModel


class PersonAddressDetails(SQLModel):
    """Address details with resolved location names."""

    locality_name: str | None = None
    sub_district_name: str | None = None
    district_name: str | None = None
    state_name: str | None = None
    country_name: str
    address_line: str | None = None


class PersonReligionDetails(SQLModel):
    """Religion details with resolved names."""

    religion_name: str
    category_name: str | None = None
    sub_category_name: str | None = None


class PersonCompleteDetailsResponse(SQLModel):
    """Complete person details with resolved names."""

    id: uuid.UUID
    first_name: str
    middle_name: str | None = None
    last_name: str
    date_of_birth: date
    date_of_death: date | None = None
    gender_name: str
    address: PersonAddressDetails | None = None
    religion: PersonReligionDetails | None = None

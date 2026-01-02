"""Gender enum with hardcoded values matching database records."""

import uuid
from enum import Enum
from typing import NamedTuple


class GenderData(NamedTuple):
    """Gender data structure."""

    id: uuid.UUID
    name: str
    code: str
    description: str
    is_active: bool


class GenderEnum(str, Enum):
    """Gender enum codes."""

    MALE = "MALE"
    FEMALE = "FEMALE"


# Hardcoded gender data matching database records
# These UUIDs must match the existing database entries
GENDER_DATA: dict[GenderEnum, GenderData] = {
    GenderEnum.MALE: GenderData(
        id=uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83"),
        name="Male",
        code="MALE",
        description="Male gender",
        is_active=True,
    ),
    GenderEnum.FEMALE: GenderData(
        id=uuid.UUID("691fde27-f82c-4a84-832f-4243acef4b95"),
        name="Female",
        code="FEMALE",
        description="Female gender",
        is_active=True,
    ),
}

# Lookup maps for quick access
GENDER_BY_ID: dict[uuid.UUID, GenderData] = {
    data.id: data for data in GENDER_DATA.values()
}
GENDER_BY_CODE: dict[str, GenderData] = {
    data.code: data for data in GENDER_DATA.values()
}


def get_gender_by_id(gender_id: uuid.UUID) -> GenderData | None:
    """Get gender data by ID."""
    return GENDER_BY_ID.get(gender_id)


def get_gender_by_code(code: str) -> GenderData | None:
    """Get gender data by code."""
    return GENDER_BY_CODE.get(code.upper())


def get_all_genders() -> list[GenderData]:
    """Get all active genders."""
    return [data for data in GENDER_DATA.values() if data.is_active]


def get_gender_mapping() -> dict[uuid.UUID, str]:
    """Get mapping of gender_id to gender code for relationship helper."""
    return {data.id: data.code for data in GENDER_DATA.values()}

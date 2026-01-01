"""Gender service - returns hardcoded gender data (no database calls)."""

import uuid

from app.enums import (
    GenderData,
    get_all_genders,
    get_gender_by_code as _get_gender_by_code,
    get_gender_by_id as _get_gender_by_id,
)
from app.schemas.person import GenderDetailPublic, GenderPublic


class GenderService:
    """Service for gender business logic using hardcoded enum values."""

    def __init__(self, session=None):
        """Initialize service. Session parameter kept for API compatibility but not used."""
        pass

    def get_genders(self) -> list[GenderPublic]:
        """Get all active genders from hardcoded enum."""
        genders = get_all_genders()
        return [
            GenderPublic(genderId=g.id, genderName=g.name, genderCode=g.code)
            for g in genders
        ]

    def get_gender_by_id(self, gender_id: uuid.UUID) -> GenderDetailPublic | None:
        """Get gender by ID from hardcoded enum."""
        gender = _get_gender_by_id(gender_id)
        if gender:
            return GenderDetailPublic(
                id=gender.id,
                name=gender.name,
                code=gender.code,
                description=gender.description,
                is_active=gender.is_active,
            )
        return None

    def get_gender_by_code(self, code: str) -> GenderData | None:
        """Get gender by code from hardcoded enum."""
        return _get_gender_by_code(code)

    def code_exists(
        self, code: str, exclude_gender_id: uuid.UUID | None = None
    ) -> bool:
        """Check if gender code exists in hardcoded enum."""
        gender = _get_gender_by_code(code)
        if gender is None:
            return False
        if exclude_gender_id and gender.id == exclude_gender_id:
            return False
        return True

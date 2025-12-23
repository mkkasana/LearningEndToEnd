"""Religion domain schemas."""

from app.schemas.religion.religion import (
    ReligionCreate,
    ReligionDetailPublic,
    ReligionPublic,
    ReligionUpdate,
)
from app.schemas.religion.religion_category import (
    ReligionCategoryCreate,
    ReligionCategoryDetailPublic,
    ReligionCategoryPublic,
    ReligionCategoryUpdate,
)
from app.schemas.religion.religion_sub_category import (
    ReligionSubCategoryCreate,
    ReligionSubCategoryDetailPublic,
    ReligionSubCategoryPublic,
    ReligionSubCategoryUpdate,
)

__all__ = [
    "ReligionCreate",
    "ReligionUpdate",
    "ReligionPublic",
    "ReligionDetailPublic",
    "ReligionCategoryCreate",
    "ReligionCategoryUpdate",
    "ReligionCategoryPublic",
    "ReligionCategoryDetailPublic",
    "ReligionSubCategoryCreate",
    "ReligionSubCategoryUpdate",
    "ReligionSubCategoryPublic",
    "ReligionSubCategoryDetailPublic",
]

"""Religion domain repositories."""

from app.repositories.religion.religion_category_repository import ReligionCategoryRepository
from app.repositories.religion.religion_repository import ReligionRepository
from app.repositories.religion.religion_sub_category_repository import (
    ReligionSubCategoryRepository,
)

__all__ = [
    "ReligionRepository",
    "ReligionCategoryRepository",
    "ReligionSubCategoryRepository",
]

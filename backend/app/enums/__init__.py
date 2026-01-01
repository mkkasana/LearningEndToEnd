"""Application enums."""

from app.enums.gender import (
    GENDER_BY_CODE,
    GENDER_BY_ID,
    GENDER_DATA,
    GenderData,
    GenderEnum,
    get_all_genders,
    get_gender_by_code,
    get_gender_by_id,
    get_gender_mapping,
)
from app.enums.relationship_type import (
    RelationshipType,
    label_id_relation,
    relation_label_id,
)
from app.enums.user_role import UserRole

__all__ = [
    "GenderData",
    "GenderEnum",
    "GENDER_BY_CODE",
    "GENDER_BY_ID",
    "GENDER_DATA",
    "RelationshipType",
    "UserRole",
    "get_all_genders",
    "get_gender_by_code",
    "get_gender_by_id",
    "get_gender_mapping",
    "label_id_relation",
    "relation_label_id",
]

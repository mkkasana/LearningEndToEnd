"""Application enums."""

from app.enums.attachment_request_status import AttachmentRequestStatus
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
from app.enums.marital_status import MaritalStatus
from app.enums.relationship_type import (
    RelationshipType,
    label_id_relation,
    relation_label_id,
)
from app.enums.user_role import UserRole

__all__ = [
    "AttachmentRequestStatus",
    "GenderData",
    "GenderEnum",
    "GENDER_BY_CODE",
    "GENDER_BY_ID",
    "GENDER_DATA",
    "MaritalStatus",
    "RelationshipType",
    "UserRole",
    "get_all_genders",
    "get_gender_by_code",
    "get_gender_by_id",
    "get_gender_mapping",
    "label_id_relation",
    "relation_label_id",
]

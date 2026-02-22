"""Relationship Type enum."""

from enum import Enum


class RelationshipType(str, Enum):
    """Relationship types between persons with unique identifiers."""

    FATHER = "rel-6a0ede824d101"
    MOTHER = "rel-6a0ede824d102"
    DAUGHTER = "rel-6a0ede824d103"
    SON = "rel-6a0ede824d104"
    WIFE = "rel-6a0ede824d105"
    HUSBAND = "rel-6a0ede824d106"
    SPOUSE = "rel-6a0ede824d107"

    @property
    def label(self) -> str:
        """Get human-readable label for the relationship type."""
        return _LABEL_ID_RELATION.get(self.value, self.value)

    @classmethod
    def from_label(cls, label: str) -> "RelationshipType | None":
        """Get RelationshipType from label."""
        relation_id = _RELATION_LABEL_ID.get(label)
        if relation_id:
            return cls(relation_id)
        return None

    @classmethod
    def get_all_labels(cls) -> dict[str, str]:
        """Get all relationship labels with their IDs."""
        return _LABEL_ID_RELATION.copy()


# Mapping: ID -> Label
_LABEL_ID_RELATION = {
    "rel-6a0ede824d101": "Father",
    "rel-6a0ede824d102": "Mother",
    "rel-6a0ede824d103": "Daughter",
    "rel-6a0ede824d104": "Son",
    "rel-6a0ede824d105": "Wife",
    "rel-6a0ede824d106": "Husband",
    "rel-6a0ede824d107": "Spouse",
}

# Mapping: Label -> ID
_RELATION_LABEL_ID = {v: k for k, v in _LABEL_ID_RELATION.items()}


def label_id_relation() -> dict[str, str]:
    """Get mapping of relationship IDs to labels."""
    return _LABEL_ID_RELATION.copy()


def relation_label_id() -> dict[str, str]:
    """Get mapping of relationship labels to IDs."""
    return _RELATION_LABEL_ID.copy()

"""Marital status enum for person records."""

from enum import Enum


class MaritalStatus(str, Enum):
    """Marital status options for a person."""

    UNKNOWN = "unknown"
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    SEPARATED = "separated"

    @property
    def label(self) -> str:
        """Get human-readable label."""
        return _MARITAL_STATUS_LABELS.get(self.value, self.value.title())

    @classmethod
    def get_selectable_options(cls) -> list["MaritalStatus"]:
        """Get options that users can select (excludes UNKNOWN)."""
        return [status for status in cls if status != cls.UNKNOWN]


_MARITAL_STATUS_LABELS = {
    "unknown": "Unknown",
    "single": "Single",
    "married": "Married",
    "divorced": "Divorced",
    "widowed": "Widowed",
    "separated": "Separated",
}

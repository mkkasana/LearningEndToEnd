"""Attachment request status enum for person attachment requests."""

from enum import Enum


class AttachmentRequestStatus(str, Enum):
    """Status options for person attachment requests."""

    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"

    @property
    def label(self) -> str:
        """Get human-readable label."""
        return _ATTACHMENT_REQUEST_STATUS_LABELS.get(self.value, self.value.title())


_ATTACHMENT_REQUEST_STATUS_LABELS = {
    "pending": "Pending",
    "approved": "Approved",
    "denied": "Denied",
    "cancelled": "Cancelled",
}

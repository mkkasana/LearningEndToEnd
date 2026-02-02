"""Attachment request repository."""

import logging
import uuid

from sqlmodel import Session, desc, func, select

from app.db_models.person.person_attachment_request import PersonAttachmentRequest
from app.enums.attachment_request_status import AttachmentRequestStatus
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class AttachmentRequestRepository(BaseRepository[PersonAttachmentRequest]):
    """Repository for PersonAttachmentRequest data access."""

    def __init__(self, session: Session):
        super().__init__(PersonAttachmentRequest, session)

    def get_pending_by_requester(
        self, user_id: uuid.UUID
    ) -> PersonAttachmentRequest | None:
        """Get pending request for a requester (only one allowed at a time).

        Args:
            user_id: The requester's user ID

        Returns:
            The pending attachment request if one exists, None otherwise
        """
        logger.debug(f"Querying pending request for requester: {user_id}")
        statement = select(PersonAttachmentRequest).where(
            PersonAttachmentRequest.requester_user_id == user_id,
            PersonAttachmentRequest.status == AttachmentRequestStatus.PENDING,
        )
        result = self.session.exec(statement).first()
        logger.debug(
            f"Found pending request for requester {user_id}: {result is not None}"
        )
        return result

    def get_pending_by_approver(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[PersonAttachmentRequest]:
        """Get all pending requests for an approver.

        Args:
            user_id: The approver's user ID
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return

        Returns:
            List of pending attachment requests for the approver
        """
        logger.debug(
            f"Querying pending requests for approver: {user_id}, skip={skip}, limit={limit}"
        )
        statement = (
            select(PersonAttachmentRequest)
            .where(
                PersonAttachmentRequest.approver_user_id == user_id,
                PersonAttachmentRequest.status == AttachmentRequestStatus.PENDING,
            )
            .order_by(desc(PersonAttachmentRequest.created_at))
            .offset(skip)
            .limit(limit)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Found {len(results)} pending requests for approver {user_id}")
        return results

    def count_pending_by_approver(self, user_id: uuid.UUID) -> int:
        """Count pending requests for an approver (for badge display).

        Args:
            user_id: The approver's user ID

        Returns:
            Number of pending attachment requests for the approver
        """
        logger.debug(f"Counting pending requests for approver: {user_id}")
        statement = (
            select(func.count())
            .select_from(PersonAttachmentRequest)
            .where(
                PersonAttachmentRequest.approver_user_id == user_id,
                PersonAttachmentRequest.status == AttachmentRequestStatus.PENDING,
            )
        )
        count = self.session.exec(statement).one()
        logger.debug(f"Approver {user_id} has {count} pending requests")
        return count

    def get_by_target_person(
        self, target_person_id: uuid.UUID, status: AttachmentRequestStatus | None = None
    ) -> list[PersonAttachmentRequest]:
        """Get all requests for a specific target person.

        Args:
            target_person_id: The target person's ID
            status: Optional status filter

        Returns:
            List of attachment requests for the target person
        """
        logger.debug(
            f"Querying requests for target person: {target_person_id}, status={status}"
        )
        statement = select(PersonAttachmentRequest).where(
            PersonAttachmentRequest.target_person_id == target_person_id
        )

        if status is not None:
            statement = statement.where(PersonAttachmentRequest.status == status)

        statement = statement.order_by(desc(PersonAttachmentRequest.created_at))
        results = list(self.session.exec(statement).all())
        logger.debug(
            f"Found {len(results)} requests for target person {target_person_id}"
        )
        return results

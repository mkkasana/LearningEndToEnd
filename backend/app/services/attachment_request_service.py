"""Attachment request service."""

import logging
import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import Session

from app.db_models.person.person_attachment_request import PersonAttachmentRequest
from app.enums import get_gender_by_id
from app.enums.attachment_request_status import AttachmentRequestStatus
from app.repositories.attachment_request_repository import AttachmentRequestRepository
from app.repositories.person.life_event_repository import LifeEventRepository
from app.repositories.person.person_address_repository import PersonAddressRepository
from app.repositories.person.person_metadata_repository import PersonMetadataRepository
from app.repositories.person.person_profession_repository import (
    PersonProfessionRepository,
)
from app.repositories.person.person_relationship_repository import (
    PersonRelationshipRepository,
)
from app.repositories.person.person_religion_repository import PersonReligionRepository
from app.repositories.person.person_repository import PersonRepository
from app.repositories.user_repository import UserRepository
from app.schemas.attachment_request import (
    AttachmentRequestCreate,
    AttachmentRequestWithDetails,
    MyPendingRequestResponse,
)
from app.services.person.person_address_service import PersonAddressService
from app.services.person.person_religion_service import PersonReligionService

logger = logging.getLogger(__name__)


class AttachmentRequestService:
    """Service for attachment request business logic."""

    def __init__(self, session: Session):
        self.session = session
        self.request_repo = AttachmentRequestRepository(session)
        self.person_repo = PersonRepository(session)
        self.user_repo = UserRepository(session)

    def create_request(
        self, requester_user_id: uuid.UUID, request_in: AttachmentRequestCreate
    ) -> PersonAttachmentRequest:
        """
        Create a new attachment request.

        Validations:
        - Requester must have a person record
        - Requester cannot have existing pending request
        - Target person must exist and have no user_id
        - Target person must not be created by requester
        """
        logger.info(
            f"Creating attachment request: requester={requester_user_id}, "
            f"target_person={request_in.target_person_id}"
        )

        # 1. Get requester's person record
        requester_person = self.person_repo.get_by_user_id(requester_user_id)
        if not requester_person:
            logger.warning(
                f"Requester {requester_user_id} does not have a person record"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You must complete your profile before creating an attachment request",
            )

        # 2. Check for existing pending request
        existing_request = self.request_repo.get_pending_by_requester(requester_user_id)
        if existing_request:
            logger.warning(
                f"Requester {requester_user_id} already has a pending request"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a pending attachment request",
            )

        # 3. Get target person
        target_person = self.person_repo.get_by_id(request_in.target_person_id)
        if not target_person:
            logger.warning(f"Target person {request_in.target_person_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Person not found",
            )

        # 4. Check target person doesn't have a user linked
        if target_person.user_id is not None:
            logger.warning(
                f"Target person {request_in.target_person_id} already has a user linked"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This person is already linked to a user account",
            )

        # 5. Check target person wasn't created by requester
        if target_person.created_by_user_id == requester_user_id:
            logger.warning(
                f"Requester {requester_user_id} cannot attach to their own creation"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot attach to a person you created",
            )

        # 6. Create the attachment request
        attachment_request = PersonAttachmentRequest(
            requester_user_id=requester_user_id,
            requester_person_id=requester_person.id,
            target_person_id=target_person.id,
            approver_user_id=target_person.created_by_user_id,
            status=AttachmentRequestStatus.PENDING,
        )

        created_request = self.request_repo.create(attachment_request)
        logger.info(
            f"Attachment request created: ID={created_request.id}, "
            f"requester={requester_user_id}, target={target_person.id}, "
            f"approver={target_person.created_by_user_id}"
        )
        return created_request

    def get_requests_to_approve(
        self, approver_user_id: uuid.UUID
    ) -> list[AttachmentRequestWithDetails]:
        """Get all pending requests for approver with full details."""
        logger.info(f"Fetching requests to approve for user: {approver_user_id}")

        requests = self.request_repo.get_pending_by_approver(approver_user_id)
        logger.debug(f"Found {len(requests)} pending requests for approver")

        results = []
        for request in requests:
            details = self._build_request_with_details(request)
            if details:
                results.append(details)

        logger.info(
            f"Returning {len(results)} requests with details for approver {approver_user_id}"
        )
        return results

    def get_my_pending_request(
        self, requester_user_id: uuid.UUID
    ) -> MyPendingRequestResponse | None:
        """Get requester's pending request with target details."""
        logger.info(f"Fetching pending request for requester: {requester_user_id}")

        request = self.request_repo.get_pending_by_requester(requester_user_id)
        if not request:
            logger.debug(f"No pending request found for requester {requester_user_id}")
            return None

        # Get target person details
        target_person = self.person_repo.get_by_id(request.target_person_id)
        if not target_person:
            logger.warning(
                f"Target person {request.target_person_id} not found for request {request.id}"
            )
            return None

        # Get gender name
        gender_name = "Unknown"
        if target_person.gender_id:
            gender = get_gender_by_id(target_person.gender_id)
            if gender:
                gender_name = gender.name

        response = MyPendingRequestResponse(
            id=request.id,
            status=request.status,
            created_at=request.created_at,
            target_first_name=target_person.first_name,
            target_middle_name=target_person.middle_name,
            target_last_name=target_person.last_name,
            target_date_of_birth=target_person.date_of_birth,
            target_gender=gender_name,
        )

        logger.info(f"Returning pending request {request.id} for requester")
        return response

    def get_pending_count(self, approver_user_id: uuid.UUID) -> int:
        """Get count of pending requests for badge display."""
        logger.debug(f"Counting pending requests for approver: {approver_user_id}")
        count = self.request_repo.count_pending_by_approver(approver_user_id)
        logger.debug(f"Approver {approver_user_id} has {count} pending requests")
        return count

    def _build_request_with_details(
        self, request: PersonAttachmentRequest
    ) -> AttachmentRequestWithDetails | None:
        """Build request with full requester and target details."""
        # Validate required IDs are present
        if request.requester_person_id is None:
            logger.warning(f"Request {request.id} has no requester_person_id")
            return None

        # Get requester person
        requester_person = self.person_repo.get_by_id(request.requester_person_id)
        if not requester_person:
            logger.warning(f"Requester person {request.requester_person_id} not found")
            return None

        # Get target person
        target_person = self.person_repo.get_by_id(request.target_person_id)
        if not target_person:
            logger.warning(f"Target person {request.target_person_id} not found")
            return None

        # Get requester gender name
        requester_gender = "Unknown"
        if requester_person.gender_id:
            gender = get_gender_by_id(requester_person.gender_id)
            if gender:
                requester_gender = gender.name

        # Get requester address display
        address_service = PersonAddressService(self.session)
        requester_address = address_service.get_formatted_current_address(
            requester_person.id
        )

        # Get requester religion display
        religion_service = PersonReligionService(self.session)
        requester_religion = religion_service.get_formatted_religion(
            requester_person.id
        )

        return AttachmentRequestWithDetails(
            id=request.id,
            status=request.status,
            created_at=request.created_at,
            requester_first_name=requester_person.first_name,
            requester_middle_name=requester_person.middle_name,
            requester_last_name=requester_person.last_name,
            requester_date_of_birth=requester_person.date_of_birth,
            requester_gender=requester_gender,
            requester_address_display=requester_address,
            requester_religion_display=requester_religion,
            target_first_name=target_person.first_name,
            target_middle_name=target_person.middle_name,
            target_last_name=target_person.last_name,
            target_date_of_birth=target_person.date_of_birth,
        )

    def approve_request(
        self, request_id: uuid.UUID, approver_user_id: uuid.UUID
    ) -> None:
        """
        Approve an attachment request.

        Actions:
        1. Validate request exists and is pending
        2. Validate current user is the approver
        3. Transfer marital status from temp person to target person
        4. Link requester user to target person
        5. Set target person as primary
        6. Delete requester's temp person and all metadata
        7. Update request status to APPROVED
        """
        logger.info(
            f"Approving attachment request: request_id={request_id}, "
            f"approver={approver_user_id}"
        )

        # 1. Get the request
        request = self.request_repo.get_by_id(request_id)
        if not request:
            logger.warning(f"Attachment request {request_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment request not found",
            )

        # 2. Validate current user is the approver
        if request.approver_user_id != approver_user_id:
            logger.warning(
                f"User {approver_user_id} is not authorized to approve request {request_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action",
            )

        # 3. Validate request is pending
        if request.status != AttachmentRequestStatus.PENDING:
            logger.warning(
                f"Request {request_id} is not pending (status: {request.status})"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This request has already been resolved",
            )

        # 4. Get target person and link requester user
        target_person = self.person_repo.get_by_id(request.target_person_id)
        if not target_person:
            logger.error(f"Target person {request.target_person_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target person not found",
            )

        # 5. Store requester_person_id before updating request
        requester_person_id = request.requester_person_id
        if requester_person_id is None:
            logger.error(f"Requester person ID is None for request {request_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid request state: requester person not found",
            )

        # 6. Get requester's temp person to transfer data
        requester_person = self.person_repo.get_by_id(requester_person_id)
        if requester_person:
            # Transfer marital status from temp person to target person
            # The requester's self-reported marital status is more accurate
            logger.info(
                f"Transferring marital status from temp person {requester_person_id} "
                f"({requester_person.marital_status}) to target person {target_person.id}"
            )
            target_person.marital_status = requester_person.marital_status

        # 7. Update request status and clear FK reference FIRST
        # This must be committed before we can delete the person
        request.status = AttachmentRequestStatus.APPROVED
        request.resolved_at = datetime.utcnow()
        request.resolved_by_user_id = approver_user_id
        request.requester_person_id = None  # Clear FK reference before deletion
        self.session.add(request)
        self.session.commit()
        logger.info(f"Updated request {request_id} status to APPROVED and cleared requester_person_id")

        # 8. Clear requester_person_id from ALL other attachment requests for this person
        # This handles cases where user cancelled previous requests
        other_requests = self.request_repo.get_by_requester_person(requester_person_id)
        for other_request in other_requests:
            other_request.requester_person_id = None
            self.session.add(other_request)
        if other_requests:
            self.session.commit()
            logger.info(f"Cleared requester_person_id from {len(other_requests)} other attachment requests")

        # 9. Delete requester's temp person and all metadata
        # This is done after clearing the FK reference
        self._delete_person_with_metadata(requester_person_id)
        logger.info(f"Deleted temp person {requester_person_id}")

        # 10. Link requester user to target person (after temp person is deleted)
        target_person.user_id = request.requester_user_id
        target_person.is_primary = True
        target_person.is_active = True  # Activate the target person
        target_person.updated_at = datetime.utcnow()
        self.session.add(target_person)
        self.session.commit()
        logger.info(
            f"Linked user {request.requester_user_id} to person {target_person.id}"
        )

        logger.info(f"Attachment request {request_id} approved successfully")

    def deny_request(self, request_id: uuid.UUID, approver_user_id: uuid.UUID) -> None:
        """
        Deny an attachment request.

        Actions:
        1. Validate request exists and is pending
        2. Validate current user is the approver
        3. Delete requester's temp person and all metadata
        4. Delete requester's user account
        5. Update request status to DENIED
        """
        logger.info(
            f"Denying attachment request: request_id={request_id}, "
            f"approver={approver_user_id}"
        )

        # 1. Get the request
        request = self.request_repo.get_by_id(request_id)
        if not request:
            logger.warning(f"Attachment request {request_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment request not found",
            )

        # 2. Validate current user is the approver
        if request.approver_user_id != approver_user_id:
            logger.warning(
                f"User {approver_user_id} is not authorized to deny request {request_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to perform this action",
            )

        # 3. Validate request is pending
        if request.status != AttachmentRequestStatus.PENDING:
            logger.warning(
                f"Request {request_id} is not pending (status: {request.status})"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This request has already been resolved",
            )

        # Store IDs before updating request
        requester_user_id = request.requester_user_id
        requester_person_id = request.requester_person_id

        # Validate IDs are not None
        if requester_person_id is None:
            logger.error(f"Requester person ID is None for request {request_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid request state: requester person not found",
            )
        if requester_user_id is None:
            logger.error(f"Requester user ID is None for request {request_id}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Invalid request state: requester user not found",
            )

        # 4. Update request status FIRST (before deleting person/user to avoid FK violation)
        request.status = AttachmentRequestStatus.DENIED
        request.resolved_at = datetime.utcnow()
        request.resolved_by_user_id = approver_user_id
        request.requester_person_id = None  # Clear FK reference before deletion
        request.requester_user_id = None  # Clear FK reference before user deletion
        self.session.add(request)
        self.session.commit()
        logger.info(f"Updated request {request_id} status to DENIED and cleared FK references")

        # 5. Clear requester_person_id from ALL other attachment requests for this person
        # This handles cases where user cancelled previous requests
        other_requests = self.request_repo.get_by_requester_person(requester_person_id)
        for other_request in other_requests:
            other_request.requester_person_id = None
            self.session.add(other_request)
        if other_requests:
            self.session.commit()
            logger.info(f"Cleared requester_person_id from {len(other_requests)} other attachment requests")

        # 6. Delete requester's temp person and all metadata
        self._delete_person_with_metadata(requester_person_id)
        logger.info(f"Deleted temp person {requester_person_id}")

        # 6. Delete requester's user account
        requester_user = self.user_repo.get_by_id(requester_user_id)
        if requester_user:
            self.user_repo.delete(requester_user)
            logger.info(f"Deleted requester user {requester_user_id}")
        else:
            logger.warning(f"Requester user {requester_user_id} not found for deletion")

        logger.info(f"Attachment request {request_id} denied successfully")

    def cancel_request(
        self, request_id: uuid.UUID, requester_user_id: uuid.UUID
    ) -> None:
        """
        Cancel an attachment request.

        Actions:
        1. Validate request exists and is pending
        2. Validate current user is the requester
        3. Update request status to CANCELLED (no deletions)
        """
        logger.info(
            f"Cancelling attachment request: request_id={request_id}, "
            f"requester={requester_user_id}"
        )

        # 1. Get the request
        request = self.request_repo.get_by_id(request_id)
        if not request:
            logger.warning(f"Attachment request {request_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attachment request not found",
            )

        # 2. Validate current user is the requester
        if request.requester_user_id != requester_user_id:
            logger.warning(
                f"User {requester_user_id} is not authorized to cancel request {request_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only cancel your own requests",
            )

        # 3. Validate request is pending
        if request.status != AttachmentRequestStatus.PENDING:
            logger.warning(
                f"Request {request_id} is not pending (status: {request.status})"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This request has already been resolved",
            )

        # 4. Update request status only (no deletions)
        request.status = AttachmentRequestStatus.CANCELLED
        request.resolved_at = datetime.utcnow()
        request.resolved_by_user_id = requester_user_id
        self.request_repo.update(request)

        logger.info(f"Attachment request {request_id} cancelled successfully")

    def _delete_person_with_metadata(self, person_id: uuid.UUID) -> None:
        """
        Delete a person and all associated metadata.

        Deletes in order to respect foreign key constraints:
        1. person_address records
        2. person_religion records
        3. person_relationship records
        4. person_life_event records
        5. person_metadata records
        6. person_profession records
        7. person record

        Uses transaction for atomicity.
        """
        logger.info(f"Deleting person with metadata: {person_id}")

        try:
            # 1. Delete person_address records
            address_repo = PersonAddressRepository(self.session)
            addresses = address_repo.get_by_person_id(person_id)
            for address in addresses:
                self.session.delete(address)
            logger.debug(
                f"Deleted {len(addresses)} address records for person {person_id}"
            )

            # 2. Delete person_religion records
            religion_repo = PersonReligionRepository(self.session)
            religion = religion_repo.get_by_person_id(person_id)
            if religion:
                self.session.delete(religion)
                logger.debug(f"Deleted religion record for person {person_id}")

            # 3. Delete person_relationship records
            relationship_repo = PersonRelationshipRepository(self.session)
            relationships = relationship_repo.get_by_person_id(person_id)
            for relationship in relationships:
                self.session.delete(relationship)
            logger.debug(
                f"Deleted {len(relationships)} relationship records for person {person_id}"
            )

            # 4. Delete person_life_event records
            life_event_repo = LifeEventRepository(self.session)
            life_events = life_event_repo.get_by_person(person_id)
            for event in life_events:
                self.session.delete(event)
            logger.debug(
                f"Deleted {len(life_events)} life event records for person {person_id}"
            )

            # 5. Delete person_metadata records
            metadata_repo = PersonMetadataRepository(self.session)
            metadata = metadata_repo.get_by_person_id(person_id)
            if metadata:
                self.session.delete(metadata)
                logger.debug(f"Deleted metadata record for person {person_id}")

            # 6. Delete person_profession records
            profession_repo = PersonProfessionRepository(self.session)
            professions = profession_repo.get_by_person_id(person_id)
            for profession in professions:
                self.session.delete(profession)
            logger.debug(
                f"Deleted {len(professions)} profession records for person {person_id}"
            )

            # 7. Delete person record
            person = self.person_repo.get_by_id(person_id)
            if person:
                self.session.delete(person)
                logger.debug(f"Deleted person record {person_id}")

            # Commit all deletions in a single transaction
            self.session.commit()
            logger.info(f"Successfully deleted person {person_id} with all metadata")

        except Exception as e:
            logger.error(
                f"Failed to delete person {person_id} with metadata: {e}",
                exc_info=True,
            )
            self.session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete person data",
            )

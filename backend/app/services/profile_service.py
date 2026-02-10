"""Profile service for checking profile completion."""

import logging
import uuid

from fastapi import HTTPException
from sqlmodel import Session

from app.enums.marital_status import MaritalStatus
from app.repositories.attachment_request_repository import AttachmentRequestRepository
from app.repositories.person.person_address_repository import PersonAddressRepository
from app.repositories.person.person_religion_repository import PersonReligionRepository
from app.repositories.person.person_repository import PersonRepository
from app.schemas.person.person_search import PersonMatchResult, PersonSearchRequest
from app.schemas.profile import ProfileCompletionStatus
from app.services.person.person_address_service import PersonAddressService
from app.services.person.person_matching_service import PersonMatchingService
from app.services.person.person_religion_service import PersonReligionService

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for profile completion checks."""

    def __init__(self, session: Session):
        self.session = session
        self.person_repo = PersonRepository(session)
        self.address_repo = PersonAddressRepository(session)
        self.religion_repo = PersonReligionRepository(session)
        self.attachment_request_repo = AttachmentRequestRepository(session)

    def check_profile_completion(self, user_id: uuid.UUID) -> ProfileCompletionStatus:
        """Check if user has completed their profile."""
        logger.info(f"Checking profile completion for user ID: {user_id}")
        missing_fields = []

        # Check if person record exists
        person = self.person_repo.get_by_user_id(user_id)
        has_person = person is not None

        if not has_person:
            logger.debug(f"User {user_id} missing person record")
            missing_fields.append("person")
        else:
            # person is guaranteed to be not None here due to has_person check
            assert person is not None
            logger.debug(f"User {user_id} has person record (Person ID: {person.id})")

        # Check if address exists
        has_address = False
        if has_person and person is not None:
            addresses = self.address_repo.get_by_person_id(person.id)  # Use person.id
            has_address = len(addresses) > 0

            if not has_address:
                logger.debug(f"Person {person.id} missing address")
                missing_fields.append("address")
            else:
                logger.debug(f"Person {person.id} has {len(addresses)} address(es)")
        else:
            missing_fields.append("address")

        # Check if religion exists
        has_religion = False
        if has_person and person is not None:
            has_religion = self.religion_repo.person_has_religion(
                person.id
            )  # Use person.id

            if not has_religion:
                logger.debug(f"Person {person.id} missing religion")
                missing_fields.append("religion")
            else:
                logger.debug(f"Person {person.id} has religion")
        else:
            missing_fields.append("religion")

        # Check if marital status is set (not UNKNOWN)
        has_marital_status = False
        if has_person and person is not None:
            has_marital_status = person.marital_status != MaritalStatus.UNKNOWN

            if not has_marital_status:
                logger.debug(f"Person {person.id} missing marital status")
                missing_fields.append("marital_status")
            else:
                logger.debug(
                    f"Person {person.id} has marital status: {person.marital_status}"
                )
        else:
            missing_fields.append("marital_status")

        # Check for pending attachment request
        pending_request = self.attachment_request_repo.get_pending_by_requester(user_id)
        has_pending_attachment_request = pending_request is not None
        pending_request_id = pending_request.id if pending_request else None

        if has_pending_attachment_request:
            logger.debug(
                f"User {user_id} has pending attachment request: {pending_request_id}"
            )

        # Check if duplicate check is complete
        # Duplicate check is complete if:
        # 1. Person is active (user completed without attachment), OR
        # 2. User has a pending attachment request
        has_duplicate_check = False
        if has_person and person is not None:
            has_duplicate_check = person.is_active or has_pending_attachment_request
            logger.debug(
                f"Person {person.id} duplicate check status: {has_duplicate_check} "
                f"(is_active={person.is_active}, has_pending_request={has_pending_attachment_request})"
            )

        if not has_duplicate_check:
            missing_fields.append("duplicate_check")

        # Profile is complete when all steps done AND no pending request
        is_complete = (
            has_person
            and has_address
            and has_religion
            and has_marital_status
            and has_duplicate_check
            and not has_pending_attachment_request
        )

        if is_complete:
            logger.info(f"Profile complete for user {user_id}")
        else:
            logger.info(
                f"Profile incomplete for user {user_id}, missing: {missing_fields}"
            )

        return ProfileCompletionStatus(
            is_complete=is_complete,
            has_person=has_person,
            has_address=has_address,
            has_religion=has_religion,
            has_marital_status=has_marital_status,
            has_duplicate_check=has_duplicate_check,
            has_pending_attachment_request=has_pending_attachment_request,
            pending_request_id=pending_request_id,
            missing_fields=missing_fields,
        )

    def get_duplicate_matches(self, user_id: uuid.UUID) -> list[PersonMatchResult]:
        """Find potential duplicate persons for the current user.

        Uses the user's person data (name, address, religion, gender) to search
        for matching persons that could be the same person.

        Args:
            user_id: The current user's ID

        Returns:
            List of matching persons with scores, filtered to exclude:
            - The current user's own person record
            - Persons that already have a linked user account
            - Inactive persons (handled by PersonMatchingService)
        """
        logger.info(f"Getting duplicate matches for user: {user_id}")

        person = self.person_repo.get_by_user_id(user_id)
        if not person:
            logger.debug(f"User {user_id} has no person record")
            return []

        # Get user's address and religion for matching
        addresses = self.address_repo.get_by_person_id(person.id)
        religion = self.religion_repo.get_by_person_id(person.id)

        if not addresses:
            logger.debug(f"Person {person.id} has no address, cannot search for matches")
            return []

        if not religion:
            logger.debug(f"Person {person.id} has no religion, cannot search for matches")
            return []

        address = addresses[0]  # Use primary/first address

        # Build display strings for address and religion
        address_display = self._build_address_display(person.id)
        religion_display = self._build_religion_display(person.id)

        # Build search criteria from user's data
        search_criteria = PersonSearchRequest(
            first_name=person.first_name,
            last_name=person.last_name,
            gender_id=person.gender_id,
            country_id=address.country_id,
            state_id=address.state_id,
            district_id=address.district_id,
            sub_district_id=address.sub_district_id,
            locality_id=address.locality_id,
            religion_id=religion.religion_id,
            religion_category_id=religion.religion_category_id,
            religion_sub_category_id=religion.religion_sub_category_id,
            address_display=address_display,
            religion_display=religion_display,
        )

        logger.debug(f"Search criteria built for person {person.id}")

        # Use existing matching service
        matching_service = PersonMatchingService(self.session)
        matches = matching_service.search_matching_persons(user_id, search_criteria)

        logger.debug(f"Found {len(matches)} initial matches")

        # Filter out persons that already have a user linked
        # (they can't be attachment targets)
        filtered_matches = [
            m
            for m in matches
            if not self._person_has_user(m.person_id) and m.person_id != person.id
        ]

        logger.info(
            f"Returning {len(filtered_matches)} matches after filtering "
            f"(excluded {len(matches) - len(filtered_matches)} with linked users)"
        )

        return filtered_matches

    def complete_without_attachment(
        self, user_id: uuid.UUID
    ) -> ProfileCompletionStatus:
        """Complete profile without attaching to existing person.

        Activates the current user's person record, marking the duplicate
        check step as complete.

        Args:
            user_id: The current user's ID

        Returns:
            Updated profile completion status

        Raises:
            HTTPException: If user has pending attachment request or person not found
        """
        logger.info(f"Completing profile without attachment for user: {user_id}")

        # Check for pending request
        pending_request = self.attachment_request_repo.get_pending_by_requester(user_id)
        if pending_request:
            logger.warning(
                f"User {user_id} has pending attachment request, cannot complete"
            )
            raise HTTPException(
                status_code=400,
                detail="Cannot complete profile while attachment request is pending",
            )

        # Activate the person
        person = self.person_repo.get_by_user_id(user_id)
        if not person:
            logger.warning(f"User {user_id} has no person record")
            raise HTTPException(status_code=404, detail="Person not found")

        person.is_active = True
        self.session.add(person)
        self.session.commit()

        logger.info(f"Person {person.id} activated for user {user_id}")

        return self.check_profile_completion(user_id)

    def _build_address_display(self, person_id: uuid.UUID) -> str | None:
        """Build address display string for a person.

        Args:
            person_id: The person's ID

        Returns:
            Formatted address string or None if no address
        """
        address_service = PersonAddressService(self.session)
        return address_service.get_formatted_current_address(person_id)

    def _build_religion_display(self, person_id: uuid.UUID) -> str | None:
        """Build religion display string for a person.

        Args:
            person_id: The person's ID

        Returns:
            Formatted religion string or None if no religion
        """
        religion_service = PersonReligionService(self.session)
        return religion_service.get_formatted_religion(person_id)

    def _person_has_user(self, person_id: uuid.UUID) -> bool:
        """Check if a person has a linked user account.

        Args:
            person_id: The person's ID

        Returns:
            True if person has a user_id, False otherwise
        """
        person = self.person_repo.get_by_id(person_id)
        if not person:
            return False
        return person.user_id is not None

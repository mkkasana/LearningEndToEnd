"""Profile service for checking profile completion."""

import logging
import uuid

from sqlmodel import Session

from app.repositories.person.person_address_repository import PersonAddressRepository
from app.repositories.person.person_religion_repository import PersonReligionRepository
from app.repositories.person.person_repository import PersonRepository
from app.schemas.profile import ProfileCompletionStatus

logger = logging.getLogger(__name__)


class ProfileService:
    """Service for profile completion checks."""

    def __init__(self, session: Session):
        self.session = session
        self.person_repo = PersonRepository(session)
        self.address_repo = PersonAddressRepository(session)
        self.religion_repo = PersonReligionRepository(session)

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

        is_complete = has_person and has_address and has_religion
        
        if is_complete:
            logger.info(f"Profile complete for user {user_id}")
        else:
            logger.info(f"Profile incomplete for user {user_id}, missing: {missing_fields}")

        return ProfileCompletionStatus(
            is_complete=is_complete,
            has_person=has_person,
            has_address=has_address,
            has_religion=has_religion,
            missing_fields=missing_fields,
        )

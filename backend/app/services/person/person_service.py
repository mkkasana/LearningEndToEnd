"""Person service."""

import logging
import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person import Person
from app.repositories.person.person_address_repository import PersonAddressRepository
from app.repositories.person.person_repository import PersonRepository
from app.schemas.person import PersonCreate, PersonUpdate
from app.services.profile_view_tracking_service import ProfileViewTrackingService

logger = logging.getLogger(__name__)


class PersonService:
    """Service for person business logic."""

    def __init__(self, session: Session):
        self.person_repo = PersonRepository(session)

    def get_person_by_user_id(self, user_id: uuid.UUID) -> Person | None:
        """Get person by user ID."""
        logger.debug(f"Fetching person for user ID: {user_id}")
        person = self.person_repo.get_by_user_id(user_id)
        if person:
            logger.debug(
                f"Person found: {person.first_name} {person.last_name} "
                f"(Person ID: {person.id}, User ID: {user_id})"
            )
        else:
            logger.debug(f"No person found for user ID: {user_id}")
        return person

    def create_person(self, person_create: PersonCreate) -> Person:
        """Create a new person."""
        logger.info(
            f"Creating person: {person_create.first_name} {person_create.last_name}, "
            f"gender_id={person_create.gender_id}, user_id={person_create.user_id}"
        )
        person = Person(**person_create.model_dump())
        created_person = self.person_repo.create(person)
        logger.info(
            f"Person created successfully: {created_person.first_name} {created_person.last_name} "
            f"(ID: {created_person.id}), is_primary={created_person.is_primary}"
        )
        return created_person

    def update_person(self, person: Person, person_update: PersonUpdate) -> Person:
        """Update a person."""
        logger.info(
            f"Updating person: {person.first_name} {person.last_name} (ID: {person.id})"
        )
        update_data = person_update.model_dump(exclude_unset=True)

        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(f"Updating fields for person {person.id}: {update_fields}")

        for key, value in update_data.items():
            setattr(person, key, value)
        person.updated_at = datetime.utcnow()

        updated_person = self.person_repo.update(person)
        logger.info(
            f"Person updated successfully: {updated_person.first_name} {updated_person.last_name} "
            f"(ID: {updated_person.id})"
        )
        return updated_person

    def delete_person(self, person: Person) -> None:
        """Delete a person."""
        logger.warning(
            f"Deleting person: {person.first_name} {person.last_name} (ID: {person.id})"
        )
        self.person_repo.delete(person)
        logger.info(
            f"Person deleted successfully: {person.first_name} {person.last_name} (ID: {person.id})"
        )

    def user_has_person(self, user_id: uuid.UUID) -> bool:
        """Check if user already has a person record."""
        logger.debug(f"Checking if user has person record: user_id={user_id}")
        has_person = self.person_repo.user_has_person(user_id)
        logger.debug(f"User {user_id} has person: {has_person}")
        return has_person

    def get_my_contributions(self, user_id: uuid.UUID) -> list[dict]:
        """
        Get all persons created by the user with view statistics.

        Returns list of dicts with person details, addresses, and view counts.
        Sorted by view count descending (most viewed first).
        """
        logger.info(f"Fetching contributions for user: {user_id}")

        # Get all persons created by this user
        persons = self.person_repo.get_by_creator(user_id)

        if not persons:
            logger.debug(f"No contributions found for user {user_id}")
            return []

        logger.debug(f"Found {len(persons)} contributions for user {user_id}")

        # Get person IDs for bulk operations
        person_ids = [p.id for p in persons]

        # Get view counts for all persons
        view_tracking_service = ProfileViewTrackingService(self.person_repo.session)
        view_counts = view_tracking_service.get_total_views_bulk(person_ids)

        # Get addresses for all persons
        address_repo = PersonAddressRepository(self.person_repo.session)

        # Build result list
        results = []
        for person in persons:
            # Get addresses for this person
            addresses = address_repo.get_by_person_id(person.id)
            address_str = self._format_addresses(addresses)

            # Get view count (default to 0 if no views)
            view_count = view_counts.get(person.id, 0)

            results.append(
                {
                    "id": person.id,
                    "first_name": person.first_name,
                    "last_name": person.last_name,
                    "date_of_birth": person.date_of_birth,
                    "date_of_death": person.date_of_death,
                    "is_active": (
                        person.is_active if hasattr(person, "is_active") else True
                    ),
                    "address": address_str,
                    "total_views": view_count,
                    "created_at": person.created_at,
                }
            )

        # Sort by view count descending
        results.sort(key=lambda x: x["total_views"], reverse=True)

        logger.info(
            f"Returning {len(results)} contributions for user {user_id}, "
            f"sorted by view count"
        )

        return results

    def _format_addresses(self, addresses: list) -> str:
        """Format addresses as comma-separated string."""
        if not addresses:
            return ""

        address_parts = []
        for addr in addresses:
            # For now, use address_line if available
            # In the future, this can be enhanced to join with location tables
            # to get country, state, district, sub_district, locality names
            if addr.address_line:
                address_parts.append(addr.address_line)

        return ", ".join(address_parts)

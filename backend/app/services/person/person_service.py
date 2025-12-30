"""Person service."""

import logging
import uuid
from datetime import date, datetime

from sqlmodel import Session

from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.repositories.address.country_repository import CountryRepository
from app.repositories.address.district_repository import DistrictRepository
from app.repositories.address.locality_repository import LocalityRepository
from app.repositories.address.state_repository import StateRepository
from app.repositories.address.sub_district_repository import SubDistrictRepository
from app.repositories.person.gender_repository import GenderRepository
from app.repositories.person.person_address_repository import PersonAddressRepository
from app.repositories.person.person_religion_repository import PersonReligionRepository
from app.repositories.person.person_repository import PersonRepository
from app.repositories.religion.religion_category_repository import (
    ReligionCategoryRepository,
)
from app.repositories.religion.religion_repository import ReligionRepository
from app.repositories.religion.religion_sub_category_repository import (
    ReligionSubCategoryRepository,
)
from app.schemas.person import PersonCreate, PersonUpdate
from app.schemas.person.person_complete_details import (
    PersonAddressDetails,
    PersonCompleteDetailsResponse,
    PersonReligionDetails,
)
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

    def get_my_contributions(
        self, user_id: uuid.UUID
    ) -> list[dict[str, str | int | uuid.UUID | date | datetime | None]]:
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

        # Sort by view count descending (total_views is always int)
        results.sort(key=lambda x: x.get("total_views", 0) or 0, reverse=True)

        logger.info(
            f"Returning {len(results)} contributions for user {user_id}, "
            f"sorted by view count"
        )

        return results

    def _format_addresses(self, addresses: list[PersonAddress]) -> str:
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

    def get_person_complete_details(
        self, person_id: uuid.UUID
    ) -> PersonCompleteDetailsResponse | None:
        """
        Get complete person details with resolved names for gender, address, and religion.

        Args:
            person_id: The UUID of the person to fetch

        Returns:
            PersonCompleteDetailsResponse with all resolved names, or None if person not found
        """
        logger.info(f"Fetching complete details for person ID: {person_id}")

        # 1. Fetch person by ID
        person = self.person_repo.get_by_id(person_id)
        if not person:
            logger.debug(f"Person not found: {person_id}")
            return None

        # 2. Resolve gender name
        gender_name = "Unknown"
        if person.gender_id:
            gender_repo = GenderRepository(self.person_repo.session)
            gender = gender_repo.get_by_id(person.gender_id)
            if gender:
                gender_name = gender.name
                logger.debug(f"Resolved gender: {gender_name}")

        # 3. Fetch current address and resolve location names
        address_details = self._resolve_address_details(person_id)

        # 4. Fetch religion and resolve names
        religion_details = self._resolve_religion_details(person_id)

        # 5. Build and return response
        response = PersonCompleteDetailsResponse(
            id=person.id,
            first_name=person.first_name,
            middle_name=person.middle_name,
            last_name=person.last_name,
            date_of_birth=person.date_of_birth,
            date_of_death=person.date_of_death,
            gender_name=gender_name,
            address=address_details,
            religion=religion_details,
        )

        logger.info(
            f"Complete details fetched for person: {person.first_name} {person.last_name}"
        )
        return response

    def _resolve_address_details(
        self, person_id: uuid.UUID
    ) -> PersonAddressDetails | None:
        """Resolve address details with location names."""
        address_repo = PersonAddressRepository(self.person_repo.session)
        current_address = address_repo.get_current_address(person_id)

        if not current_address:
            logger.debug(f"No current address found for person {person_id}")
            return None

        # Initialize repositories for location lookups
        country_repo = CountryRepository(self.person_repo.session)
        state_repo = StateRepository(self.person_repo.session)
        district_repo = DistrictRepository(self.person_repo.session)
        sub_district_repo = SubDistrictRepository(self.person_repo.session)
        locality_repo = LocalityRepository(self.person_repo.session)

        # Resolve country name (required)
        country = country_repo.get_by_id(current_address.country_id)
        country_name = country.name if country else "Unknown"

        # Resolve optional location names
        state_name = None
        if current_address.state_id:
            state = state_repo.get_by_id(current_address.state_id)
            state_name = state.name if state else None

        district_name = None
        if current_address.district_id:
            district = district_repo.get_by_id(current_address.district_id)
            district_name = district.name if district else None

        sub_district_name = None
        if current_address.sub_district_id:
            sub_district = sub_district_repo.get_by_id(current_address.sub_district_id)
            sub_district_name = sub_district.name if sub_district else None

        locality_name = None
        if current_address.locality_id:
            locality = locality_repo.get_by_id(current_address.locality_id)
            locality_name = locality.name if locality else None

        logger.debug(
            f"Resolved address for person {person_id}: "
            f"{locality_name}, {sub_district_name}, {district_name}, {state_name}, {country_name}"
        )

        return PersonAddressDetails(
            locality_name=locality_name,
            sub_district_name=sub_district_name,
            district_name=district_name,
            state_name=state_name,
            country_name=country_name,
            address_line=current_address.address_line,
        )

    def _resolve_religion_details(
        self, person_id: uuid.UUID
    ) -> PersonReligionDetails | None:
        """Resolve religion details with names."""
        religion_repo = PersonReligionRepository(self.person_repo.session)
        person_religion = religion_repo.get_by_person_id(person_id)

        if not person_religion:
            logger.debug(f"No religion found for person {person_id}")
            return None

        # Initialize repositories for religion lookups
        religion_master_repo = ReligionRepository(self.person_repo.session)
        category_repo = ReligionCategoryRepository(self.person_repo.session)
        sub_category_repo = ReligionSubCategoryRepository(self.person_repo.session)

        # Resolve religion name (required)
        religion = religion_master_repo.get_by_id(person_religion.religion_id)
        religion_name = religion.name if religion else "Unknown"

        # Resolve optional category and sub-category names
        category_name = None
        if person_religion.religion_category_id:
            category = category_repo.get_by_id(person_religion.religion_category_id)
            category_name = category.name if category else None

        sub_category_name = None
        if person_religion.religion_sub_category_id:
            sub_category = sub_category_repo.get_by_id(
                person_religion.religion_sub_category_id
            )
            sub_category_name = sub_category.name if sub_category else None

        logger.debug(
            f"Resolved religion for person {person_id}: "
            f"{religion_name}, {category_name}, {sub_category_name}"
        )

        return PersonReligionDetails(
            religion_name=religion_name,
            category_name=category_name,
            sub_category_name=sub_category_name,
        )

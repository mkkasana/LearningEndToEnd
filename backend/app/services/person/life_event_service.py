"""Life Event service."""

import calendar
import logging
import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person_life_event import PersonLifeEvent
from app.db_models.user import User
from app.repositories.person.life_event_repository import LifeEventRepository
from app.schemas.person.life_event import LifeEventCreate, LifeEventUpdate

logger = logging.getLogger(__name__)


class LifeEventService:
    """Service for life event business logic."""

    def __init__(self, session: Session):
        self.session = session
        self.life_event_repo = LifeEventRepository(session)

    def get_life_events(
        self, person_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[PersonLifeEvent], int]:
        """Get all life events for a person with pagination."""
        logger.debug(
            f"Fetching life events for person: {person_id}, skip={skip}, limit={limit}"
        )
        events = self.life_event_repo.get_by_person(person_id, skip=skip, limit=limit)
        count = self.life_event_repo.count_by_person(person_id)
        logger.info(
            f"Retrieved {len(events)} life events for person {person_id} (total: {count})"
        )
        return events, count

    def get_life_event_by_id(self, event_id: uuid.UUID) -> PersonLifeEvent | None:
        """Get a single life event by ID."""
        logger.debug(f"Fetching life event by ID: {event_id}")
        event = self.life_event_repo.get_by_id(event_id)
        if event:
            logger.info(f"Life event found: {event.title} (ID: {event.id})")
        else:
            logger.info(f"Life event not found: ID {event_id}")
        return event

    def create_life_event(
        self, person_id: uuid.UUID, life_event_in: LifeEventCreate
    ) -> PersonLifeEvent:
        """Create a new life event for a person."""
        logger.info(
            f"Creating life event: {life_event_in.title} for person: {person_id}"
        )

        # Validate date consistency
        self.validate_date(
            life_event_in.event_year,
            life_event_in.event_month,
            life_event_in.event_date,
        )

        life_event = PersonLifeEvent(
            person_id=person_id,
            event_type=life_event_in.event_type.value,
            title=life_event_in.title,
            description=life_event_in.description,
            event_year=life_event_in.event_year,
            event_month=life_event_in.event_month,
            event_date=life_event_in.event_date,
            country_id=life_event_in.country_id,
            state_id=life_event_in.state_id,
            district_id=life_event_in.district_id,
            sub_district_id=life_event_in.sub_district_id,
            locality_id=life_event_in.locality_id,
            address_details=life_event_in.address_details,
        )
        created_event = self.life_event_repo.create(life_event)
        logger.info(
            f"Life event created: {created_event.title} (ID: {created_event.id})"
        )
        return created_event

    def update_life_event(
        self, life_event: PersonLifeEvent, life_event_in: LifeEventUpdate
    ) -> PersonLifeEvent:
        """Update a life event."""
        logger.info(f"Updating life event: {life_event.title} (ID: {life_event.id})")

        update_data = life_event_in.model_dump(exclude_unset=True)

        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(
                f"Updating fields for life event {life_event.id}: {update_fields}"
            )

        # Determine the final values for date validation
        event_year = update_data.get("event_year", life_event.event_year)
        event_month = update_data.get("event_month", life_event.event_month)
        event_date = update_data.get("event_date", life_event.event_date)

        # Validate date consistency
        self.validate_date(event_year, event_month, event_date)

        # Handle event_type enum conversion
        if "event_type" in update_data and update_data["event_type"] is not None:
            update_data["event_type"] = update_data["event_type"].value

        for key, value in update_data.items():
            setattr(life_event, key, value)

        life_event.updated_at = datetime.utcnow()
        updated_event = self.life_event_repo.update(life_event)
        logger.info(
            f"Life event updated: {updated_event.title} (ID: {updated_event.id})"
        )
        return updated_event

    def delete_life_event(self, life_event: PersonLifeEvent) -> None:
        """Delete a life event."""
        logger.warning(
            f"Deleting life event: {life_event.title} (ID: {life_event.id}) "
            f"for person {life_event.person_id}"
        )
        self.life_event_repo.delete(life_event)
        logger.info(f"Life event deleted: {life_event.title} (ID: {life_event.id})")

    def user_can_access_event(
        self, user: User, life_event: PersonLifeEvent, user_person_id: uuid.UUID | None
    ) -> bool:
        """Check if user can access a life event.

        Users can only access their own life events (events linked to their person record).
        Superusers and admins can access all events.
        """
        # Superusers and admins can access all events
        if user.is_superuser or user.is_admin:
            logger.debug(
                f"User {user.id} (admin/superuser) has access to life event: "
                f"{life_event.title} (ID: {life_event.id})"
            )
            return True

        # Regular users can only access their own events
        if user_person_id is None:
            logger.warning(
                f"User {user.id} has no person record, denying access to life event: "
                f"{life_event.title} (ID: {life_event.id})"
            )
            return False

        can_access = life_event.person_id == user_person_id
        if can_access:
            logger.debug(
                f"User {user.id} has access to life event: "
                f"{life_event.title} (ID: {life_event.id})"
            )
        else:
            logger.warning(
                f"User {user.id} denied access to life event: "
                f"{life_event.title} (ID: {life_event.id})"
            )
        return can_access

    @staticmethod
    def validate_date(year: int, month: int | None, date: int | None) -> None:
        """Validate date consistency.

        If event_date is provided, it must be valid for the given month and year.
        For example, Feb 30 or Apr 31 are invalid.

        Raises:
            ValueError: If the date is invalid for the given month/year.
        """
        if date is None or month is None:
            # No validation needed if date or month is not provided
            return

        # Get the maximum number of days in the given month/year
        _, max_days = calendar.monthrange(year, month)

        if date > max_days:
            logger.warning(
                f"Invalid date: {year}-{month}-{date} (max days in month: {max_days})"
            )
            raise ValueError(
                f"Invalid date for the given month/year: day {date} is not valid "
                f"for month {month} in year {year} (max: {max_days} days)"
            )

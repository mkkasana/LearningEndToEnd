"""Person Address repository."""

import logging
import uuid

from sqlmodel import Session, desc, select

from app.db_models.person.person_address import PersonAddress
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PersonAddressRepository(BaseRepository[PersonAddress]):
    """Repository for person address data access."""

    def __init__(self, session: Session):
        super().__init__(PersonAddress, session)

    def get_by_person_id(self, person_id: uuid.UUID) -> list[PersonAddress]:
        """Get all addresses for a person."""
        logger.debug(f"Querying addresses for person: {person_id}")
        statement = (
            select(PersonAddress)
            .where(PersonAddress.person_id == person_id)
            .order_by(desc(PersonAddress.start_date))
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} addresses for person {person_id}")
        return results

    def get_current_address(self, person_id: uuid.UUID) -> PersonAddress | None:
        """Get current address for a person."""
        logger.debug(f"Querying current address for person: {person_id}")
        statement = select(PersonAddress).where(
            PersonAddress.person_id == person_id, PersonAddress.is_current
        )
        result = self.session.exec(statement).first()
        if result:
            logger.debug(f"Current address found for person {person_id} (ID: {result.id})")
        else:
            logger.debug(f"No current address found for person {person_id}")
        return result

    def clear_current_addresses(self, person_id: uuid.UUID) -> None:
        """Clear is_current flag for all addresses of a person."""
        logger.debug(f"Clearing current addresses for person: {person_id}")
        statement = select(PersonAddress).where(PersonAddress.person_id == person_id)
        addresses = self.session.exec(statement).all()
        count = 0
        for address in addresses:
            address.is_current = False
            self.session.add(address)
            count += 1
        self.session.commit()
        logger.debug(f"Cleared {count} current addresses for person {person_id}")

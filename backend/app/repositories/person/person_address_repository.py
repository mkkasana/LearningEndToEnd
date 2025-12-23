"""Person Address repository."""

import uuid

from sqlmodel import Session, select

from app.db_models.person.person_address import PersonAddress
from app.repositories.base import BaseRepository


class PersonAddressRepository(BaseRepository[PersonAddress]):
    """Repository for person address data access."""

    def __init__(self, session: Session):
        super().__init__(PersonAddress, session)

    def get_by_person_id(self, person_id: uuid.UUID) -> list[PersonAddress]:
        """Get all addresses for a person."""
        statement = (
            select(PersonAddress)
            .where(PersonAddress.person_id == person_id)
            .order_by(PersonAddress.start_date.desc())
        )
        return list(self.session.exec(statement).all())

    def get_current_address(self, person_id: uuid.UUID) -> PersonAddress | None:
        """Get current address for a person."""
        statement = select(PersonAddress).where(
            PersonAddress.person_id == person_id, PersonAddress.is_current == True
        )
        return self.session.exec(statement).first()

    def clear_current_addresses(self, person_id: uuid.UUID) -> None:
        """Clear is_current flag for all addresses of a person."""
        statement = select(PersonAddress).where(PersonAddress.person_id == person_id)
        addresses = self.session.exec(statement).all()
        for address in addresses:
            address.is_current = False
            self.session.add(address)
        self.session.commit()

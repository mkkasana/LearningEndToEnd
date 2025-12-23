"""Person Address service."""

import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person_address import PersonAddress
from app.repositories.person.person_address_repository import PersonAddressRepository
from app.schemas.person import PersonAddressCreate, PersonAddressUpdate


class PersonAddressService:
    """Service for person address business logic."""

    def __init__(self, session: Session):
        self.address_repo = PersonAddressRepository(session)

    def get_addresses_by_person(self, person_id: uuid.UUID) -> list[PersonAddress]:
        """Get all addresses for a person."""
        return self.address_repo.get_by_person_id(person_id)

    def get_address_by_id(self, address_id: uuid.UUID) -> PersonAddress | None:
        """Get address by ID."""
        return self.address_repo.get_by_id(address_id)

    def create_address(
        self, person_id: uuid.UUID, address_create: PersonAddressCreate
    ) -> PersonAddress:
        """Create a new address for a person."""
        # If marking as current, clear other current addresses
        if address_create.is_current:
            self.address_repo.clear_current_addresses(person_id)

        address = PersonAddress(person_id=person_id, **address_create.model_dump())
        return self.address_repo.create(address)

    def update_address(
        self, address: PersonAddress, address_update: PersonAddressUpdate
    ) -> PersonAddress:
        """Update an address."""
        update_data = address_update.model_dump(exclude_unset=True)

        # If marking as current, clear other current addresses
        if update_data.get("is_current"):
            self.address_repo.clear_current_addresses(address.person_id)

        for key, value in update_data.items():
            setattr(address, key, value)
        address.updated_at = datetime.utcnow()
        return self.address_repo.update(address)

    def delete_address(self, address: PersonAddress) -> None:
        """Delete an address."""
        self.address_repo.delete(address)

"""Person Address service."""

import logging
import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person_address import PersonAddress
from app.repositories.person.person_address_repository import PersonAddressRepository
from app.schemas.person import PersonAddressCreate, PersonAddressUpdate

logger = logging.getLogger(__name__)


class PersonAddressService:
    """Service for person address business logic."""

    def __init__(self, session: Session):
        self.address_repo = PersonAddressRepository(session)

    def get_addresses_by_person(self, person_id: uuid.UUID) -> list[PersonAddress]:
        """Get all addresses for a person."""
        logger.debug(f"Fetching addresses for person ID: {person_id}")
        addresses = self.address_repo.get_by_person_id(person_id)
        logger.debug(f"Found {len(addresses)} address(es) for person {person_id}")
        return addresses

    def get_address_by_id(self, address_id: uuid.UUID) -> PersonAddress | None:
        """Get address by ID."""
        logger.debug(f"Fetching address by ID: {address_id}")
        address = self.address_repo.get_by_id(address_id)
        if address:
            logger.debug(f"Address found: ID {address_id}")
        else:
            logger.debug(f"Address not found: ID {address_id}")
        return address

    def create_address(
        self, person_id: uuid.UUID, address_create: PersonAddressCreate
    ) -> PersonAddress:
        """Create a new address for a person."""
        logger.info(f"Creating address for person ID: {person_id}, is_current={address_create.is_current}")
        
        # If marking as current, clear other current addresses
        if address_create.is_current:
            logger.debug(f"Clearing other current addresses for person {person_id}")
            self.address_repo.clear_current_addresses(person_id)

        address = PersonAddress(person_id=person_id, **address_create.model_dump())
        created_address = self.address_repo.create(address)
        logger.info(f"Address created successfully: ID {created_address.id} for person {person_id}")
        return created_address

    def update_address(
        self, address: PersonAddress, address_update: PersonAddressUpdate
    ) -> PersonAddress:
        """Update an address."""
        logger.info(f"Updating address: ID {address.id} for person {address.person_id}")
        update_data = address_update.model_dump(exclude_unset=True)
        
        # Log what fields are being updated
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(f"Updating fields for address {address.id}: {update_fields}")

        # If marking as current, clear other current addresses
        if update_data.get("is_current"):
            logger.debug(f"Clearing other current addresses for person {address.person_id}")
            self.address_repo.clear_current_addresses(address.person_id)

        for key, value in update_data.items():
            setattr(address, key, value)
        address.updated_at = datetime.utcnow()
        updated_address = self.address_repo.update(address)
        logger.info(f"Address updated successfully: ID {updated_address.id}")
        return updated_address

    def delete_address(self, address: PersonAddress) -> None:
        """Delete an address."""
        logger.warning(f"Deleting address: ID {address.id} for person {address.person_id}")
        self.address_repo.delete(address)
        logger.info(f"Address deleted successfully: ID {address.id}")

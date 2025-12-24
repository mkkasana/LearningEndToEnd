"""Profile service for checking profile completion."""

import uuid

from sqlmodel import Session

from app.repositories.person.person_address_repository import PersonAddressRepository
from app.repositories.person.person_religion_repository import PersonReligionRepository
from app.repositories.person.person_repository import PersonRepository
from app.schemas.profile import ProfileCompletionStatus


class ProfileService:
    """Service for profile completion checks."""

    def __init__(self, session: Session):
        self.session = session
        self.person_repo = PersonRepository(session)
        self.address_repo = PersonAddressRepository(session)
        self.religion_repo = PersonReligionRepository(session)

    def check_profile_completion(self, user_id: uuid.UUID) -> ProfileCompletionStatus:
        """Check if user has completed their profile."""
        missing_fields = []
        
        # Check if person record exists
        person = self.person_repo.get_by_user_id(user_id)
        has_person = person is not None
        
        print(f"[DEBUG] User ID: {user_id}")
        print(f"[DEBUG] Person exists: {has_person}")
        if has_person:
            print(f"[DEBUG] Person ID: {person.id}")
        
        if not has_person:
            missing_fields.append("person")
        
        # Check if address exists
        has_address = False
        if has_person:
            addresses = self.address_repo.get_by_person_id(person.id)  # Use person.id
            has_address = len(addresses) > 0
            print(f"[DEBUG] Addresses found: {len(addresses)}")
            print(f"[DEBUG] Has address: {has_address}")
            
            if not has_address:
                missing_fields.append("address")
        else:
            missing_fields.append("address")
        
        # Check if religion exists
        has_religion = False
        if has_person:
            has_religion = self.religion_repo.person_has_religion(person.id)  # Use person.id
            print(f"[DEBUG] Has religion: {has_religion}")
            
            if not has_religion:
                missing_fields.append("religion")
        else:
            missing_fields.append("religion")
        
        is_complete = has_person and has_address and has_religion
        
        print(f"[DEBUG] Profile complete: {is_complete}")
        print(f"[DEBUG] Missing fields: {missing_fields}")
        
        return ProfileCompletionStatus(
            is_complete=is_complete,
            has_person=has_person,
            has_address=has_address,
            has_religion=has_religion,
            missing_fields=missing_fields,
        )

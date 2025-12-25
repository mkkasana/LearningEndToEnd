"""Person API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.db_models.person.person import Person
from app.schemas.person import (
    PersonAddressCreate,
    PersonAddressPublic,
    PersonAddressUpdate,
    PersonCreate,
    PersonMetadataCreate,
    PersonMetadataPublic,
    PersonMetadataUpdate,
    PersonProfessionCreate,
    PersonProfessionPublic,
    PersonProfessionUpdate,
    PersonPublic,
    PersonRelationshipCreate,
    PersonRelationshipPublic,
    PersonRelationshipUpdate,
    PersonRelationshipWithDetails,
    PersonReligionCreate,
    PersonUpdate,
)
from app.services.person import (
    PersonAddressService,
    PersonMetadataService,
    PersonProfessionService,
    PersonRelationshipService,
    PersonReligionService,
    PersonService,
)

router = APIRouter()


@router.get("/me", response_model=PersonPublic)
def get_my_person(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    return person


@router.post("/me", response_model=PersonPublic)
def create_my_person(
    session: SessionDep, current_user: CurrentUser, person_in: PersonCreate
) -> Any:
    """
    Create person profile for current user.
    """
    person_service = PersonService(session)

    # Check if user already has a person profile
    if person_service.user_has_person(current_user.id):
        raise HTTPException(
            status_code=400,
            detail="Person profile already exists for this user",
        )

    # Ensure user_id matches current user
    if person_in.user_id != current_user.id:
        raise HTTPException(
            status_code=400,
            detail="Cannot create person profile for another user",
        )

    person = person_service.create_person(person_in)
    return person


@router.post("/family-member", response_model=PersonPublic)
def create_family_member(
    session: SessionDep, current_user: CurrentUser, person_in: PersonCreate
) -> Any:
    """
    Create a family member (person without user account).
    """
    person_service = PersonService(session)

    # Family members should not have a user_id
    if person_in.user_id is not None:
        raise HTTPException(
            status_code=400,
            detail="Family members cannot have a user account",
        )

    # Set created_by_user_id to current user
    person_data = person_in.model_dump()
    person_data["created_by_user_id"] = current_user.id
    person = Person(**person_data)
    
    created_person = person_service.person_repo.create(person)
    return created_person


@router.post("/{person_id}/addresses", response_model=PersonAddressPublic)
def create_person_address(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    address_in: PersonAddressCreate,
) -> Any:
    """
    Create address for a specific person.
    User must be the creator of the person or a superuser.
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    # Check if user has permission (created the person or is superuser)
    if person.created_by_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to add address to this person",
        )

    address_service = PersonAddressService(session)
    address = address_service.create_address(person_id, address_in)
    return address


@router.post("/{person_id}/religion", response_model=PersonPublic)
def create_person_religion(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    religion_data: dict,
) -> Any:
    """
    Create religion for a specific person.
    User must be the creator of the person or a superuser.
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    # Check if user has permission (created the person or is superuser)
    if person.created_by_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to add religion to this person",
        )

    religion_service = PersonReligionService(session)
    religion_create = PersonReligionCreate(**religion_data)
    religion = religion_service.create_person_religion(person_id, religion_create)
    
    # Return the updated person
    return person_service.person_repo.get_by_id(person_id)


@router.patch("/me", response_model=PersonPublic)
def update_my_person(
    session: SessionDep, current_user: CurrentUser, person_in: PersonUpdate
) -> Any:
    """
    Update current user's person profile.
    """
    person_service = PersonService(session)

    person = person_service.get_person_by_user_id(current_user.id)
    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    updated_person = person_service.update_person(person, person_in)
    return updated_person


@router.delete("/me")
def delete_my_person(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete current user's person profile.
    """
    person_service = PersonService(session)

    person = person_service.get_person_by_user_id(current_user.id)
    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    person_service.delete_person(person)
    return {"message": "Person profile deleted successfully"}


# Admin endpoints
@router.get(
    "/{user_id}",
    response_model=PersonPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def get_person_by_user_id(session: SessionDep, user_id: uuid.UUID) -> Any:
    """
    Get person by user ID (admin only).
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(user_id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    return person


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_person_by_user_id(session: SessionDep, user_id: uuid.UUID) -> Any:
    """
    Delete person by user ID (admin only).
    """
    person_service = PersonService(session)

    person = person_service.get_person_by_user_id(user_id)
    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    person_service.delete_person(person)
    return {"message": "Person deleted successfully"}


# ============================================================================
# Person Address Endpoints
# ============================================================================


@router.get("/me/addresses", response_model=list[PersonAddressPublic])
def get_my_addresses(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get all addresses for current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    address_service = PersonAddressService(session)
    addresses = address_service.get_addresses_by_person(person.id)
    return addresses


@router.post("/me/addresses", response_model=PersonAddressPublic)
def create_my_address(
    session: SessionDep, current_user: CurrentUser, address_in: PersonAddressCreate
) -> Any:
    """
    Create new address for current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    address_service = PersonAddressService(session)
    address = address_service.create_address(person.id, address_in)  # Use person.id, not person.id
    return address


@router.get("/me/addresses/{address_id}", response_model=PersonAddressPublic)
def get_my_address(
    session: SessionDep, current_user: CurrentUser, address_id: uuid.UUID
) -> Any:
    """
    Get specific address by ID for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    address_service = PersonAddressService(session)
    address = address_service.get_address_by_id(address_id)

    if not address or address.person_id != person.id:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    return address


@router.patch("/me/addresses/{address_id}", response_model=PersonAddressPublic)
def update_my_address(
    session: SessionDep,
    current_user: CurrentUser,
    address_id: uuid.UUID,
    address_in: PersonAddressUpdate,
) -> Any:
    """
    Update address for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    address_service = PersonAddressService(session)
    address = address_service.get_address_by_id(address_id)

    if not address or address.person_id != person.id:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    updated_address = address_service.update_address(address, address_in)
    return updated_address


@router.delete("/me/addresses/{address_id}")
def delete_my_address(
    session: SessionDep, current_user: CurrentUser, address_id: uuid.UUID
) -> Any:
    """
    Delete address for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    address_service = PersonAddressService(session)
    address = address_service.get_address_by_id(address_id)

    if not address or address.person_id != person.id:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    address_service.delete_address(address)
    return {"message": "Address deleted successfully"}


# ============================================================================
# Person Profession Endpoints
# ============================================================================


@router.get("/me/professions", response_model=list[PersonProfessionPublic])
def get_my_professions(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get all professions for current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    profession_service = PersonProfessionService(session)
    professions = profession_service.get_professions_by_person(person.id)
    return professions


@router.post("/me/professions", response_model=PersonProfessionPublic)
def create_my_profession(
    session: SessionDep, current_user: CurrentUser, profession_in: PersonProfessionCreate
) -> Any:
    """
    Create new profession for current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    profession_service = PersonProfessionService(session)
    profession = profession_service.create_profession(person.id, profession_in)
    return profession


@router.get("/me/professions/{profession_id}", response_model=PersonProfessionPublic)
def get_my_profession(
    session: SessionDep, current_user: CurrentUser, profession_id: uuid.UUID
) -> Any:
    """
    Get specific profession by ID for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    profession_service = PersonProfessionService(session)
    profession = profession_service.get_profession_by_id(profession_id)

    if not profession or profession.person_id != person.id:
        raise HTTPException(
            status_code=404,
            detail="Profession not found",
        )

    return profession


@router.patch("/me/professions/{profession_id}", response_model=PersonProfessionPublic)
def update_my_profession(
    session: SessionDep,
    current_user: CurrentUser,
    profession_id: uuid.UUID,
    profession_in: PersonProfessionUpdate,
) -> Any:
    """
    Update profession for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    profession_service = PersonProfessionService(session)
    profession = profession_service.get_profession_by_id(profession_id)

    if not profession or profession.person_id != person.id:
        raise HTTPException(
            status_code=404,
            detail="Profession not found",
        )

    updated_profession = profession_service.update_profession(profession, profession_in)
    return updated_profession


@router.delete("/me/professions/{profession_id}")
def delete_my_profession(
    session: SessionDep, current_user: CurrentUser, profession_id: uuid.UUID
) -> Any:
    """
    Delete profession for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    profession_service = PersonProfessionService(session)
    profession = profession_service.get_profession_by_id(profession_id)

    if not profession or profession.person_id != person.id:
        raise HTTPException(
            status_code=404,
            detail="Profession not found",
        )

    profession_service.delete_profession(profession)
    return {"message": "Profession deleted successfully"}


# ============================================================================
# Person Relationship Endpoints
# ============================================================================


@router.get("/me/relationships", response_model=list[PersonRelationshipPublic])
def get_my_relationships(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get all relationships for current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    relationship_service = PersonRelationshipService(session)
    relationships = relationship_service.get_relationships_by_person(person.id)
    return relationships


@router.get("/me/relationships/with-details", response_model=list[PersonRelationshipWithDetails])
def get_my_relationships_with_details(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get all relationships for current user with full person details.
    Returns list of objects with relationship and related person information.
    """
    from app.schemas.person.person_relationship import PersonDetails
    
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    relationship_service = PersonRelationshipService(session)
    relationships = relationship_service.get_relationships_by_person(person.id)
    
    # Enrich each relationship with person details
    result = []
    for rel in relationships:
        related_person = person_service.person_repo.get_by_id(rel.related_person_id)
        if related_person:
            result.append(
                PersonRelationshipWithDetails(
                    relationship=rel,
                    person=PersonDetails(**related_person.model_dump())
                )
            )
    
    return result


@router.post("/me/relationships", response_model=PersonRelationshipPublic)
def create_my_relationship(
    session: SessionDep,
    current_user: CurrentUser,
    relationship_in: PersonRelationshipCreate,
) -> Any:
    """
    Create new relationship for current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    relationship_service = PersonRelationshipService(session)
    relationship = relationship_service.create_relationship(person.id, relationship_in)
    return relationship


@router.get("/me/relationships/{relationship_id}", response_model=PersonRelationshipPublic)
def get_my_relationship(
    session: SessionDep, current_user: CurrentUser, relationship_id: uuid.UUID
) -> Any:
    """
    Get specific relationship by ID for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    relationship_service = PersonRelationshipService(session)
    relationship = relationship_service.get_relationship_by_id(relationship_id)

    if not relationship or relationship.person_id != person.id:
        raise HTTPException(
            status_code=404,
            detail="Relationship not found",
        )

    return relationship


@router.patch("/me/relationships/{relationship_id}", response_model=PersonRelationshipPublic)
def update_my_relationship(
    session: SessionDep,
    current_user: CurrentUser,
    relationship_id: uuid.UUID,
    relationship_in: PersonRelationshipUpdate,
) -> Any:
    """
    Update relationship for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    relationship_service = PersonRelationshipService(session)
    relationship = relationship_service.get_relationship_by_id(relationship_id)

    if not relationship or relationship.person_id != person.id:
        raise HTTPException(
            status_code=404,
            detail="Relationship not found",
        )

    updated_relationship = relationship_service.update_relationship(
        relationship, relationship_in
    )
    return updated_relationship


@router.delete("/me/relationships/{relationship_id}")
def delete_my_relationship(
    session: SessionDep, current_user: CurrentUser, relationship_id: uuid.UUID
) -> Any:
    """
    Delete relationship for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    relationship_service = PersonRelationshipService(session)
    relationship = relationship_service.get_relationship_by_id(relationship_id)

    if not relationship or relationship.person_id != person.id:
        raise HTTPException(
            status_code=404,
            detail="Relationship not found",
        )

    relationship_service.delete_relationship(relationship)
    return {"message": "Relationship deleted successfully"}


# ============================================================================
# Person Metadata Endpoints
# ============================================================================


@router.get("/me/metadata", response_model=PersonMetadataPublic)
def get_my_metadata(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get metadata for current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    metadata_service = PersonMetadataService(session)
    metadata = metadata_service.get_metadata_by_person(person.id)

    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Person metadata not found",
        )

    return metadata


@router.post("/me/metadata", response_model=PersonMetadataPublic)
def create_my_metadata(
    session: SessionDep, current_user: CurrentUser, metadata_in: PersonMetadataCreate
) -> Any:
    """
    Create metadata for current user's person profile.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    metadata_service = PersonMetadataService(session)

    # Check if metadata already exists
    existing = metadata_service.get_metadata_by_person(person.id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Person metadata already exists",
        )

    metadata = metadata_service.create_metadata(person.id, metadata_in)
    return metadata


@router.patch("/me/metadata", response_model=PersonMetadataPublic)
def update_my_metadata(
    session: SessionDep, current_user: CurrentUser, metadata_in: PersonMetadataUpdate
) -> Any:
    """
    Update metadata for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    metadata_service = PersonMetadataService(session)
    metadata = metadata_service.get_metadata_by_person(person.id)

    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Person metadata not found",
        )

    updated_metadata = metadata_service.update_metadata(metadata, metadata_in)
    return updated_metadata


@router.delete("/me/metadata")
def delete_my_metadata(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete metadata for current user.
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(current_user.id)

    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person profile not found",
        )

    metadata_service = PersonMetadataService(session)
    metadata = metadata_service.get_metadata_by_person(person.id)

    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Person metadata not found",
        )

    metadata_service.delete_metadata(metadata)
    return {"message": "Person metadata deleted successfully"}

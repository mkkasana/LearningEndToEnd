"""Person API routes."""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import CurrentUser, SessionDep, get_current_active_admin
from app.db_models.person.person import Person
from app.schemas.person import (
    CanAssumeResponse,
    PersonAddressCreate,
    PersonAddressPublic,
    PersonAddressUpdate,
    PersonCompleteDetailsResponse,
    PersonContributionPublic,
    PersonCreate,
    PersonDiscoveryResult,
    PersonMatchResult,
    PersonMetadataCreate,
    PersonMetadataPublic,
    PersonMetadataUpdate,
    PersonProfessionCreate,
    PersonProfessionPublic,
    PersonProfessionUpdate,
    PersonPublic,
    PersonRelationshipCreate,
    PersonRelationshipPublic,
    PersonRelationshipsWithDetailsResponse,
    PersonRelationshipUpdate,
    PersonRelationshipWithDetails,
    PersonReligionCreate,
    PersonSearchRequest,
    PersonUpdate,
)
from app.services.person import (
    PersonAddressService,
    PersonDiscoveryService,
    PersonMatchingService,
    PersonMetadataService,
    PersonProfessionService,
    PersonRelationshipService,
    PersonReligionService,
    PersonService,
)
from app.utils.logging_decorator import log_route
from app.utils.person_permissions import validate_person_access

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# IMPORTANT: Route Order Matters!
# All /me/* routes MUST be defined BEFORE /{person_id}/* routes
# FastAPI matches routes in order, so /me must come first to avoid
# "me" being parsed as a UUID for /{person_id} routes
# ============================================================================


# ============================================================================
# /me Endpoints - Current User's Person Profile
# ============================================================================


@router.get("/me", response_model=PersonPublic)
@log_route
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
@log_route
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


# ============================================================================
# /me/addresses Endpoints
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
    address = address_service.create_address(person.id, address_in)
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
# /me/professions Endpoints
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
    session: SessionDep,
    current_user: CurrentUser,
    profession_in: PersonProfessionCreate,
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
# /me/relationships Endpoints
# ============================================================================


@router.get("/me/relationships", response_model=list[PersonRelationshipPublic])
@log_route
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


@router.get(
    "/me/relationships/with-details",
    response_model=PersonRelationshipsWithDetailsResponse,
)
def get_my_relationships_with_details(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get all relationships for current user with full person details.
    Returns the selected person and list of objects with relationship and related person information.
    """
    from app.schemas.person.person_relationship import (
        PersonDetails,
        PersonRelationshipsWithDetailsResponse,
    )

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
        # Skip inactive persons (e.g., temporary persons pending approval)
        if related_person and (
            not hasattr(related_person, "is_active") or related_person.is_active
        ):
            result.append(
                PersonRelationshipWithDetails(
                    relationship=rel,
                    person=PersonDetails(**related_person.model_dump()),
                )
            )

    return PersonRelationshipsWithDetailsResponse(
        selected_person=PersonDetails(**person.model_dump()), relationships=result
    )


@router.post("/me/relationships", response_model=PersonRelationshipPublic)
@log_route
def create_my_relationship(
    session: SessionDep,
    current_user: CurrentUser,
    relationship_in: PersonRelationshipCreate,
) -> Any:
    """
    Create new relationship for current user's person profile.

    **Bidirectional Relationships:**
    This endpoint automatically creates both directions of the relationship:
    - Primary relationship: Person A → Person B (as specified)
    - Inverse relationship: Person B → Person A (automatically determined)
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


@router.get(
    "/me/relationships/{relationship_id}", response_model=PersonRelationshipPublic
)
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


@router.patch(
    "/me/relationships/{relationship_id}", response_model=PersonRelationshipPublic
)
def update_my_relationship(
    session: SessionDep,
    current_user: CurrentUser,
    relationship_id: uuid.UUID,
    relationship_in: PersonRelationshipUpdate,
) -> Any:
    """
    Update relationship for current user.

    **Bidirectional Updates:**
    This endpoint automatically updates both directions of the relationship.
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

    **Bidirectional Deletion:**
    This endpoint automatically deletes both directions of the relationship.
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
# /me/metadata Endpoints
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


# ============================================================================
# Other Static Path Endpoints (before /{person_id} routes)
# ============================================================================


@router.get("/my-contributions", response_model=list[PersonContributionPublic])
@log_route
def get_my_contributions(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Get all persons created by the current user with view statistics.
    """
    person_service = PersonService(session)
    contributions = person_service.get_my_contributions(current_user.id)

    logger.info(
        f"Retrieved {len(contributions)} contributions for user {current_user.email}"
    )

    return contributions


@router.post("/family-member", response_model=PersonPublic)
@log_route
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


@router.post("/search-matches", response_model=list[PersonMatchResult])
@log_route
def search_matching_persons(
    session: SessionDep,
    current_user: CurrentUser,
    search_request: PersonSearchRequest,
) -> Any:
    """
    Search for existing persons matching the provided criteria.
    """
    logger.info(
        f"Person search request from user {current_user.email}: "
        f"name={search_request.first_name} {search_request.last_name}, "
        f"country={search_request.country_id}, state={search_request.state_id}, "
        f"district={search_request.district_id}, religion={search_request.religion_id}"
    )

    try:
        matching_service = PersonMatchingService(session)
        matches = matching_service.search_matching_persons(
            current_user_id=current_user.id,
            search_criteria=search_request,
        )

        logger.info(
            f"Found {len(matches)} matching persons for user {current_user.email}"
        )
        return matches

    except ValueError as e:
        logger.error(
            f"Validation error in person search for user {current_user.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=422,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(
            f"Unexpected error in person search for user {current_user.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred while searching for matching persons",
        )


@router.get("/discover-family-members", response_model=list[PersonDiscoveryResult])
@log_route
def discover_family_members(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Discover potential family member connections for the current user.
    """
    logger.info(
        f"Discovery request from user {current_user.email} (ID: {current_user.id})"
    )

    try:
        discovery_service = PersonDiscoveryService(session)
        discoveries = discovery_service.discover_family_members(current_user.id)

        logger.info(
            f"Found {len(discoveries)} potential connections for user {current_user.email}"
        )
        return discoveries

    except Exception as e:
        logger.exception(
            f"Error in family member discovery for user {current_user.email} (ID: {current_user.id}): {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred while discovering family members. Please try again later.",
        )


# ============================================================================
# /{person_id} Endpoints - Person-Specific Operations
# IMPORTANT: These MUST come AFTER all /me/* routes
# ============================================================================


# ============================================================================
# /{person_id}/addresses Endpoints
# ============================================================================


@router.get("/{person_id}/addresses", response_model=list[PersonAddressPublic])
def get_person_addresses(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
) -> Any:
    """
    Get all addresses for a specific person.
    _Requirements: 3.1, 3.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    address_service = PersonAddressService(session)
    addresses = address_service.get_addresses_by_person(person_id)
    return addresses


@router.post("/{person_id}/addresses", response_model=PersonAddressPublic)
def create_person_address(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    address_in: PersonAddressCreate,
) -> Any:
    """
    Create address for a specific person.
    _Requirements: 3.2, 3.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    address_service = PersonAddressService(session)
    address = address_service.create_address(person_id, address_in)
    return address


@router.patch("/{person_id}/addresses/{address_id}", response_model=PersonAddressPublic)
def update_person_address(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    address_id: uuid.UUID,
    address_in: PersonAddressUpdate,
) -> Any:
    """
    Update address for a specific person.
    _Requirements: 3.3, 3.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    address_service = PersonAddressService(session)
    address = address_service.get_address_by_id(address_id)

    if not address or address.person_id != person_id:
        raise HTTPException(status_code=404, detail="Address not found")

    updated_address = address_service.update_address(address, address_in)
    return updated_address


@router.delete("/{person_id}/addresses/{address_id}")
def delete_person_address(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    address_id: uuid.UUID,
) -> Any:
    """
    Delete address for a specific person.
    _Requirements: 3.4, 3.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    address_service = PersonAddressService(session)
    address = address_service.get_address_by_id(address_id)

    if not address or address.person_id != person_id:
        raise HTTPException(status_code=404, detail="Address not found")

    address_service.delete_address(address)
    return {"message": "Address deleted successfully"}


# ============================================================================
# /{person_id}/professions Endpoints
# ============================================================================


@router.get("/{person_id}/professions", response_model=list[PersonProfessionPublic])
def get_person_professions(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
) -> Any:
    """
    Get all professions for a specific person.
    _Requirements: 4.1, 4.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    profession_service = PersonProfessionService(session)
    professions = profession_service.get_professions_by_person(person_id)
    return professions


@router.post("/{person_id}/professions", response_model=PersonProfessionPublic)
def create_person_profession(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    profession_in: PersonProfessionCreate,
) -> Any:
    """
    Create profession for a specific person.
    _Requirements: 4.2, 4.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    profession_service = PersonProfessionService(session)
    profession = profession_service.create_profession(person_id, profession_in)
    return profession


@router.patch(
    "/{person_id}/professions/{profession_id}", response_model=PersonProfessionPublic
)
def update_person_profession(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    profession_id: uuid.UUID,
    profession_in: PersonProfessionUpdate,
) -> Any:
    """
    Update profession for a specific person.
    _Requirements: 4.3, 4.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    profession_service = PersonProfessionService(session)
    profession = profession_service.get_profession_by_id(profession_id)

    if not profession or profession.person_id != person_id:
        raise HTTPException(status_code=404, detail="Profession not found")

    updated_profession = profession_service.update_profession(profession, profession_in)
    return updated_profession


@router.delete("/{person_id}/professions/{profession_id}")
def delete_person_profession(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    profession_id: uuid.UUID,
) -> Any:
    """
    Delete profession for a specific person.
    _Requirements: 4.4, 4.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    profession_service = PersonProfessionService(session)
    profession = profession_service.get_profession_by_id(profession_id)

    if not profession or profession.person_id != person_id:
        raise HTTPException(status_code=404, detail="Profession not found")

    profession_service.delete_profession(profession)
    return {"message": "Profession deleted successfully"}


# ============================================================================
# /{person_id}/metadata Endpoints
# ============================================================================


@router.get("/{person_id}/metadata", response_model=PersonMetadataPublic)
def get_person_metadata(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
) -> Any:
    """
    Get metadata for a specific person.
    _Requirements: 5.1, 5.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    metadata_service = PersonMetadataService(session)
    metadata = metadata_service.get_metadata_by_person(person_id)

    if not metadata:
        raise HTTPException(status_code=404, detail="Person metadata not found")

    return metadata


@router.post("/{person_id}/metadata", response_model=PersonMetadataPublic)
def create_person_metadata(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    metadata_in: PersonMetadataCreate,
) -> Any:
    """
    Create metadata for a specific person.
    _Requirements: 5.2, 5.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    metadata_service = PersonMetadataService(session)

    existing = metadata_service.get_metadata_by_person(person_id)
    if existing:
        raise HTTPException(status_code=400, detail="Person metadata already exists")

    metadata = metadata_service.create_metadata(person_id, metadata_in)
    return metadata


@router.patch("/{person_id}/metadata", response_model=PersonMetadataPublic)
def update_person_metadata(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    metadata_in: PersonMetadataUpdate,
) -> Any:
    """
    Update metadata for a specific person.
    _Requirements: 5.3, 5.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    metadata_service = PersonMetadataService(session)
    metadata = metadata_service.get_metadata_by_person(person_id)

    if not metadata:
        raise HTTPException(status_code=404, detail="Person metadata not found")

    updated_metadata = metadata_service.update_metadata(metadata, metadata_in)
    return updated_metadata


@router.delete("/{person_id}/metadata")
def delete_person_metadata(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
) -> Any:
    """
    Delete metadata for a specific person.
    _Requirements: 5.4, 5.5_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    metadata_service = PersonMetadataService(session)
    metadata = metadata_service.get_metadata_by_person(person_id)

    if not metadata:
        raise HTTPException(status_code=404, detail="Person metadata not found")

    metadata_service.delete_metadata(metadata)
    return {"message": "Person metadata deleted successfully"}


# ============================================================================
# /{person_id}/can-assume Endpoint - Assume Person Role Feature
# ============================================================================


@router.get("/{person_id}/can-assume", response_model=CanAssumeResponse)
@log_route
def can_assume_person(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
) -> Any:
    """
    Check if current user can assume the role of a specific person.

    Requirements for assuming a person's role:
    - User must have SUPERUSER or ADMIN role (elevated user)
    - Person must have been created by this user (created_by_user_id matches)

    Returns:
        CanAssumeResponse with can_assume boolean and reason if denied.

    _Requirements: 1.1, 1.2, 2.1, 2.4_
    """
    from app.enums.user_role import UserRole

    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)

    # Check if person exists
    if not person:
        return CanAssumeResponse(
            can_assume=False,
            reason="person_not_found",
            person_name=None,
        )

    # Check if user is elevated (SUPERUSER or ADMIN)
    # Requirements: 1.1, 1.2
    if not current_user.role.has_permission(UserRole.SUPERUSER):
        logger.info(
            f"User {current_user.email} (role={current_user.role.value}) "
            f"denied assume for person {person_id}: not elevated user"
        )
        return CanAssumeResponse(
            can_assume=False,
            reason="not_elevated_user",
            person_name=None,
        )

    # Check if user created this person
    # Requirements: 2.1, 2.4
    if person.created_by_user_id != current_user.id:
        logger.info(
            f"User {current_user.email} denied assume for person {person_id}: "
            f"not creator (created_by={person.created_by_user_id})"
        )
        return CanAssumeResponse(
            can_assume=False,
            reason="not_creator",
            person_name=None,
        )

    # User can assume this person's role
    person_name = f"{person.first_name} {person.last_name}"
    logger.info(
        f"User {current_user.email} can assume person {person_id} ({person_name})"
    )

    return CanAssumeResponse(
        can_assume=True,
        reason=None,
        person_name=person_name,
    )


# ============================================================================
# /{person_id}/discover-family-members Endpoint - Assume Person Role Feature
# ============================================================================


@router.get(
    "/{person_id}/discover-family-members", response_model=list[PersonDiscoveryResult]
)
@log_route
def discover_person_family_members(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
) -> Any:
    """
    Discover potential family member connections for a specific person.

    This endpoint enables the "assume person role" feature where elevated users
    can discover family members for persons they created, allowing them to build
    multi-generational family trees.

    Authorization:
    - User must have permission to access the person (via validate_person_access)
    - This includes: user's own person, persons they created, or admin access

    _Requirements: 5.1, 5.2_
    """
    logger.info(
        f"Discovery request for person {person_id} from user {current_user.email} "
        f"(ID: {current_user.id})"
    )

    # Validate user has permission to access this person
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    try:
        discovery_service = PersonDiscoveryService(session)
        discoveries = discovery_service.discover_family_members(
            current_user_id=current_user.id, person_id=person_id
        )

        logger.info(
            f"Found {len(discoveries)} potential connections for person {person_id} "
            f"(requested by user {current_user.email})"
        )
        return discoveries

    except Exception as e:
        logger.exception(
            f"Error in family member discovery for person {person_id} "
            f"(requested by user {current_user.email}): {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred while discovering family members. Please try again later.",
        )


# ============================================================================
# /{person_id}/relationships Endpoints
# ============================================================================


@router.get("/{person_id}/relationships", response_model=list[PersonRelationshipPublic])
@log_route
def get_person_relationships(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
) -> Any:
    """
    Get all relationships for a specific person.
    _Requirements: 2.2, 2.4_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    relationship_service = PersonRelationshipService(session)
    relationships = relationship_service.get_relationships_by_person(person_id)
    return relationships


@router.post("/{person_id}/relationships", response_model=PersonRelationshipPublic)
@log_route
def create_person_relationship(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    relationship_in: PersonRelationshipCreate,
) -> Any:
    """
    Create relationship for a specific person.
    _Requirements: 2.1, 2.4, 2.5, 2.6_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    relationship_service = PersonRelationshipService(session)
    relationship = relationship_service.create_relationship(person_id, relationship_in)
    return relationship


@router.delete("/{person_id}/relationships/{relationship_id}")
@log_route
def delete_person_relationship(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    relationship_id: uuid.UUID,
) -> Any:
    """
    Delete relationship for a specific person.

    This endpoint enables the "assume person role" feature where elevated users
    can delete relationships for persons they created.

    **Bidirectional Deletion:**
    This endpoint automatically deletes both directions of the relationship.

    Authorization:
    - User must have permission to access the person (via validate_person_access)
    - This includes: user's own person, persons they created, or admin access

    _Requirements: 5.1, 5.2 (assume-person-role)_
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)
    validate_person_access(person, current_user)

    relationship_service = PersonRelationshipService(session)
    relationship = relationship_service.get_relationship_by_id(relationship_id)

    if not relationship or relationship.person_id != person_id:
        raise HTTPException(
            status_code=404,
            detail="Relationship not found",
        )

    relationship_service.delete_relationship(relationship)

    logger.info(
        f"User {current_user.email} deleted relationship {relationship_id} "
        f"for person {person_id}"
    )

    return {"message": "Relationship deleted successfully"}


@router.get(
    "/{person_id}/relationships/with-details",
    response_model=PersonRelationshipsWithDetailsResponse,
)
def get_person_relationships_with_details(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
) -> Any:
    """
    Get all relationships for a specific person with full person details.
    This endpoint is open to all authenticated users for viewing family tree data.
    _Requirements: 2.3_
    """
    from app.schemas.person.person_relationship import (
        PersonDetails,
        PersonRelationshipsWithDetailsResponse,
    )
    from app.services.profile_view_tracking_service import ProfileViewTrackingService

    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    # Record profile view (non-blocking, fail gracefully)
    try:
        viewer_person = person_service.get_person_by_user_id(current_user.id)
        if viewer_person:
            view_tracking_service = ProfileViewTrackingService(session)
            view_tracking_service.record_view(
                viewer_person_id=viewer_person.id, viewed_person_id=person_id
            )
            logger.info(
                f"Recorded profile view: viewer={viewer_person.id}, viewed={person_id}"
            )
    except Exception as e:
        logger.error(f"Failed to record profile view: {e}", exc_info=True)

    session.refresh(person)

    relationship_service = PersonRelationshipService(session)
    relationships = relationship_service.get_relationships_by_person(person_id)

    result = []
    for rel in relationships:
        related_person = person_service.person_repo.get_by_id(rel.related_person_id)
        # Skip inactive persons (e.g., temporary persons pending approval)
        if related_person and (
            not hasattr(related_person, "is_active") or related_person.is_active
        ):
            result.append(
                PersonRelationshipWithDetails(
                    relationship=rel,
                    person=PersonDetails(**related_person.model_dump()),
                )
            )

    return PersonRelationshipsWithDetailsResponse(
        selected_person=PersonDetails(**person.model_dump()), relationships=result
    )


@router.get(
    "/{person_id}/complete-details",
    response_model=PersonCompleteDetailsResponse,
)
@log_route
def get_person_complete_details(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
) -> Any:
    """
    Get complete details for a specific person with resolved names.
    """
    person_service = PersonService(session)
    complete_details = person_service.get_person_complete_details(person_id)

    if not complete_details:
        raise HTTPException(status_code=404, detail="Person not found")

    logger.info(
        f"Retrieved complete details for person {person_id} "
        f"by user {current_user.email}"
    )

    return complete_details


@router.post("/{person_id}/religion", response_model=PersonPublic)
def create_person_religion(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    religion_data: dict[str, Any],
) -> Any:
    """
    Create religion for a specific person.
    User must be the creator of the person or a superuser.
    """
    person_service = PersonService(session)
    person = person_service.person_repo.get_by_id(person_id)

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    if person.created_by_user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to add religion to this person",
        )

    religion_service = PersonReligionService(session)
    religion_create = PersonReligionCreate(**religion_data)
    religion_service.create_person_religion(person_id, religion_create)

    return person_service.person_repo.get_by_id(person_id)


# ============================================================================
# Admin Endpoints (/{user_id} - admin only)
# ============================================================================


@router.get(
    "/{user_id}",
    response_model=PersonPublic,
    dependencies=[Depends(get_current_active_admin)],
)
def get_person_by_user_id(session: SessionDep, user_id: uuid.UUID) -> Any:
    """
    Get person by user ID (admin only).
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(user_id)

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    return person


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_admin)],
)
def delete_person_by_user_id(session: SessionDep, user_id: uuid.UUID) -> Any:
    """
    Delete person by user ID (admin only).
    """
    person_service = PersonService(session)
    person = person_service.get_person_by_user_id(user_id)

    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    person_service.delete_person(person)
    return {"message": "Person deleted successfully"}

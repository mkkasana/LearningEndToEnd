"""Person API routes."""

import logging
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

logger = logging.getLogger(__name__)
router = APIRouter()


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

    Returns list of potential matches with scores, sorted by match score descending.
    Used to prevent duplicate person records when adding family members.
    """
    logger.info(
        f"Person search request from user {current_user.email}: "
        f"name={search_request.first_name} {search_request.last_name}, "
        f"country={search_request.country_id}, state={search_request.state_id}, "
        f"district={search_request.district_id}, religion={search_request.religion_id}"
    )

    try:
        # Instantiate PersonMatchingService
        matching_service = PersonMatchingService(session)

        # Call search_matching_persons method
        matches = matching_service.search_matching_persons(
            current_user_id=current_user.id,
            search_criteria=search_request,
        )

        logger.info(
            f"Found {len(matches)} matching persons for user {current_user.email}"
        )
        return matches

    except ValueError as e:
        # Handle validation errors
        logger.error(
            f"Validation error in person search for user {current_user.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=422,
            detail=str(e),
        )
    except Exception as e:
        # Handle unexpected errors
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
    
    This endpoint analyzes existing relationships to find persons who are:
    - Connected to the user's family members
    - Not yet directly connected to the user
    
    Discovery patterns:
    1. Spouse's children → Suggested as user's Son/Daughter
    2. Parent's spouse → Suggested as user's Father/Mother
    3. Child's parent → Suggested as user's Spouse
    
    Returns:
        List of discovered persons with inferred relationship types,
        sorted by relationship proximity and type priority.
        Limited to top 20 results.
    """
    logger.info(f"Discovery request from user {current_user.email}")
    
    try:
        discovery_service = PersonDiscoveryService(session)
        discoveries = discovery_service.discover_family_members(current_user.id)
        
        logger.info(
            f"Found {len(discoveries)} potential connections for user {current_user.email}"
        )
        return discoveries
        
    except Exception as e:
        logger.exception(
            f"Error in family member discovery for user {current_user.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred while discovering family members",
        )


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
    religion_data: dict[str, Any],
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
    religion_service.create_person_religion(person_id, religion_create)

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
    address = address_service.create_address(
        person.id, address_in
    )  # Use person.id, not person.id
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
# Person Relationship Endpoints
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
        if related_person:
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
    "/{person_id}/relationships/with-details",
    response_model=PersonRelationshipsWithDetailsResponse,
)
def get_person_relationships_with_details(
    session: SessionDep,
    current_user: CurrentUser,  # noqa: ARG001
    person_id: uuid.UUID,
) -> Any:
    """
    Get all relationships for a specific person with full person details.
    Returns the selected person and list of objects with relationship and related person information.
    Used to help users identify the correct person when multiple people have similar names.
    """
    from app.schemas.person.person_relationship import (
        PersonDetails,
        PersonRelationshipsWithDetailsResponse,
    )

    person_service = PersonService(session)

    # Verify the person exists
    person = person_service.person_repo.get_by_id(person_id)
    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found",
        )

    relationship_service = PersonRelationshipService(session)
    relationships = relationship_service.get_relationships_by_person(person_id)

    # Enrich each relationship with person details
    result = []
    for rel in relationships:
        related_person = person_service.person_repo.get_by_id(rel.related_person_id)
        if related_person:
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

    **Inverse Relationship Logic:**
    The system determines the correct inverse relationship type based on:
    - The primary relationship type
    - Both persons' genders (when applicable)

    **Examples:**

    1. Parent-Child Relationships (gender-dependent):
       - Create: A → B as "Father" (B is A's father)
       - System creates: B → A as "Son" (if A is male) or "Daughter" (if A is female)

       - Create: A → B as "Mother" (B is A's mother)
       - System creates: B → A as "Son" (if A is male) or "Daughter" (if A is female)

       - Create: A → B as "Son" (B is A's son)
       - System creates: B → A as "Father" (if A is male) or "Mother" (if A is female)

       - Create: A → B as "Daughter" (B is A's daughter)
       - System creates: B → A as "Father" (if A is male) or "Mother" (if A is female)

    2. Spouse Relationships (gender-independent):
       - Create: A → B as "Husband" (B is A's husband)
       - System creates: B → A as "Wife" (A is B's wife)

       - Create: A → B as "Wife" (B is A's wife)
       - System creates: B → A as "Husband" (A is B's husband)

       - Create: A → B as "Spouse" (B is A's spouse)
       - System creates: B → A as "Spouse" (A is B's spouse)

    **Result:**
    Both persons will see each other in their family trees with the correct relationship type.
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
    This endpoint automatically updates both directions of the relationship:
    - Updates the primary relationship (the one you're modifying)
    - Finds and updates the inverse relationship automatically

    **Synchronized Fields:**
    The following fields are synchronized across both directions:
    - `is_active`: When you activate/deactivate a relationship, both directions are updated
    - `start_date`: Changes to start date are reflected in both directions
    - `end_date`: Changes to end date are reflected in both directions
    - `updated_at`: Timestamp is updated for both relationships

    **Non-Synchronized Fields:**
    - `relationship_type`: Each direction maintains its own correct type (e.g., Father/Son)

    **Examples:**

    1. Deactivating a relationship:
       - Update: A → B relationship, set `is_active=False`
       - System updates: B → A relationship, also sets `is_active=False`
       - Result: Neither person sees the relationship in their family tree

    2. Updating dates:
       - Update: A → B relationship, set `start_date="2020-01-01"`
       - System updates: B → A relationship, also sets `start_date="2020-01-01"`
       - Result: Both directions show the same date range

    **Graceful Handling:**
    If the inverse relationship is not found (e.g., legacy data), the system:
    - Logs a warning
    - Continues with updating the primary relationship
    - Does not fail the request
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
    This endpoint automatically deletes both directions of the relationship:
    - Deletes the primary relationship (the one you're removing)
    - Finds and deletes the inverse relationship automatically

    **Transaction Safety:**
    Both deletions are performed within a database transaction:
    - If both deletions succeed, changes are committed
    - If either deletion fails, all changes are rolled back
    - Ensures data consistency (no orphaned relationships)

    **Soft Delete Support:**
    If using soft delete (setting `is_active=False` instead of removing records):
    - Both directions are soft-deleted together
    - Maintains referential integrity

    **Examples:**

    1. Hard delete:
       - Delete: A → B relationship (Father)
       - System deletes: B → A relationship (Son/Daughter)
       - Result: Both records are removed from the database

    2. Soft delete:
       - Delete: A → B relationship (sets `is_active=False`)
       - System updates: B → A relationship (also sets `is_active=False`)
       - Result: Both relationships are hidden but data is preserved

    **Graceful Handling:**
    If the inverse relationship is not found (e.g., legacy data), the system:
    - Logs a warning
    - Continues with deleting the primary relationship
    - Does not fail the request

    **Result:**
    Neither person will see the relationship in their family tree after deletion.
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

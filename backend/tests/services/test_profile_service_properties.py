"""Property-based tests for Profile Service.

**Feature: person-attachment-signup-flow**
**Validates: Requirements 2.2, 5.1, 5.2, 5.3, 5.4, 7.2, 7.3, 7.4, 7.5, 8.2, 8.3, 8.4**
"""

import uuid
from datetime import date

import pytest
from fastapi import HTTPException
from hypothesis import HealthCheck, given, settings, Phase
from hypothesis import strategies as st
from sqlmodel import Session, select, delete

from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_attachment_request import PersonAttachmentRequest
from app.db_models.person.person_religion import PersonReligion
from app.db_models.address.country import Country
from app.db_models.address.state import State
from app.db_models.address.district import District
from app.db_models.address.sub_district import SubDistrict
from app.db_models.religion.religion import Religion
from app.db_models.religion.religion_category import ReligionCategory
from app.enums.attachment_request_status import AttachmentRequestStatus
from app.enums.marital_status import MaritalStatus
from app.models import User
from app.services.profile_service import ProfileService


class BaseProfilePropertyTest:
    """Base class for profile service property tests."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, db: Session):
        db.rollback()
        yield
        db.rollback()

    def _get_fixtures(self, db: Session) -> dict:
        """Get required fixtures from database."""
        gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
        country = db.exec(select(Country).limit(1)).first()
        state = db.exec(select(State).limit(1)).first() if country else None
        district = db.exec(select(District).limit(1)).first() if state else None
        sub_district = db.exec(select(SubDistrict).limit(1)).first() if district else None
        religion = db.exec(select(Religion).limit(1)).first()
        religion_category = db.exec(select(ReligionCategory).limit(1)).first() if religion else None
        return {
            "gender": gender, "country": country, "state": state,
            "district": district, "sub_district": sub_district,
            "religion": religion, "religion_category": religion_category,
        }

    def _create_user(self, db: Session) -> User:
        """Create a test user."""
        user = User(
            email=f"test_{uuid.uuid4()}@example.com",
            hashed_password="test_password",
            is_active=True, is_superuser=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def _create_person(
        self, db: Session, fixtures: dict, user: User | None, created_by: User,
        is_primary: bool = False, is_active: bool = True,
        marital_status: MaritalStatus = MaritalStatus.SINGLE
    ) -> Person:
        """Create a test person."""
        person = Person(
            user_id=user.id if user else None,
            created_by_user_id=created_by.id,
            is_primary=is_primary,
            first_name=f"Test{uuid.uuid4().hex[:4]}",
            last_name="Person",
            gender_id=fixtures["gender"].id,
            date_of_birth=date(1990, 1, 1),
            is_active=is_active,
            marital_status=marital_status,
        )
        db.add(person)
        db.commit()
        db.refresh(person)
        return person

    def _create_address(self, db: Session, fixtures: dict, person_id: uuid.UUID) -> PersonAddress:
        """Create a test address for a person."""
        address = PersonAddress(
            person_id=person_id,
            country_id=fixtures["country"].id,
            state_id=fixtures["state"].id,
            district_id=fixtures["district"].id,
            sub_district_id=fixtures["sub_district"].id,
            start_date=date(2020, 1, 1),
            is_current=True,
        )
        db.add(address)
        db.commit()
        db.refresh(address)
        return address

    def _create_religion(self, db: Session, fixtures: dict, person_id: uuid.UUID) -> PersonReligion:
        """Create a test religion for a person."""
        religion = PersonReligion(
            person_id=person_id,
            religion_id=fixtures["religion"].id,
            religion_category_id=fixtures["religion_category"].id,
        )
        db.add(religion)
        db.commit()
        db.refresh(religion)
        return religion

    def _create_attachment_request(
        self, db: Session, requester_user_id: uuid.UUID, requester_person_id: uuid.UUID,
        target_person_id: uuid.UUID, approver_user_id: uuid.UUID,
        status: AttachmentRequestStatus = AttachmentRequestStatus.PENDING
    ) -> PersonAttachmentRequest:
        """Create a test attachment request."""
        request = PersonAttachmentRequest(
            requester_user_id=requester_user_id,
            requester_person_id=requester_person_id,
            target_person_id=target_person_id,
            approver_user_id=approver_user_id,
            status=status,
        )
        db.add(request)
        db.commit()
        db.refresh(request)
        return request

    def _cleanup_person(self, db: Session, person_id: uuid.UUID):
        """Clean up a person and related records."""
        db.execute(delete(PersonAddress).where(PersonAddress.person_id == person_id))
        db.execute(delete(PersonReligion).where(PersonReligion.person_id == person_id))
        db.execute(delete(Person).where(Person.id == person_id))
        db.commit()

    def _cleanup_user(self, db: Session, user_id: uuid.UUID):
        """Clean up a user."""
        db.execute(delete(User).where(User.id == user_id))
        db.commit()

    def _cleanup_request(self, db: Session, request_id: uuid.UUID):
        """Clean up an attachment request."""
        db.execute(delete(PersonAttachmentRequest).where(PersonAttachmentRequest.id == request_id))
        db.commit()


class TestProfileCompletionStatusAccuracy(BaseProfilePropertyTest):
    """Property 2: Profile Completion Status Accuracy.
    
    *For any* user, the profile completion status SHALL accurately reflect:
    - `has_duplicate_check` is `True` if and only if the user's Person is active OR user has a pending attachment request
    - `has_pending_attachment_request` is `True` if and only if the user has a PENDING attachment request
    - `is_complete` is `True` if and only if all profile fields are complete AND `has_duplicate_check` is `True` AND `has_pending_attachment_request` is `False`
    
    **Validates: Requirements 2.2, 5.1, 5.2, 5.3, 5.4**
    """

    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target],
        database=None,
        deadline=None,
    )
    @given(
        is_active=st.booleans(),
        has_pending_request=st.booleans(),
        has_address=st.booleans(),
        has_religion=st.booleans(),
        marital_status=st.sampled_from([MaritalStatus.SINGLE, MaritalStatus.MARRIED, MaritalStatus.UNKNOWN]),
    )
    def test_profile_completion_status_accuracy(
        self, db: Session, is_active: bool, has_pending_request: bool,
        has_address: bool, has_religion: bool, marital_status: MaritalStatus
    ):
        """Property: Profile completion status accurately reflects user state."""
        db.rollback()
        fixtures = self._get_fixtures(db)
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available")

        user = self._create_user(db)
        approver = self._create_user(db)
        person = self._create_person(
            db, fixtures, user, user, is_primary=True,
            is_active=is_active, marital_status=marital_status
        )
        
        # Create address if needed
        if has_address:
            self._create_address(db, fixtures, person.id)
        
        # Create religion if needed
        if has_religion:
            self._create_religion(db, fixtures, person.id)
        
        # Create pending request if needed
        request = None
        target_person = None
        if has_pending_request:
            target_person = self._create_person(db, fixtures, None, approver, is_active=True)
            request = self._create_attachment_request(
                db, user.id, person.id, target_person.id, approver.id,
                AttachmentRequestStatus.PENDING
            )

        try:
            service = ProfileService(db)
            result = service.check_profile_completion(user.id)

            # Property 1: has_duplicate_check is True iff person is active OR has pending request
            expected_has_duplicate_check = is_active or has_pending_request
            assert result.has_duplicate_check == expected_has_duplicate_check, (
                f"has_duplicate_check should be {expected_has_duplicate_check} "
                f"(is_active={is_active}, has_pending_request={has_pending_request})"
            )

            # Property 2: has_pending_attachment_request is True iff has PENDING request
            assert result.has_pending_attachment_request == has_pending_request, (
                f"has_pending_attachment_request should be {has_pending_request}"
            )

            # Property 3: is_complete is True iff all fields complete AND has_duplicate_check AND NOT has_pending_request
            has_marital = marital_status != MaritalStatus.UNKNOWN
            expected_is_complete = (
                has_address and has_religion and has_marital and
                expected_has_duplicate_check and not has_pending_request
            )
            assert result.is_complete == expected_is_complete, (
                f"is_complete should be {expected_is_complete} "
                f"(has_address={has_address}, has_religion={has_religion}, "
                f"has_marital={has_marital}, has_duplicate_check={expected_has_duplicate_check}, "
                f"has_pending_request={has_pending_request})"
            )

        finally:
            if request:
                self._cleanup_request(db, request.id)
            if target_person:
                self._cleanup_person(db, target_person.id)
            self._cleanup_person(db, person.id)
            self._cleanup_user(db, user.id)
            self._cleanup_user(db, approver.id)


class TestDuplicateCheckResultsFiltering(BaseProfilePropertyTest):
    """Property 3: Duplicate Check Results Filtering.
    
    *For any* call to the duplicate-check endpoint, all returned persons SHALL:
    - NOT be the current user's own Person record
    - NOT have a linked user account (user_id is NULL)
    - Have a match score >= 40%
    - Be active persons (is_active = True)
    
    **Validates: Requirements 3.2, 7.2, 7.3, 7.4, 7.5**
    """

    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target],
        database=None,
        deadline=None,
    )
    @given(
        num_potential_matches=st.integers(min_value=0, max_value=3),
        include_linked_person=st.booleans(),
    )
    def test_duplicate_check_filters_correctly(
        self, db: Session, num_potential_matches: int, include_linked_person: bool
    ):
        """Property: Duplicate check results are correctly filtered."""
        db.rollback()
        fixtures = self._get_fixtures(db)
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available")

        user = self._create_user(db)
        person = self._create_person(db, fixtures, user, user, is_primary=True, is_active=False)
        self._create_address(db, fixtures, person.id)
        self._create_religion(db, fixtures, person.id)

        # Create potential matches (persons without users)
        potential_matches = []
        for _ in range(num_potential_matches):
            match_person = self._create_person(db, fixtures, None, user, is_active=True)
            self._create_address(db, fixtures, match_person.id)
            self._create_religion(db, fixtures, match_person.id)
            potential_matches.append(match_person)

        # Optionally create a person with a linked user (should be filtered out)
        linked_person = None
        linked_user = None
        if include_linked_person:
            linked_user = self._create_user(db)
            linked_person = self._create_person(db, fixtures, linked_user, user, is_active=True)
            self._create_address(db, fixtures, linked_person.id)
            self._create_religion(db, fixtures, linked_person.id)

        try:
            service = ProfileService(db)
            results = service.get_duplicate_matches(user.id)

            # Property: All results should NOT be the current user's person
            for result in results:
                assert result.person_id != person.id, "Results should not include current user's person"

            # Property: All results should NOT have a linked user
            for result in results:
                result_person = db.get(Person, result.person_id)
                assert result_person.user_id is None, "Results should not include persons with linked users"

            # Property: All results should be active
            for result in results:
                result_person = db.get(Person, result.person_id)
                assert result_person.is_active is True, "Results should only include active persons"

            # Property: If we created a linked person, it should NOT be in results
            if linked_person:
                result_ids = [r.person_id for r in results]
                assert linked_person.id not in result_ids, "Linked person should be filtered out"

        finally:
            if linked_person:
                self._cleanup_person(db, linked_person.id)
            if linked_user:
                self._cleanup_user(db, linked_user.id)
            for match in potential_matches:
                self._cleanup_person(db, match.id)
            self._cleanup_person(db, person.id)
            self._cleanup_user(db, user.id)


class TestCompleteWithoutAttachmentActivatesPerson(BaseProfilePropertyTest):
    """Property 4: Complete Without Attachment Activates Person.
    
    *For any* successful call to complete-without-attachment endpoint:
    - The current user's Person `is_active` SHALL be set to `True`
    - The response SHALL include updated profile completion status with `has_duplicate_check` = `True`
    - The response SHALL include `is_complete` = `True` (assuming other fields are complete)
    
    **Validates: Requirements 3.8, 6.1, 8.2, 8.3**
    """

    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target],
        database=None,
        deadline=None,
    )
    @given(
        initial_is_active=st.booleans(),
        marital_status=st.sampled_from([MaritalStatus.SINGLE, MaritalStatus.MARRIED]),
    )
    def test_complete_without_attachment_activates_person(
        self, db: Session, initial_is_active: bool, marital_status: MaritalStatus
    ):
        """Property: Complete without attachment activates person and updates status."""
        db.rollback()
        fixtures = self._get_fixtures(db)
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available")

        user = self._create_user(db)
        person = self._create_person(
            db, fixtures, user, user, is_primary=True,
            is_active=initial_is_active, marital_status=marital_status
        )
        self._create_address(db, fixtures, person.id)
        self._create_religion(db, fixtures, person.id)

        try:
            service = ProfileService(db)
            result = service.complete_without_attachment(user.id)

            # Refresh person from database
            db.refresh(person)

            # Property 1: Person should be active after completion
            assert person.is_active is True, "Person should be activated"

            # Property 2: has_duplicate_check should be True
            assert result.has_duplicate_check is True, "has_duplicate_check should be True after completion"

            # Property 3: is_complete should be True (all fields are complete)
            assert result.is_complete is True, "is_complete should be True when all fields are complete"

        finally:
            self._cleanup_person(db, person.id)
            self._cleanup_user(db, user.id)


class TestCompleteWithoutAttachmentBlockedByPendingRequest(BaseProfilePropertyTest):
    """Property 5: Complete Without Attachment Blocked by Pending Request.
    
    *For any* user with a PENDING attachment request, calling complete-without-attachment
    SHALL return a 400 error and NOT modify the Person's `is_active` status.
    
    **Validates: Requirements 8.4**
    """

    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target],
        database=None,
        deadline=None,
    )
    @given(
        initial_is_active=st.booleans(),
    )
    def test_complete_without_attachment_blocked_by_pending_request(
        self, db: Session, initial_is_active: bool
    ):
        """Property: Complete without attachment is blocked when pending request exists."""
        db.rollback()
        fixtures = self._get_fixtures(db)
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available")

        user = self._create_user(db)
        approver = self._create_user(db)
        person = self._create_person(
            db, fixtures, user, user, is_primary=True,
            is_active=initial_is_active, marital_status=MaritalStatus.SINGLE
        )
        self._create_address(db, fixtures, person.id)
        self._create_religion(db, fixtures, person.id)

        # Create target person and pending request
        target_person = self._create_person(db, fixtures, None, approver, is_active=True)
        request = self._create_attachment_request(
            db, user.id, person.id, target_person.id, approver.id,
            AttachmentRequestStatus.PENDING
        )

        try:
            service = ProfileService(db)

            # Property: Should raise 400 error
            with pytest.raises(HTTPException) as exc_info:
                service.complete_without_attachment(user.id)

            assert exc_info.value.status_code == 400, "Should return 400 error"
            assert "pending" in exc_info.value.detail.lower(), "Error should mention pending request"

            # Property: Person's is_active should NOT be modified
            db.refresh(person)
            assert person.is_active == initial_is_active, (
                f"Person's is_active should remain {initial_is_active}"
            )

        finally:
            self._cleanup_request(db, request.id)
            self._cleanup_person(db, target_person.id)
            self._cleanup_person(db, person.id)
            self._cleanup_user(db, user.id)
            self._cleanup_user(db, approver.id)

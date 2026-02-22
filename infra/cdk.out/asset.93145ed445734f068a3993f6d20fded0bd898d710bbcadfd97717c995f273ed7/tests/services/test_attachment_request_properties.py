"""Property-based tests for Attachment Request Service.

**Feature: person-attachment-approval**
**Validates: Requirements 2.2, 2.3, 3.2-3.7, 6.4, 7.4, 8.4, 8.5**
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
from app.models import User
from app.schemas.attachment_request import AttachmentRequestCreate
from app.services.attachment_request_service import AttachmentRequestService


class BasePropertyTest:
    """Base class for property tests."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, db: Session):
        db.rollback()
        yield
        db.rollback()

    def _get_fixtures(self, db: Session) -> dict:
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
        user = User(
            email=f"test_{uuid.uuid4()}@example.com",
            hashed_password="test_password",
            is_active=True, is_superuser=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def _create_person(self, db, fixtures, user, created_by, is_primary=False, is_active=True):
        person = Person(
            user_id=user.id if user else None,
            created_by_user_id=created_by.id,
            is_primary=is_primary,
            first_name=f"Test{uuid.uuid4().hex[:4]}",
            last_name="Person",
            gender_id=fixtures["gender"].id,
            date_of_birth=date(1990, 1, 1),
            is_active=is_active,
        )
        db.add(person)
        db.commit()
        db.refresh(person)
        return person

    def _create_person_with_metadata(self, db, fixtures, user, created_by, is_primary=False, is_active=True):
        person = self._create_person(db, fixtures, user, created_by, is_primary, is_active)
        address = PersonAddress(
            person_id=person.id, country_id=fixtures["country"].id,
            state_id=fixtures["state"].id, district_id=fixtures["district"].id,
            sub_district_id=fixtures["sub_district"].id,
            start_date=date(2020, 1, 1), is_current=True,
        )
        db.add(address)
        religion = PersonReligion(
            person_id=person.id, religion_id=fixtures["religion"].id,
            religion_category_id=fixtures["religion_category"].id,
        )
        db.add(religion)
        db.commit()
        return person

    def _cleanup_person(self, db, person_id):
        db.execute(delete(PersonAddress).where(PersonAddress.person_id == person_id))
        db.execute(delete(PersonReligion).where(PersonReligion.person_id == person_id))
        db.execute(delete(Person).where(Person.id == person_id))
        db.commit()

    def _cleanup_user(self, db, user_id):
        db.execute(delete(User).where(User.id == user_id))
        db.commit()

    def _cleanup_request(self, db, request_id):
        db.execute(delete(PersonAttachmentRequest).where(PersonAttachmentRequest.id == request_id))
        db.commit()



class TestOnePendingRequestPerUser(BasePropertyTest):
    """Property 4: One Pending Request Per User. Validates: Requirements 2.2, 3.7"""

    @settings(
        max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target], database=None, deadline=None,
    )
    @given(num_attempts=st.integers(min_value=2, max_value=4))
    def test_only_one_pending_request_allowed(self, db: Session, num_attempts: int):
        """Property: User cannot have more than one pending request."""
        db.rollback()
        fixtures = self._get_fixtures(db)
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available")
        
        requester = self._create_user(db)
        approver = self._create_user(db)
        requester_person = self._create_person_with_metadata(db, fixtures, requester, requester, True)
        targets = [self._create_person(db, fixtures, None, approver) for _ in range(num_attempts)]
        created = []
        
        try:
            service = AttachmentRequestService(db)
            req1 = service.create_request(requester.id, AttachmentRequestCreate(target_person_id=targets[0].id))
            created.append(req1)
            
            for i in range(1, num_attempts):
                with pytest.raises(HTTPException) as exc:
                    service.create_request(requester.id, AttachmentRequestCreate(target_person_id=targets[i].id))
                assert exc.value.status_code == 400
                assert "already have a pending" in exc.value.detail.lower()
        finally:
            for r in created:
                self._cleanup_request(db, r.id)
            for t in targets:
                self._cleanup_person(db, t.id)
            self._cleanup_person(db, requester_person.id)
            self._cleanup_user(db, requester.id)
            self._cleanup_user(db, approver.id)


class TestTargetPersonMustNotHaveUser(BasePropertyTest):
    """Property 5: Target Person Must Not Have User. Validates: Requirements 2.3, 3.8"""

    @settings(
        max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target], database=None, deadline=None,
    )
    @given(target_has_user=st.booleans())
    def test_target_person_user_validation(self, db: Session, target_has_user: bool):
        """Property: Request fails if target person already has a user."""
        db.rollback()
        fixtures = self._get_fixtures(db)
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available")
        
        requester = self._create_user(db)
        approver = self._create_user(db)
        linked_user = self._create_user(db) if target_has_user else None
        requester_person = self._create_person_with_metadata(db, fixtures, requester, requester, True)
        target = self._create_person(db, fixtures, linked_user, approver)
        created = []
        
        try:
            service = AttachmentRequestService(db)
            if target_has_user:
                with pytest.raises(HTTPException) as exc:
                    service.create_request(requester.id, AttachmentRequestCreate(target_person_id=target.id))
                assert exc.value.status_code == 400
                assert "already linked" in exc.value.detail.lower()
            else:
                req = service.create_request(requester.id, AttachmentRequestCreate(target_person_id=target.id))
                created.append(req)
                assert req.status == AttachmentRequestStatus.PENDING
        finally:
            for r in created:
                self._cleanup_request(db, r.id)
            self._cleanup_person(db, target.id)
            self._cleanup_person(db, requester_person.id)
            if linked_user:
                self._cleanup_user(db, linked_user.id)
            self._cleanup_user(db, requester.id)
            self._cleanup_user(db, approver.id)


class TestCreateRequestAutoPopulation(BasePropertyTest):
    """Property 7: Create Request Auto-Population. Validates: Requirements 3.2-3.6"""

    @settings(
        max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target], database=None, deadline=None,
    )
    @given(dummy=st.integers(min_value=1, max_value=1))
    def test_create_request_auto_populates_fields(self, db: Session, dummy: int):
        """Property: Create request auto-populates all required fields."""
        db.rollback()
        fixtures = self._get_fixtures(db)
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available")
        
        requester = self._create_user(db)
        approver = self._create_user(db)
        requester_person = self._create_person_with_metadata(db, fixtures, requester, requester, True)
        target = self._create_person(db, fixtures, None, approver)
        
        try:
            service = AttachmentRequestService(db)
            req = service.create_request(requester.id, AttachmentRequestCreate(target_person_id=target.id))
            
            assert req.requester_user_id == requester.id
            assert req.requester_person_id == requester_person.id
            assert req.approver_user_id == target.created_by_user_id
            assert req.target_person_id == target.id
            assert req.status == AttachmentRequestStatus.PENDING
            
            self._cleanup_request(db, req.id)
        finally:
            self._cleanup_person(db, target.id)
            self._cleanup_person(db, requester_person.id)
            self._cleanup_user(db, requester.id)
            self._cleanup_user(db, approver.id)


class TestApproveSideEffects(BasePropertyTest):
    """Property 12: Approve Side Effects. Validates: Requirements 6.4"""

    @settings(
        max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target], database=None, deadline=None,
    )
    @given(dummy=st.integers(min_value=1, max_value=1))
    def test_approve_side_effects(self, db: Session, dummy: int):
        """Property: Approve has correct side effects."""
        db.rollback()
        fixtures = self._get_fixtures(db)
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available")
        
        requester = self._create_user(db)
        approver = self._create_user(db)
        requester_person = self._create_person_with_metadata(db, fixtures, requester, requester, True, False)
        requester_person_id = requester_person.id
        target = self._create_person(db, fixtures, None, approver)
        target_id = target.id
        
        try:
            service = AttachmentRequestService(db)
            req = service.create_request(requester.id, AttachmentRequestCreate(target_person_id=target_id))
            req_id = req.id
            
            service.approve_request(req_id, approver.id)
            
            updated_target = db.get(Person, target_id)
            assert updated_target.user_id == requester.id
            assert updated_target.is_primary is True
            assert db.get(Person, requester_person_id) is None
            assert db.get(PersonAttachmentRequest, req_id).status == AttachmentRequestStatus.APPROVED
            
            self._cleanup_request(db, req_id)
        finally:
            self._cleanup_person(db, target_id)
            self._cleanup_user(db, requester.id)
            self._cleanup_user(db, approver.id)


class TestDenySideEffects(BasePropertyTest):
    """Property 13: Deny Side Effects. Validates: Requirements 7.4"""

    @settings(
        max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target], database=None, deadline=None,
    )
    @given(dummy=st.integers(min_value=1, max_value=1))
    def test_deny_side_effects(self, db: Session, dummy: int):
        """Property: Deny has correct side effects."""
        db.rollback()
        fixtures = self._get_fixtures(db)
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available")
        
        requester = self._create_user(db)
        approver = self._create_user(db)
        requester_id = requester.id
        requester_person = self._create_person_with_metadata(db, fixtures, requester, requester, True, False)
        requester_person_id = requester_person.id
        target = self._create_person(db, fixtures, None, approver)
        target_id = target.id
        
        try:
            service = AttachmentRequestService(db)
            req = service.create_request(requester_id, AttachmentRequestCreate(target_person_id=target_id))
            req_id = req.id
            
            service.deny_request(req_id, approver.id)
            
            assert db.get(Person, requester_person_id) is None
            assert db.get(User, requester_id) is None
            assert db.get(PersonAttachmentRequest, req_id).status == AttachmentRequestStatus.DENIED
            assert db.get(Person, target_id) is not None
            
            self._cleanup_request(db, req_id)
        finally:
            self._cleanup_person(db, target_id)
            self._cleanup_user(db, approver.id)


class TestCancelPreservesRecords(BasePropertyTest):
    """Property 14: Cancel Preserves Records. Validates: Requirements 8.4, 8.5"""

    @settings(
        max_examples=10, suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target], database=None, deadline=None,
    )
    @given(dummy=st.integers(min_value=1, max_value=1))
    def test_cancel_preserves_records(self, db: Session, dummy: int):
        """Property: Cancel preserves all records."""
        db.rollback()
        fixtures = self._get_fixtures(db)
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available")
        
        requester = self._create_user(db)
        approver = self._create_user(db)
        requester_person = self._create_person_with_metadata(db, fixtures, requester, requester, True)
        requester_person_id = requester_person.id
        target = self._create_person(db, fixtures, None, approver)
        target_id = target.id
        
        try:
            service = AttachmentRequestService(db)
            req = service.create_request(requester.id, AttachmentRequestCreate(target_person_id=target_id))
            req_id = req.id
            
            service.cancel_request(req_id, requester.id)
            
            assert db.get(PersonAttachmentRequest, req_id).status == AttachmentRequestStatus.CANCELLED
            assert db.get(Person, requester_person_id) is not None
            assert db.get(User, requester.id) is not None
            assert db.get(Person, target_id) is not None
            
            self._cleanup_request(db, req_id)
        finally:
            self._cleanup_person(db, target_id)
            self._cleanup_person(db, requester_person_id)
            self._cleanup_user(db, requester.id)
            self._cleanup_user(db, approver.id)

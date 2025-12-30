"""Property-based tests for PersonRepository.

**Feature: contribution-stats, Property 1: Contribution Query Correctness**
**Validates: Requirements 1.1**
"""

import uuid
from datetime import date

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlmodel import Session, select

from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.models import User
from app.repositories.person.person_repository import PersonRepository


class TestContributionQueryCorrectness:
    """Tests for Property 1: Contribution Query Correctness.
    
    **Feature: contribution-stats, Property 1: Contribution Query Correctness**
    **Validates: Requirements 1.1**
    
    Property: For any user and any set of person records in the database,
    querying contributions for that user should return exactly the persons
    where created_by_user_id matches the user's ID, and no others.
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        # Generate number of persons created by target user (0-5)
        target_user_person_count=st.integers(min_value=0, max_value=5),
        # Generate number of persons created by other users (0-5)
        other_users_person_count=st.integers(min_value=0, max_value=5),
    )
    def test_contribution_query_correctness_property(
        self,
        db: Session,
        target_user_person_count: int,
        other_users_person_count: int,
    ) -> None:
        """Property 1: Query returns exactly persons created by the user."""
        repo = PersonRepository(db)
        
        # Get or create gender for persons
        gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
        if not gender:
            gender = Gender(
                id=uuid.uuid4(),
                name="Male",
                code="MALE",
                description="Male gender",
                is_active=True
            )
            db.add(gender)
            db.commit()
            db.refresh(gender)
        
        # Create target user
        target_user = User(
            email=f"target_{uuid.uuid4()}@example.com",
            hashed_password="test_password",
            is_active=True,
            is_superuser=False,
        )
        db.add(target_user)
        db.commit()
        db.refresh(target_user)
        
        # Create other users
        other_users = []
        for i in range(max(1, other_users_person_count)):  # At least 1 other user
            user = User(
                email=f"other_{uuid.uuid4()}@example.com",
                hashed_password="test_password",
                is_active=True,
                is_superuser=False,
            )
            db.add(user)
            other_users.append(user)
        
        if other_users:
            db.commit()
            for user in other_users:
                db.refresh(user)
        
        # Create persons by target user
        target_persons = []
        for i in range(target_user_person_count):
            person = Person(
                user_id=None,
                created_by_user_id=target_user.id,
                is_primary=False,
                first_name=f"Target{i}",
                last_name="Person",
                gender_id=gender.id,
                date_of_birth=date(1990, 1, 1),
            )
            db.add(person)
            target_persons.append(person)
        
        # Create persons by other users
        other_persons = []
        for i in range(other_users_person_count):
            if other_users:
                creator = other_users[i % len(other_users)]
                person = Person(
                    user_id=None,
                    created_by_user_id=creator.id,
                    is_primary=False,
                    first_name=f"Other{i}",
                    last_name="Person",
                    gender_id=gender.id,
                    date_of_birth=date(1990, 1, 1),
                )
                db.add(person)
                other_persons.append(person)
        
        try:
            db.commit()
            
            # Query contributions for target user
            result = repo.get_by_creator(target_user.id)
            
            # Verify the property: all returned persons have correct creator
            for person in result:
                assert person.created_by_user_id == target_user.id, (
                    f"Returned person {person.id} has wrong creator: "
                    f"expected {target_user.id}, got {person.created_by_user_id}"
                )
            
            # Verify the property: correct count
            assert len(result) == target_user_person_count, (
                f"Expected {target_user_person_count} persons, got {len(result)}"
            )
            
            # Verify the property: all target persons are returned
            result_ids = {person.id for person in result}
            target_ids = {person.id for person in target_persons}
            assert result_ids == target_ids, (
                f"Returned person IDs don't match expected. "
                f"Expected: {target_ids}, Got: {result_ids}"
            )
            
            # Verify the property: no other persons are returned
            other_ids = {person.id for person in other_persons}
            assert result_ids.isdisjoint(other_ids), (
                f"Result contains persons from other users: "
                f"{result_ids & other_ids}"
            )
        
        finally:
            # Cleanup
            for person in target_persons + other_persons:
                db.delete(person)
            db.delete(target_user)
            for user in other_users:
                db.delete(user)
            db.commit()

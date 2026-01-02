"""Property-based tests for ProfileViewTrackingRepository.

**Feature: contribution-stats, Property 12: View Count Aggregation**
**Validates: Requirements 4.2, 4.3**
"""

import uuid
from datetime import date

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlmodel import Session, select

from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.db_models.profile_view_tracking import ProfileViewTracking
from app.db_models.user import User
from app.repositories.profile_view_tracking_repository import (
    ProfileViewTrackingRepository,
)


class TestViewCountAggregation:
    """Tests for Property 12: View Count Aggregation.
    
    **Feature: contribution-stats, Property 12: View Count Aggregation**
    **Validates: Requirements 4.2, 4.3**
    
    Property: For any person with multiple view records (both aggregated and non-aggregated),
    the total view count should equal the sum of all view_count values for that person.
    """

    @settings(
        max_examples=10,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    @given(
        # Generate a list of view counts (1-5 records, each with count 1-100)
        view_counts=st.lists(
            st.integers(min_value=1, max_value=100),
            min_size=1,
            max_size=5,
        ),
        # Generate a list of booleans for is_aggregated flag
        is_aggregated_flags=st.lists(
            st.booleans(),
            min_size=1,
            max_size=5,
        ),
    )
    def test_view_count_aggregation_property(
        self,
        db: Session,
        view_counts: list[int],
        is_aggregated_flags: list[bool],
    ) -> None:
        """Property 12: Total view count equals sum of all view_count values."""
        # Rollback any pending transaction
        db.rollback()
        
        # Ensure both lists have the same length
        min_len = min(len(view_counts), len(is_aggregated_flags))
        view_counts = view_counts[:min_len]
        is_aggregated_flags = is_aggregated_flags[:min_len]
        
        repo = ProfileViewTrackingRepository(db)
        
        # Get a gender from the database
        gender = db.exec(select(Gender)).first()
        if not gender:
            # Skip test if no gender exists
            return
        
        # Create a test user
        test_user = User(
            email=f"test_view_agg_{uuid.uuid4()}@example.com",
            hashed_password="test_password",
            is_active=True,
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create the viewed person
        viewed_person = Person(
            first_name="Viewed",
            last_name="Person",
            date_of_birth=date(1990, 1, 1),
            gender_id=gender.id,
            created_by_user_id=test_user.id,
        )
        db.add(viewed_person)
        db.commit()
        db.refresh(viewed_person)
        
        # Create viewer persons and view records
        view_records = []
        viewer_persons = []
        for i, (count, is_agg) in enumerate(zip(view_counts, is_aggregated_flags)):
            viewer = Person(
                first_name=f"Viewer{i}",
                last_name="Person",
                date_of_birth=date(1990, 1, 1),
                gender_id=gender.id,
                created_by_user_id=test_user.id,
            )
            db.add(viewer)
            db.commit()
            db.refresh(viewer)
            viewer_persons.append(viewer)
            
            record = ProfileViewTracking(
                viewer_person_id=viewer.id,
                viewed_person_id=viewed_person.id,
                view_count=count,
                is_aggregated=is_agg,
            )
            view_records.append(record)
            db.add(record)
        
        db.commit()
        
        try:
            # Calculate expected total (sum of all view_count values)
            expected_total = sum(view_counts)
            
            # Get actual total from repository
            actual_total = repo.get_total_views_for_person(viewed_person.id)
            
            # Verify the property holds
            assert actual_total == expected_total, (
                f"View count aggregation failed: expected {expected_total}, "
                f"got {actual_total}. View counts: {view_counts}, "
                f"is_aggregated: {is_aggregated_flags}"
            )
        
        finally:
            # Cleanup
            for record in view_records:
                db.delete(record)
            db.commit()
            for viewer in viewer_persons:
                db.delete(viewer)
            db.delete(viewed_person)
            db.delete(test_user)
            db.commit()

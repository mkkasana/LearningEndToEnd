"""Property-based tests for ProfileViewTrackingRepository.

**Feature: contribution-stats, Property 12: View Count Aggregation**
**Validates: Requirements 4.2, 4.3**
"""

import uuid

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlmodel import Session

from app.db_models.profile_view_tracking import ProfileViewTracking
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
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        # Generate a list of view counts (1-10 records, each with count 1-100)
        view_counts=st.lists(
            st.integers(min_value=1, max_value=100),
            min_size=1,
            max_size=10,
        ),
        # Generate a list of booleans for is_aggregated flag
        is_aggregated_flags=st.lists(
            st.booleans(),
            min_size=1,
            max_size=10,
        ),
    )
    def test_view_count_aggregation_property(
        self,
        db: Session,
        view_counts: list[int],
        is_aggregated_flags: list[bool],
    ) -> None:
        """Property 12: Total view count equals sum of all view_count values."""
        # Ensure both lists have the same length
        min_len = min(len(view_counts), len(is_aggregated_flags))
        view_counts = view_counts[:min_len]
        is_aggregated_flags = is_aggregated_flags[:min_len]
        
        repo = ProfileViewTrackingRepository(db)
        
        # Generate UUIDs for viewer and viewed persons
        # Note: These won't have actual Person records, but that's okay for this test
        # as we're testing the aggregation logic, not the foreign key constraints
        viewed_person_id = uuid.uuid4()
        
        # Create multiple view records with different viewers
        view_records = []
        for i, (count, is_agg) in enumerate(zip(view_counts, is_aggregated_flags)):
            viewer_id = uuid.uuid4()
            record = ProfileViewTracking(
                viewer_person_id=viewer_id,
                viewed_person_id=viewed_person_id,
                view_count=count,
                is_aggregated=is_agg,
            )
            view_records.append(record)
            db.add(record)
        
        try:
            db.commit()
            
            # Calculate expected total (sum of all view_count values)
            expected_total = sum(view_counts)
            
            # Get actual total from repository
            actual_total = repo.get_total_views_for_person(viewed_person_id)
            
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

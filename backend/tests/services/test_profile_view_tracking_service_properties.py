"""Property-based tests for ProfileViewTrackingService.

**Feature: contribution-stats**
"""

import uuid
from unittest.mock import patch

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlmodel import Session

from app.db_models.profile_view_tracking import ProfileViewTracking
from app.services.profile_view_tracking_service import ProfileViewTrackingService


# Strategy for generating UUIDs
uuid_strategy = st.uuids()


class TestViewRecordingProperties:
    """Property-based tests for view recording functionality.
    
    **Feature: contribution-stats, Property 9: First View Creates New Record**
    **Validates: Requirements 3.6**
    
    **Feature: contribution-stats, Property 10: Subsequent Views Increment Count**
    **Validates: Requirements 3.7**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        viewer_id=uuid_strategy,
        viewed_id=uuid_strategy,
    )
    def test_first_view_creates_record_with_count_one(
        self,
        db: Session,
        viewer_id: uuid.UUID,
        viewed_id: uuid.UUID,
    ) -> None:
        """Property 9: For any viewer-viewed pair with no existing record, 
        recording a view creates a new record with view_count=1.
        """
        # Skip if viewer and viewed are the same (self-view)
        if viewer_id == viewed_id:
            return

        service = ProfileViewTrackingService(db)

        # Mock repository to simulate no existing record
        with patch.object(
            service.repo, "get_non_aggregated_view", return_value=None
        ) as mock_get, patch.object(service.repo, "create") as mock_create:
            # Record view
            service.record_view(viewer_id, viewed_id)

            # Verify get was called
            mock_get.assert_called_once_with(viewer_id, viewed_id)

            # Verify create was called with correct data
            mock_create.assert_called_once()
            created_record = mock_create.call_args[0][0]
            assert created_record.viewer_person_id == viewer_id
            assert created_record.viewed_person_id == viewed_id
            assert created_record.view_count == 1
            assert created_record.is_aggregated is False

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        viewer_id=uuid_strategy,
        viewed_id=uuid_strategy,
        initial_count=st.integers(min_value=1, max_value=100),
    )
    def test_subsequent_view_increments_count(
        self,
        db: Session,
        viewer_id: uuid.UUID,
        viewed_id: uuid.UUID,
        initial_count: int,
    ) -> None:
        """Property 10: For any viewer-viewed pair with an existing record, 
        recording another view increments view_count by 1.
        """
        # Skip if viewer and viewed are the same (self-view)
        if viewer_id == viewed_id:
            return

        service = ProfileViewTrackingService(db)

        # Create mock existing record with random initial count
        existing_record = ProfileViewTracking(
            viewer_person_id=viewer_id,
            viewed_person_id=viewed_id,
            view_count=initial_count,
            is_aggregated=False,
        )

        # Mock repository methods
        with patch.object(
            service.repo, "get_non_aggregated_view", return_value=existing_record
        ) as mock_get, patch.object(service.repo, "update") as mock_update:
            # Record view
            service.record_view(viewer_id, viewed_id)

            # Verify get was called
            mock_get.assert_called_once_with(viewer_id, viewed_id)

            # Verify update was called and count was incremented
            mock_update.assert_called_once()
            updated_record = mock_update.call_args[0][0]
            assert updated_record.view_count == initial_count + 1


class TestErrorResilience:
    """Property-based tests for error handling.
    
    **Feature: contribution-stats, Property 11: Error Resilience**
    **Validates: Requirements 3.8**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        viewer_id=uuid_strategy,
        viewed_id=uuid_strategy,
        error_message=st.text(min_size=1, max_size=100),
    )
    def test_errors_are_caught_and_logged(
        self,
        db: Session,
        viewer_id: uuid.UUID,
        viewed_id: uuid.UUID,
        error_message: str,
    ) -> None:
        """Property 11: For any error during view recording, 
        the system logs the error and continues without raising.
        """
        service = ProfileViewTrackingService(db)

        # Mock repository to raise an exception
        with patch.object(
            service.repo,
            "get_non_aggregated_view",
            side_effect=Exception(error_message),
        ):
            # This should not raise an exception
            try:
                service.record_view(viewer_id, viewed_id)
                # If we get here, the test passed
            except Exception:
                # If an exception is raised, the test fails
                assert False, "record_view should not raise exceptions"

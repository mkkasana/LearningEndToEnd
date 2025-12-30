"""Unit tests for ProfileViewTrackingService."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from app.db_models.profile_view_tracking import ProfileViewTracking
from app.services.profile_view_tracking_service import ProfileViewTrackingService


class TestRecordView:
    """Tests for record_view method."""

    def test_record_view_with_self_view_should_not_record(self, db: Session) -> None:
        """Test that self-views are not recorded.
        
        Requirements: 3.4
        """
        service = ProfileViewTrackingService(db)
        person_id = uuid.uuid4()

        # Mock the repository to track if it was called
        with patch.object(service.repo, "get_non_aggregated_view") as mock_get:
            # Record a self-view
            service.record_view(person_id, person_id)

            # Verify repository was not called (early return)
            mock_get.assert_not_called()

    def test_record_view_first_view_creates_new_record(self, db: Session) -> None:
        """Test that first view creates a new record with view_count=1.
        
        Requirements: 3.6
        """
        service = ProfileViewTrackingService(db)
        viewer_id = uuid.uuid4()
        viewed_id = uuid.uuid4()

        # Mock repository methods
        with patch.object(
            service.repo, "get_non_aggregated_view", return_value=None
        ) as mock_get, patch.object(service.repo, "create") as mock_create:
            # Record first view
            service.record_view(viewer_id, viewed_id)

            # Verify get was called
            mock_get.assert_called_once_with(viewer_id, viewed_id)

            # Verify create was called
            mock_create.assert_called_once()
            created_record = mock_create.call_args[0][0]
            assert created_record.viewer_person_id == viewer_id
            assert created_record.viewed_person_id == viewed_id
            assert created_record.view_count == 1
            assert created_record.is_aggregated is False

    def test_record_view_subsequent_view_increments_count(self, db: Session) -> None:
        """Test that subsequent views increment the view_count.
        
        Requirements: 3.7
        """
        service = ProfileViewTrackingService(db)
        viewer_id = uuid.uuid4()
        viewed_id = uuid.uuid4()

        # Create a mock existing record
        existing_record = ProfileViewTracking(
            viewer_person_id=viewer_id,
            viewed_person_id=viewed_id,
            view_count=1,
            is_aggregated=False,
        )

        # Mock repository methods
        with patch.object(
            service.repo, "get_non_aggregated_view", return_value=existing_record
        ) as mock_get, patch.object(service.repo, "update") as mock_update:
            # Record second view
            service.record_view(viewer_id, viewed_id)

            # Verify get was called
            mock_get.assert_called_once_with(viewer_id, viewed_id)

            # Verify update was called
            mock_update.assert_called_once()
            updated_record = mock_update.call_args[0][0]
            assert updated_record.view_count == 2
            assert updated_record.last_viewed_at is not None
            assert updated_record.updated_at is not None

    def test_record_view_with_database_error_should_not_raise(
        self, db: Session
    ) -> None:
        """Test that database errors are caught and logged without raising.
        
        Requirements: 3.8
        """
        service = ProfileViewTrackingService(db)
        viewer_id = uuid.uuid4()
        viewed_id = uuid.uuid4()

        # Mock the repository to raise an exception
        with patch.object(
            service.repo,
            "get_non_aggregated_view",
            side_effect=Exception("Database error"),
        ):
            # This should not raise an exception
            try:
                service.record_view(viewer_id, viewed_id)
            except Exception as e:
                pytest.fail(f"record_view should not raise exception, but raised: {e}")


class TestGetTotalViews:
    """Tests for get_total_views method."""

    def test_get_total_views_with_no_views(self, db: Session) -> None:
        """Test that get_total_views returns 0 for person with no views.
        
        Requirements: 4.4
        """
        service = ProfileViewTrackingService(db)
        person_id = uuid.uuid4()

        # Mock repository to return 0
        with patch.object(
            service.repo, "get_total_views_for_person", return_value=0
        ) as mock_get:
            # Get total views for person with no views
            total_views = service.get_total_views(person_id)

            # Verify repository was called
            mock_get.assert_called_once_with(person_id)
            assert total_views == 0


class TestGetTotalViewsBulk:
    """Tests for get_total_views_bulk method."""

    def test_get_total_views_bulk_with_empty_list(self, db: Session) -> None:
        """Test that get_total_views_bulk returns empty dict for empty list.
        
        Requirements: 4.6
        """
        service = ProfileViewTrackingService(db)

        # Get total views for empty list
        result = service.get_total_views_bulk([])

        assert result == {}

    def test_get_total_views_bulk_with_multiple_persons(self, db: Session) -> None:
        """Test that get_total_views_bulk returns correct counts for multiple persons."""
        service = ProfileViewTrackingService(db)
        viewed_id_1 = uuid.uuid4()
        viewed_id_2 = uuid.uuid4()

        # Mock repository to return view counts
        mock_result = {viewed_id_1: 2, viewed_id_2: 1}
        with patch.object(
            service.repo, "get_total_views_for_persons", return_value=mock_result
        ) as mock_get:
            # Get bulk view counts
            result = service.get_total_views_bulk([viewed_id_1, viewed_id_2])

            # Verify repository was called
            mock_get.assert_called_once_with([viewed_id_1, viewed_id_2])
            assert result == mock_result
            assert result[viewed_id_1] == 2
            assert result[viewed_id_2] == 1

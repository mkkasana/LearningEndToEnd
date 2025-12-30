"""Unit tests for ProfileViewTrackingRepository.

Note: These tests focus on the repository methods' logic.
Full integration tests with actual Person records are in the integration test suite.
"""

import uuid

import pytest
from sqlmodel import Session

from app.repositories.profile_view_tracking_repository import (
    ProfileViewTrackingRepository,
)


class TestGetNonAggregatedView:
    """Tests for get_non_aggregated_view method."""

    def test_get_non_aggregated_view_non_existing_pair(self, db: Session) -> None:
        """Test get_non_aggregated_view with non-existing viewer-viewed pair."""
        repo = ProfileViewTrackingRepository(db)
        person1_id = uuid.uuid4()
        person2_id = uuid.uuid4()
        
        # Test retrieval of non-existent pair
        result = repo.get_non_aggregated_view(person1_id, person2_id)
        
        assert result is None


class TestGetTotalViewsForPerson:
    """Tests for get_total_views_for_person method."""

    def test_get_total_views_with_zero_views(self, db: Session) -> None:
        """Test get_total_views_for_person with person who has no views."""
        repo = ProfileViewTrackingRepository(db)
        person_id = uuid.uuid4()
        
        # Test with person who has no view records
        result = repo.get_total_views_for_person(person_id)
        
        assert result == 0


class TestGetTotalViewsForPersons:
    """Tests for get_total_views_for_persons bulk method."""

    def test_get_total_views_for_persons_empty_list(self, db: Session) -> None:
        """Test get_total_views_for_persons with empty list."""
        repo = ProfileViewTrackingRepository(db)
        
        # Test with empty list
        result = repo.get_total_views_for_persons([])
        
        assert result == {}

    def test_get_total_views_for_persons_with_no_views(self, db: Session) -> None:
        """Test get_total_views_for_persons with persons who have no views."""
        repo = ProfileViewTrackingRepository(db)
        person_id = uuid.uuid4()
        
        # Test with person who has no view records
        result = repo.get_total_views_for_persons([person_id])
        
        # Person with no views should not appear in result
        assert len(result) == 0

"""Unit tests for PersonMatchingService."""

import pytest
from sqlmodel import Session

from app.services.person.person_matching_service import PersonMatchingService


class TestCalculateNameMatchScore:
    """Tests for the calculate_name_match_score method."""

    @pytest.fixture
    def service(self, db: Session) -> PersonMatchingService:
        """Create a PersonMatchingService instance for testing."""
        return PersonMatchingService(db)

    def test_exact_match_returns_100(self, service: PersonMatchingService) -> None:
        """Test that exact name match returns score of 100."""
        score = service.calculate_name_match_score("John", "Smith", "John", "Smith")
        assert score == 100.0

    def test_fuzzy_match_high_score(self, service: PersonMatchingService) -> None:
        """Test that similar names (Jon vs John) return high match score."""
        score = service.calculate_name_match_score("Jon", "Smith", "John", "Smith")
        assert 94.0 <= score <= 95.0, f"Expected score ~94.29, got {score}"

    def test_case_insensitive_matching(self, service: PersonMatchingService) -> None:
        """Test that matching is case insensitive."""
        score = service.calculate_name_match_score("JOHN", "SMITH", "john", "smith")
        assert score == 100.0

    def test_whitespace_normalization(self, service: PersonMatchingService) -> None:
        """Test that leading/trailing whitespace is handled correctly."""
        score = service.calculate_name_match_score(
            "  John  ", "  Smith  ", "John", "Smith"
        )
        assert score == 100.0

    def test_weighted_average_last_name_priority(
        self, service: PersonMatchingService
    ) -> None:
        """Test that last name has higher weight (60%) than first name (40%)."""
        # Different first names, same last name
        score1 = service.calculate_name_match_score("John", "Smith", "Michael", "Smith")

        # Same first names, different last name
        score2 = service.calculate_name_match_score("John", "Smith", "John", "Johnson")

        # Score1 should be higher because last name (60% weight) matches
        assert (
            score1 > score2
        ), f"Expected score1 ({score1}) > score2 ({score2}) due to last name having 60% weight"

    def test_completely_different_names_low_score(
        self, service: PersonMatchingService
    ) -> None:
        """Test that completely different names return low match score."""
        score = service.calculate_name_match_score(
            "Michael", "Johnson", "John", "Smith"
        )
        assert score < 30, f"Expected low score for different names, got {score}"

    def test_rounded_to_two_decimal_places(
        self, service: PersonMatchingService
    ) -> None:
        """Test that score is rounded to 2 decimal places."""
        score = service.calculate_name_match_score("Jon", "Smith", "John", "Smith")
        # Check that we have at most 2 decimal places
        decimal_places = len(str(score).split(".")[-1])
        assert decimal_places <= 2, f"Expected max 2 decimal places, got {score}"

    def test_partial_first_name_match(self, service: PersonMatchingService) -> None:
        """Test partial first name match with exact last name match."""
        score = service.calculate_name_match_score("Rob", "Smith", "Robert", "Smith")
        # Should have high score due to exact last name match (60% weight)
        assert score > 70, f"Expected high score due to last name match, got {score}"

    def test_partial_last_name_match(self, service: PersonMatchingService) -> None:
        """Test exact first name match with partial last name match."""
        score = service.calculate_name_match_score("John", "Smith", "John", "Smyth")
        # Should have moderate score
        assert 80 < score < 100, f"Expected moderate-high score, got {score}"

    def test_empty_string_handling(self, service: PersonMatchingService) -> None:
        """Test handling of empty strings."""
        score = service.calculate_name_match_score("", "", "John", "Smith")
        assert score == 0.0, f"Expected 0 for empty strings, got {score}"

    def test_single_character_names(self, service: PersonMatchingService) -> None:
        """Test matching with single character names."""
        score = service.calculate_name_match_score("J", "S", "J", "S")
        assert score == 100.0, f"Expected 100 for exact single char match, got {score}"

    def test_special_characters_in_names(self, service: PersonMatchingService) -> None:
        """Test names with special characters like hyphens or apostrophes."""
        score = service.calculate_name_match_score(
            "Mary-Jane", "O'Brien", "Mary-Jane", "O'Brien"
        )
        assert score == 100.0, f"Expected 100 for exact match with special chars, got {score}"

    def test_unicode_characters(self, service: PersonMatchingService) -> None:
        """Test names with unicode characters."""
        score = service.calculate_name_match_score("José", "García", "José", "García")
        assert score == 100.0, f"Expected 100 for exact unicode match, got {score}"

    def test_very_long_names(self, service: PersonMatchingService) -> None:
        """Test matching with very long names."""
        long_first = "Christopher"
        long_last = "Schwarzenegger"
        score = service.calculate_name_match_score(
            long_first, long_last, long_first, long_last
        )
        assert score == 100.0, f"Expected 100 for exact long name match, got {score}"

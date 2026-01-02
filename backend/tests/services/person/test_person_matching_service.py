"""Unit tests for PersonMatchingService."""

import pytest
from sqlmodel import Session

from app.services.person.person_matching_service import PersonMatchingService


@pytest.mark.unit
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


@pytest.mark.unit
class TestMatchScoreThresholds:
    """Tests for match score threshold filtering."""

    @pytest.fixture
    def service(self, db: Session) -> PersonMatchingService:
        """Create a PersonMatchingService instance for testing."""
        return PersonMatchingService(db)

    def test_score_above_threshold_40(self, service: PersonMatchingService) -> None:
        """Test that scores above 40% threshold are valid matches."""
        # Similar names should score above 40%
        score = service.calculate_name_match_score("John", "Smith", "Jon", "Smith")
        assert score >= 40, f"Expected score >= 40, got {score}"

    def test_score_below_threshold_40(self, service: PersonMatchingService) -> None:
        """Test that completely different names score below 40%."""
        score = service.calculate_name_match_score("Xyz", "Abc", "John", "Smith")
        assert score < 40, f"Expected score < 40 for completely different names, got {score}"

    def test_boundary_score_near_40(self, service: PersonMatchingService) -> None:
        """Test names that produce scores near the 40% boundary."""
        # Names with some similarity but not much
        score = service.calculate_name_match_score("Mike", "Brown", "John", "Smith")
        # This should be below 40% as names are quite different
        assert score < 40, f"Expected score < 40 for different names, got {score}"


@pytest.mark.unit
class TestFuzzyMatchingEdgeCases:
    """Tests for fuzzy matching edge cases."""

    @pytest.fixture
    def service(self, db: Session) -> PersonMatchingService:
        """Create a PersonMatchingService instance for testing."""
        return PersonMatchingService(db)

    def test_transposed_letters(self, service: PersonMatchingService) -> None:
        """Test matching with transposed letters (common typo)."""
        score = service.calculate_name_match_score("Jhon", "Smtih", "John", "Smith")
        # Should still have reasonable score due to fuzzy matching
        assert score > 70, f"Expected score > 70 for transposed letters, got {score}"

    def test_missing_letter(self, service: PersonMatchingService) -> None:
        """Test matching with missing letter."""
        score = service.calculate_name_match_score("Jon", "Smth", "John", "Smith")
        assert score > 70, f"Expected score > 70 for missing letters, got {score}"

    def test_extra_letter(self, service: PersonMatchingService) -> None:
        """Test matching with extra letter."""
        score = service.calculate_name_match_score("Johnn", "Smithh", "John", "Smith")
        assert score > 80, f"Expected score > 80 for extra letters, got {score}"

    def test_phonetically_similar_names(self, service: PersonMatchingService) -> None:
        """Test matching phonetically similar names."""
        # Catherine vs Katherine
        score = service.calculate_name_match_score("Catherine", "Smith", "Katherine", "Smith")
        assert score > 80, f"Expected score > 80 for phonetically similar names, got {score}"

    def test_nickname_vs_full_name(self, service: PersonMatchingService) -> None:
        """Test matching nickname against full name."""
        # Bob vs Robert - these are quite different strings
        score = service.calculate_name_match_score("Bob", "Smith", "Robert", "Smith")
        # Last name matches (60% weight), first name is different
        assert score > 50, f"Expected score > 50 due to last name match, got {score}"

    def test_double_letters(self, service: PersonMatchingService) -> None:
        """Test matching with double letters."""
        score = service.calculate_name_match_score("Annn", "Smitth", "Ann", "Smith")
        assert score > 80, f"Expected score > 80 for double letters, got {score}"

    def test_mixed_case_variations(self, service: PersonMatchingService) -> None:
        """Test matching with various case combinations."""
        score = service.calculate_name_match_score("jOhN", "sMiTh", "JoHn", "SmItH")
        assert score == 100.0, f"Expected 100 for case-insensitive match, got {score}"


@pytest.mark.unit
class TestBuildMatchResult:
    """Tests for building match results."""

    @pytest.fixture
    def service(self, db: Session) -> PersonMatchingService:
        """Create a PersonMatchingService instance for testing."""
        return PersonMatchingService(db)

    def test_build_match_result_nonexistent_person(self, service: PersonMatchingService) -> None:
        """Test building match result for non-existent person returns None."""
        import uuid
        
        result = service._build_match_result(
            person_id=uuid.uuid4(),  # Non-existent ID
            name_score=85.0,
            address_display="Test Address",
            religion_display="Test Religion",
            is_current_user=False,
            is_already_connected=False,
        )
        
        assert result is None


@pytest.mark.unit
class TestNameMatchScoreVariations:
    """Tests for various name match score scenarios."""

    @pytest.fixture
    def service(self, db: Session) -> PersonMatchingService:
        """Create a PersonMatchingService instance for testing."""
        return PersonMatchingService(db)

    def test_first_name_only_different(self, service: PersonMatchingService) -> None:
        """Test score when only first name is different."""
        score = service.calculate_name_match_score("Alice", "Smith", "Bob", "Smith")
        # Last name matches (60% weight), first name different
        # Expected: 0 * 0.4 + 100 * 0.6 = 60
        assert 55 <= score <= 65, f"Expected score around 60, got {score}"

    def test_last_name_only_different(self, service: PersonMatchingService) -> None:
        """Test score when only last name is different."""
        score = service.calculate_name_match_score("John", "Smith", "John", "Jones")
        # First name matches (40% weight), last name different
        # Expected: 100 * 0.4 + ~20 * 0.6 = 40 + 12 = ~52
        assert 45 <= score <= 60, f"Expected score around 52, got {score}"

    def test_both_names_partially_similar(self, service: PersonMatchingService) -> None:
        """Test score when both names are partially similar."""
        score = service.calculate_name_match_score("John", "Smith", "Jon", "Smyth")
        # Both names similar but not exact
        assert 80 <= score <= 95, f"Expected score between 80-95, got {score}"

    def test_swapped_first_and_last_names(self, service: PersonMatchingService) -> None:
        """Test score when first and last names are swapped."""
        score = service.calculate_name_match_score("Smith", "John", "John", "Smith")
        # Names are swapped, so neither matches well
        assert score < 50, f"Expected low score for swapped names, got {score}"

    def test_numeric_characters_in_names(self, service: PersonMatchingService) -> None:
        """Test handling of numeric characters in names."""
        score = service.calculate_name_match_score("John3", "Smith2", "John3", "Smith2")
        assert score == 100.0, f"Expected 100 for exact match with numbers, got {score}"

    def test_very_short_vs_very_long_name(self, service: PersonMatchingService) -> None:
        """Test matching very short name against very long name."""
        score = service.calculate_name_match_score("Jo", "S", "Jonathan", "Smitherson")
        # Very different lengths should result in low score
        assert score < 50, f"Expected low score for length mismatch, got {score}"

    def test_repeated_characters(self, service: PersonMatchingService) -> None:
        """Test names with repeated characters."""
        score = service.calculate_name_match_score("Aaa", "Bbb", "Aaa", "Bbb")
        assert score == 100.0, f"Expected 100 for exact match, got {score}"

    def test_all_same_character(self, service: PersonMatchingService) -> None:
        """Test names that are all the same character."""
        score = service.calculate_name_match_score("aaaa", "bbbb", "aaaa", "bbbb")
        assert score == 100.0, f"Expected 100 for exact match, got {score}"

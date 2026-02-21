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


import uuid
from datetime import date
from unittest.mock import MagicMock, patch

from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_religion import PersonReligion
from app.schemas.person.person_search import PersonSearchRequest


@pytest.mark.unit
class TestFindPersonsByAddress:
    """Tests for _find_persons_by_address method."""

    def test_find_persons_by_address_required_fields_only(self) -> None:
        """Test finding persons with only required address fields."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        country_id = uuid.uuid4()
        state_id = uuid.uuid4()
        district_id = uuid.uuid4()
        person_id = uuid.uuid4()

        # Mock the session.exec to return person IDs
        mock_session.exec.return_value.all.return_value = [person_id]

        result = service._find_persons_by_address(
            country_id=country_id,
            state_id=state_id,
            district_id=district_id,
        )

        assert len(result) == 1
        assert result[0] == person_id
        mock_session.exec.assert_called_once()

    def test_find_persons_by_address_with_sub_district(self) -> None:
        """Test finding persons with sub_district filter."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        country_id = uuid.uuid4()
        state_id = uuid.uuid4()
        district_id = uuid.uuid4()
        sub_district_id = uuid.uuid4()
        person_id = uuid.uuid4()

        mock_session.exec.return_value.all.return_value = [person_id]

        result = service._find_persons_by_address(
            country_id=country_id,
            state_id=state_id,
            district_id=district_id,
            sub_district_id=sub_district_id,
        )

        assert len(result) == 1
        assert result[0] == person_id

    def test_find_persons_by_address_with_locality(self) -> None:
        """Test finding persons with locality filter."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        country_id = uuid.uuid4()
        state_id = uuid.uuid4()
        district_id = uuid.uuid4()
        locality_id = uuid.uuid4()
        person_id = uuid.uuid4()

        mock_session.exec.return_value.all.return_value = [person_id]

        result = service._find_persons_by_address(
            country_id=country_id,
            state_id=state_id,
            district_id=district_id,
            locality_id=locality_id,
        )

        assert len(result) == 1
        assert result[0] == person_id

    def test_find_persons_by_address_all_criteria(self) -> None:
        """Test finding persons with all address criteria."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        country_id = uuid.uuid4()
        state_id = uuid.uuid4()
        district_id = uuid.uuid4()
        sub_district_id = uuid.uuid4()
        locality_id = uuid.uuid4()
        person_ids = [uuid.uuid4(), uuid.uuid4()]

        mock_session.exec.return_value.all.return_value = person_ids

        result = service._find_persons_by_address(
            country_id=country_id,
            state_id=state_id,
            district_id=district_id,
            sub_district_id=sub_district_id,
            locality_id=locality_id,
        )

        assert len(result) == 2
        assert result == person_ids

    def test_find_persons_by_address_no_matches(self) -> None:
        """Test finding persons when no matches exist."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        mock_session.exec.return_value.all.return_value = []

        result = service._find_persons_by_address(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
        )

        assert len(result) == 0


@pytest.mark.unit
class TestFindPersonsByReligion:
    """Tests for _find_persons_by_religion method."""

    def test_find_persons_by_religion_required_field_only(self) -> None:
        """Test finding persons with only required religion field."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        religion_id = uuid.uuid4()
        person_id = uuid.uuid4()

        mock_session.exec.return_value.all.return_value = [person_id]

        result = service._find_persons_by_religion(religion_id=religion_id)

        assert len(result) == 1
        assert result[0] == person_id

    def test_find_persons_by_religion_with_category(self) -> None:
        """Test finding persons with religion category filter."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        religion_id = uuid.uuid4()
        category_id = uuid.uuid4()
        person_id = uuid.uuid4()

        mock_session.exec.return_value.all.return_value = [person_id]

        result = service._find_persons_by_religion(
            religion_id=religion_id,
            religion_category_id=category_id,
        )

        assert len(result) == 1
        assert result[0] == person_id

    def test_find_persons_by_religion_with_sub_category(self) -> None:
        """Test finding persons with religion sub-category filter."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        religion_id = uuid.uuid4()
        sub_category_id = uuid.uuid4()
        person_id = uuid.uuid4()

        mock_session.exec.return_value.all.return_value = [person_id]

        result = service._find_persons_by_religion(
            religion_id=religion_id,
            religion_sub_category_id=sub_category_id,
        )

        assert len(result) == 1
        assert result[0] == person_id

    def test_find_persons_by_religion_all_criteria(self) -> None:
        """Test finding persons with all religion criteria."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        religion_id = uuid.uuid4()
        category_id = uuid.uuid4()
        sub_category_id = uuid.uuid4()
        person_ids = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]

        mock_session.exec.return_value.all.return_value = person_ids

        result = service._find_persons_by_religion(
            religion_id=religion_id,
            religion_category_id=category_id,
            religion_sub_category_id=sub_category_id,
        )

        assert len(result) == 3
        assert result == person_ids

    def test_find_persons_by_religion_no_matches(self) -> None:
        """Test finding persons when no matches exist."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        mock_session.exec.return_value.all.return_value = []

        result = service._find_persons_by_religion(religion_id=uuid.uuid4())

        assert len(result) == 0


@pytest.mark.unit
class TestSearchMatchingPersons:
    """Tests for search_matching_persons method."""

    def test_search_matching_persons_no_address_matches(self) -> None:
        """Test search returns empty when no address matches."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        current_user_id = uuid.uuid4()
        search_criteria = PersonSearchRequest(
            first_name="John",
            last_name="Doe",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
        )

        with patch.object(service, "_find_persons_by_address", return_value=[]):
            with patch.object(service, "_find_persons_by_religion", return_value=[uuid.uuid4()]):
                result = service.search_matching_persons(current_user_id, search_criteria)

        assert len(result) == 0

    def test_search_matching_persons_no_religion_matches(self) -> None:
        """Test search returns empty when no religion matches."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        current_user_id = uuid.uuid4()
        search_criteria = PersonSearchRequest(
            first_name="John",
            last_name="Doe",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
        )

        with patch.object(service, "_find_persons_by_address", return_value=[uuid.uuid4()]):
            with patch.object(service, "_find_persons_by_religion", return_value=[]):
                result = service.search_matching_persons(current_user_id, search_criteria)

        assert len(result) == 0

    def test_search_matching_persons_no_intersection(self) -> None:
        """Test search returns empty when address and religion don't intersect."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        current_user_id = uuid.uuid4()
        search_criteria = PersonSearchRequest(
            first_name="John",
            last_name="Doe",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
        )

        # Different person IDs from address and religion queries
        address_person_id = uuid.uuid4()
        religion_person_id = uuid.uuid4()

        with patch.object(service, "_find_persons_by_address", return_value=[address_person_id]):
            with patch.object(service, "_find_persons_by_religion", return_value=[religion_person_id]):
                result = service.search_matching_persons(current_user_id, search_criteria)

        assert len(result) == 0

    def test_search_matching_persons_no_current_user_person(self) -> None:
        """Test search returns empty when current user has no person record."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        current_user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        search_criteria = PersonSearchRequest(
            first_name="John",
            last_name="Doe",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
        )

        # Mock person found in both address and religion
        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"
        mock_person.gender_id = None

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(service, "_find_persons_by_address", return_value=[person_id]):
            with patch.object(service, "_find_persons_by_religion", return_value=[person_id]):
                with patch.object(service.person_repo, "get_by_user_id", return_value=None):
                    result = service.search_matching_persons(current_user_id, search_criteria)

        assert len(result) == 0

    def test_search_matching_persons_with_gender_filter(self) -> None:
        """Test search applies gender filter when provided."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        current_user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        current_person_id = uuid.uuid4()
        gender_id = uuid.uuid4()

        search_criteria = PersonSearchRequest(
            first_name="John",
            last_name="Doe",
            gender_id=gender_id,
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
        )

        # Mock person
        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"
        mock_person.middle_name = None
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.date_of_death = None
        mock_person.gender_id = gender_id

        # Mock current user's person
        mock_current_person = MagicMock(spec=Person)
        mock_current_person.id = current_person_id

        mock_session.exec.return_value.all.return_value = [mock_person]
        mock_session.exec.return_value.first.return_value = mock_person

        with patch.object(service, "_find_persons_by_address", return_value=[person_id]):
            with patch.object(service, "_find_persons_by_religion", return_value=[person_id]):
                with patch.object(service.person_repo, "get_by_user_id", return_value=mock_current_person):
                    with patch.object(service.relationship_repo, "get_by_person_id", return_value=[]):
                        with patch.object(service, "_get_person_address_display", return_value="Test Address"):
                            with patch.object(service, "_get_person_religion_display", return_value="Test Religion"):
                                result = service.search_matching_persons(current_user_id, search_criteria)

        # Should have results (exact name match = 100 score, above 40 threshold)
        assert len(result) == 1
        assert result[0].first_name == "John"

    def test_search_matching_persons_filters_below_threshold(self) -> None:
        """Test search filters out persons with name score below 40%."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        current_user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        current_person_id = uuid.uuid4()

        search_criteria = PersonSearchRequest(
            first_name="Xyz",
            last_name="Abc",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
        )

        # Mock person with completely different name
        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.last_name = "Smith"
        mock_person.middle_name = None
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.date_of_death = None
        mock_person.gender_id = None

        mock_current_person = MagicMock(spec=Person)
        mock_current_person.id = current_person_id

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(service, "_find_persons_by_address", return_value=[person_id]):
            with patch.object(service, "_find_persons_by_religion", return_value=[person_id]):
                with patch.object(service.person_repo, "get_by_user_id", return_value=mock_current_person):
                    with patch.object(service.relationship_repo, "get_by_person_id", return_value=[]):
                        result = service.search_matching_persons(current_user_id, search_criteria)

        # Should be empty because name score is below 40%
        assert len(result) == 0

    def test_search_matching_persons_marks_current_user(self) -> None:
        """Test search marks current user's person record."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        current_user_id = uuid.uuid4()
        person_id = uuid.uuid4()

        search_criteria = PersonSearchRequest(
            first_name="John",
            last_name="Doe",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
        )

        # Mock person (same as current user's person)
        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"
        mock_person.middle_name = None
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.date_of_death = None
        mock_person.gender_id = None

        # Current user's person is the same as the found person
        mock_current_person = MagicMock(spec=Person)
        mock_current_person.id = person_id

        mock_session.exec.return_value.all.return_value = [mock_person]
        mock_session.exec.return_value.first.return_value = mock_person

        with patch.object(service, "_find_persons_by_address", return_value=[person_id]):
            with patch.object(service, "_find_persons_by_religion", return_value=[person_id]):
                with patch.object(service.person_repo, "get_by_user_id", return_value=mock_current_person):
                    with patch.object(service.relationship_repo, "get_by_person_id", return_value=[]):
                        with patch.object(service, "_get_person_address_display", return_value="Test Address"):
                            with patch.object(service, "_get_person_religion_display", return_value="Test Religion"):
                                result = service.search_matching_persons(current_user_id, search_criteria)

        assert len(result) == 1
        assert result[0].is_current_user is True

    def test_search_matching_persons_marks_already_connected(self) -> None:
        """Test search marks already connected persons."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        current_user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        current_person_id = uuid.uuid4()

        search_criteria = PersonSearchRequest(
            first_name="John",
            last_name="Doe",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
        )

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"
        mock_person.middle_name = None
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.date_of_death = None
        mock_person.gender_id = None

        mock_current_person = MagicMock(spec=Person)
        mock_current_person.id = current_person_id

        # Mock existing relationship
        mock_relationship = MagicMock()
        mock_relationship.related_person_id = person_id

        mock_session.exec.return_value.all.return_value = [mock_person]
        mock_session.exec.return_value.first.return_value = mock_person

        with patch.object(service, "_find_persons_by_address", return_value=[person_id]):
            with patch.object(service, "_find_persons_by_religion", return_value=[person_id]):
                with patch.object(service.person_repo, "get_by_user_id", return_value=mock_current_person):
                    with patch.object(service.relationship_repo, "get_by_person_id", return_value=[mock_relationship]):
                        with patch.object(service, "_get_person_address_display", return_value="Test Address"):
                            with patch.object(service, "_get_person_religion_display", return_value="Test Religion"):
                                result = service.search_matching_persons(current_user_id, search_criteria)

        assert len(result) == 1
        assert result[0].is_already_connected is True

    def test_search_matching_persons_sorts_by_score(self) -> None:
        """Test search results are sorted by match score descending."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        current_user_id = uuid.uuid4()
        person1_id = uuid.uuid4()
        person2_id = uuid.uuid4()
        current_person_id = uuid.uuid4()

        search_criteria = PersonSearchRequest(
            first_name="John",
            last_name="Smith",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
        )

        # Person 1: exact match (score 100)
        mock_person1 = MagicMock(spec=Person)
        mock_person1.id = person1_id
        mock_person1.first_name = "John"
        mock_person1.last_name = "Smith"
        mock_person1.middle_name = None
        mock_person1.date_of_birth = date(1990, 1, 1)
        mock_person1.date_of_death = None
        mock_person1.gender_id = None

        # Person 2: partial match (lower score)
        mock_person2 = MagicMock(spec=Person)
        mock_person2.id = person2_id
        mock_person2.first_name = "Jon"
        mock_person2.last_name = "Smyth"
        mock_person2.middle_name = None
        mock_person2.date_of_birth = date(1985, 5, 15)
        mock_person2.date_of_death = None
        mock_person2.gender_id = None

        mock_current_person = MagicMock(spec=Person)
        mock_current_person.id = current_person_id

        # Return persons in wrong order (person2 first)
        mock_session.exec.return_value.all.return_value = [mock_person2, mock_person1]

        def mock_first_side_effect():
            # Return different persons based on call
            return mock_person1

        mock_session.exec.return_value.first.side_effect = [mock_person2, mock_person1]

        with patch.object(service, "_find_persons_by_address", return_value=[person1_id, person2_id]):
            with patch.object(service, "_find_persons_by_religion", return_value=[person1_id, person2_id]):
                with patch.object(service.person_repo, "get_by_user_id", return_value=mock_current_person):
                    with patch.object(service.relationship_repo, "get_by_person_id", return_value=[]):
                        with patch.object(service, "_get_person_address_display", return_value="Test Address"):
                            with patch.object(service, "_get_person_religion_display", return_value="Test Religion"):
                                result = service.search_matching_persons(current_user_id, search_criteria)

        # Results should be sorted by score descending
        assert len(result) == 2
        assert result[0].match_score >= result[1].match_score

    def test_search_matching_persons_limits_to_100(self) -> None:
        """Test search limits results to 100."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        current_user_id = uuid.uuid4()
        current_person_id = uuid.uuid4()

        search_criteria = PersonSearchRequest(
            first_name="John",
            last_name="Doe",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
        )

        # Create 150 mock persons
        person_ids = [uuid.uuid4() for _ in range(150)]
        mock_persons = []
        for pid in person_ids:
            mock_person = MagicMock(spec=Person)
            mock_person.id = pid
            mock_person.first_name = "John"
            mock_person.last_name = "Doe"
            mock_person.middle_name = None
            mock_person.date_of_birth = date(1990, 1, 1)
            mock_person.date_of_death = None
            mock_person.gender_id = None
            mock_persons.append(mock_person)

        mock_current_person = MagicMock(spec=Person)
        mock_current_person.id = current_person_id

        mock_session.exec.return_value.all.return_value = mock_persons

        # Mock first() to return persons for _build_match_result
        mock_session.exec.return_value.first.side_effect = mock_persons

        with patch.object(service, "_find_persons_by_address", return_value=person_ids):
            with patch.object(service, "_find_persons_by_religion", return_value=person_ids):
                with patch.object(service.person_repo, "get_by_user_id", return_value=mock_current_person):
                    with patch.object(service.relationship_repo, "get_by_person_id", return_value=[]):
                        with patch.object(service, "_get_person_address_display", return_value="Test Address"):
                            with patch.object(service, "_get_person_religion_display", return_value="Test Religion"):
                                result = service.search_matching_persons(current_user_id, search_criteria)

        # Should be limited to 100
        assert len(result) <= 100

    def test_search_matching_persons_uses_display_strings(self) -> None:
        """Test search uses provided display strings."""
        mock_session = MagicMock()
        service = PersonMatchingService(mock_session)

        current_user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        current_person_id = uuid.uuid4()

        search_criteria = PersonSearchRequest(
            first_name="John",
            last_name="Doe",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            address_display="USA, California, Los Angeles",
            religion_display="Christianity, Catholic",
        )

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"
        mock_person.middle_name = None
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.date_of_death = None
        mock_person.gender_id = None

        mock_current_person = MagicMock(spec=Person)
        mock_current_person.id = current_person_id

        mock_session.exec.return_value.all.return_value = [mock_person]
        mock_session.exec.return_value.first.return_value = mock_person

        with patch.object(service, "_find_persons_by_address", return_value=[person_id]):
            with patch.object(service, "_find_persons_by_religion", return_value=[person_id]):
                with patch.object(service.person_repo, "get_by_user_id", return_value=mock_current_person):
                    with patch.object(service.relationship_repo, "get_by_person_id", return_value=[]):
                        with patch.object(service, "_get_person_address_display", return_value="USA, California, Los Angeles"):
                            with patch.object(service, "_get_person_religion_display", return_value="Christianity, Catholic"):
                                result = service.search_matching_persons(current_user_id, search_criteria)

        assert len(result) == 1
        assert result[0].address_display == "USA, California, Los Angeles"
        assert result[0].religion_display == "Christianity, Catholic"

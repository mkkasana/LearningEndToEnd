"""Unit tests for PersonSearchService.

Tests cover:
- Address filtering (Requirements 2.1, 2.2)
- Religion filtering (Requirements 2.3, 2.4)
- Demographic filtering (Requirements 2.5, 2.6)
- Name matching (Requirements 2.7, 2.8)
- Pagination and empty results (Requirements 2.9, 2.10)
"""

import uuid
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_religion import PersonReligion
from app.db_models.user import User
from app.enums import GenderEnum
from app.schemas.person.person_search import PersonSearchFilterRequest
from app.services.person.person_search_service import PersonSearchService
from tests.factories import PersonFactory, UserFactory


# =============================================================================
# Helper Functions for Test Data Setup
# =============================================================================


def create_test_address(
    session: Session,
    person_id: uuid.UUID,
    country_id: uuid.UUID,
    state_id: uuid.UUID,
    district_id: uuid.UUID,
    sub_district_id: uuid.UUID,
    locality_id: uuid.UUID | None = None,
) -> PersonAddress:
    """Create a PersonAddress record for testing."""
    address = PersonAddress(
        person_id=person_id,
        country_id=country_id,
        state_id=state_id,
        district_id=district_id,
        sub_district_id=sub_district_id,
        locality_id=locality_id,
        start_date=date(2020, 1, 1),
        is_current=True,
    )
    session.add(address)
    session.commit()
    session.refresh(address)
    return address


def create_test_religion(
    session: Session,
    person_id: uuid.UUID,
    religion_id: uuid.UUID,
    religion_category_id: uuid.UUID,
    religion_sub_category_id: uuid.UUID | None = None,
) -> PersonReligion:
    """Create a PersonReligion record for testing."""
    religion = PersonReligion(
        person_id=person_id,
        religion_id=religion_id,
        religion_category_id=religion_category_id,
        religion_sub_category_id=religion_sub_category_id,
    )
    session.add(religion)
    session.commit()
    session.refresh(religion)
    return religion


def create_person_with_address_and_religion(
    session: Session,
    user: User,
    first_name: str,
    last_name: str,
    country_id: uuid.UUID,
    state_id: uuid.UUID,
    district_id: uuid.UUID,
    sub_district_id: uuid.UUID,
    religion_id: uuid.UUID,
    religion_category_id: uuid.UUID,
    locality_id: uuid.UUID | None = None,
    religion_sub_category_id: uuid.UUID | None = None,
    gender: GenderEnum = GenderEnum.MALE,
    date_of_birth: date | None = None,
) -> Person:
    """Create a Person with associated address and religion records."""
    person = PersonFactory.create(
        session,
        created_by_user=user,
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        date_of_birth=date_of_birth or date(1990, 1, 1),
    )
    
    create_test_address(
        session,
        person.id,
        country_id,
        state_id,
        district_id,
        sub_district_id,
        locality_id,
    )
    
    create_test_religion(
        session,
        person.id,
        religion_id,
        religion_category_id,
        religion_sub_category_id,
    )
    
    return person


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def service(db: Session) -> PersonSearchService:
    """Create a PersonSearchService instance for testing."""
    return PersonSearchService(db)


@pytest.fixture
def test_user_for_search(db: Session) -> User:
    """Create a test user for search tests."""
    return UserFactory.create(db)


@pytest.fixture
def address_ids() -> dict[str, uuid.UUID]:
    """Generate consistent address IDs for testing."""
    return {
        "country_id": uuid.uuid4(),
        "state_id": uuid.uuid4(),
        "district_id": uuid.uuid4(),
        "sub_district_id": uuid.uuid4(),
        "locality_id": uuid.uuid4(),
    }


@pytest.fixture
def religion_ids() -> dict[str, uuid.UUID]:
    """Generate consistent religion IDs for testing."""
    return {
        "religion_id": uuid.uuid4(),
        "religion_category_id": uuid.uuid4(),
        "religion_sub_category_id": uuid.uuid4(),
    }


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestCalculateNameMatchScore:
    """Tests for the calculate_name_match_score method.
    
    Validates: Requirements 2.7, 2.8
    """

    @pytest.fixture
    def service(self, db: Session) -> PersonSearchService:
        """Create a PersonSearchService instance for testing."""
        return PersonSearchService(db)

    def test_exact_match_returns_100(self, service: PersonSearchService) -> None:
        """Test that exact name match returns score of 100."""
        score = service.calculate_name_match_score("John", "Smith", "John", "Smith")
        assert score == 100.0

    def test_case_insensitive_matching(self, service: PersonSearchService) -> None:
        """Test that matching is case insensitive."""
        score = service.calculate_name_match_score("JOHN", "SMITH", "john", "smith")
        assert score == 100.0

    def test_whitespace_normalization(self, service: PersonSearchService) -> None:
        """Test that leading/trailing whitespace is handled correctly."""
        score = service.calculate_name_match_score(
            "  John  ", "  Smith  ", "John", "Smith"
        )
        assert score == 100.0

    def test_weighted_average_first_name_priority(
        self, service: PersonSearchService
    ) -> None:
        """Test that first name has higher weight (60%) than last name (40%).
        
        Note: PersonSearchService uses 60% first name, 40% last name weighting.
        """
        # Different first names, same last name
        score1 = service.calculate_name_match_score("John", "Smith", "Michael", "Smith")

        # Same first names, different last name
        score2 = service.calculate_name_match_score("John", "Smith", "John", "Johnson")

        # Score2 should be higher because first name (60% weight) matches
        assert (
            score2 > score1
        ), f"Expected score2 ({score2}) > score1 ({score1}) due to first name having 60% weight"

    def test_completely_different_names_low_score(
        self, service: PersonSearchService
    ) -> None:
        """Test that completely different names return low match score."""
        score = service.calculate_name_match_score(
            "Michael", "Johnson", "John", "Smith"
        )
        assert score < 40, f"Expected low score for different names, got {score}"

    def test_rounded_to_two_decimal_places(
        self, service: PersonSearchService
    ) -> None:
        """Test that score is rounded to 2 decimal places."""
        score = service.calculate_name_match_score("Jon", "Smith", "John", "Smith")
        # Check that we have at most 2 decimal places
        decimal_places = len(str(score).split(".")[-1])
        assert decimal_places <= 2, f"Expected max 2 decimal places, got {score}"

    def test_empty_string_handling(self, service: PersonSearchService) -> None:
        """Test handling of empty strings."""
        score = service.calculate_name_match_score("", "", "John", "Smith")
        assert score == 0.0, f"Expected 0 for empty strings, got {score}"

    def test_fuzzy_match_high_score(self, service: PersonSearchService) -> None:
        """Test that similar names (Jon vs John) return high match score."""
        score = service.calculate_name_match_score("Jon", "Smith", "John", "Smith")
        assert score > 80, f"Expected high score for similar names, got {score}"



@pytest.mark.unit
class TestFindPersonsByAddress:
    """Tests for _find_persons_by_address method.
    
    Validates: Requirements 2.1, 2.2
    """

    def test_find_persons_by_address_required_fields(self) -> None:
        """Test finding persons with required address fields."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

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
        mock_session.exec.assert_called_once()

    def test_find_persons_by_address_with_locality(self) -> None:
        """Test finding persons with optional locality filter."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

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
        service = PersonSearchService(mock_session)

        mock_session.exec.return_value.all.return_value = []

        result = service._find_persons_by_address(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
        )

        assert len(result) == 0

    def test_find_persons_by_address_multiple_matches(self) -> None:
        """Test finding multiple persons matching address criteria."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_ids = [uuid.uuid4() for _ in range(5)]
        mock_session.exec.return_value.all.return_value = person_ids

        result = service._find_persons_by_address(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
        )

        assert len(result) == 5
        assert result == person_ids


@pytest.mark.unit
class TestFindPersonsByReligion:
    """Tests for _find_persons_by_religion method.
    
    Validates: Requirements 2.3, 2.4
    """

    def test_find_persons_by_religion_required_fields(self) -> None:
        """Test finding persons with required religion fields."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        religion_id = uuid.uuid4()
        religion_category_id = uuid.uuid4()
        person_id = uuid.uuid4()

        mock_session.exec.return_value.all.return_value = [person_id]

        result = service._find_persons_by_religion(
            religion_id=religion_id,
            religion_category_id=religion_category_id,
        )

        assert len(result) == 1
        assert result[0] == person_id

    def test_find_persons_by_religion_with_sub_category(self) -> None:
        """Test finding persons with optional sub-category filter."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        religion_id = uuid.uuid4()
        religion_category_id = uuid.uuid4()
        religion_sub_category_id = uuid.uuid4()
        person_ids = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]

        mock_session.exec.return_value.all.return_value = person_ids

        result = service._find_persons_by_religion(
            religion_id=religion_id,
            religion_category_id=religion_category_id,
            religion_sub_category_id=religion_sub_category_id,
        )

        assert len(result) == 3
        assert result == person_ids

    def test_find_persons_by_religion_no_matches(self) -> None:
        """Test finding persons when no matches exist."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        mock_session.exec.return_value.all.return_value = []

        result = service._find_persons_by_religion(
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        assert len(result) == 0



@pytest.mark.unit
class TestSearchPersonsAddressAndReligionIntersection:
    """Tests for address and religion filter intersection.
    
    Validates: Requirements 2.1, 2.2, 2.3, 2.4
    """

    def test_search_returns_empty_when_no_address_matches(self) -> None:
        """Test search returns empty when no address matches."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        with patch.object(service, "_find_persons_by_address", return_value=[]):
            with patch.object(
                service, "_find_persons_by_religion", return_value=[uuid.uuid4()]
            ):
                result = service.search_persons(request)

        assert result.total == 0
        assert len(result.results) == 0

    def test_search_returns_empty_when_no_religion_matches(self) -> None:
        """Test search returns empty when no religion matches."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        with patch.object(
            service, "_find_persons_by_address", return_value=[uuid.uuid4()]
        ):
            with patch.object(service, "_find_persons_by_religion", return_value=[]):
                result = service.search_persons(request)

        assert result.total == 0
        assert len(result.results) == 0

    def test_search_returns_empty_when_no_intersection(self) -> None:
        """Test search returns empty when address and religion don't intersect."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        # Different person IDs from address and religion queries
        address_person_id = uuid.uuid4()
        religion_person_id = uuid.uuid4()

        with patch.object(
            service, "_find_persons_by_address", return_value=[address_person_id]
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=[religion_person_id]
            ):
                result = service.search_persons(request)

        assert result.total == 0
        assert len(result.results) == 0

    def test_search_returns_intersection_of_address_and_religion(self) -> None:
        """Test search returns only persons matching both address and religion."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        # Common person ID in both queries
        common_person_id = uuid.uuid4()
        address_only_id = uuid.uuid4()
        religion_only_id = uuid.uuid4()

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        # Mock person
        mock_person = MagicMock(spec=Person)
        mock_person.id = common_person_id
        mock_person.first_name = "John"
        mock_person.middle_name = None
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.gender_id = None

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(
            service,
            "_find_persons_by_address",
            return_value=[common_person_id, address_only_id],
        ):
            with patch.object(
                service,
                "_find_persons_by_religion",
                return_value=[common_person_id, religion_only_id],
            ):
                result = service.search_persons(request)

        # Should only return the common person
        assert result.total == 1


@pytest.mark.unit
class TestSearchPersonsDemographicFilters:
    """Tests for demographic filtering (gender and birth year).
    
    Validates: Requirements 2.5, 2.6
    """

    def test_search_with_gender_filter(self) -> None:
        """Test search applies gender filter when provided."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_id = uuid.uuid4()
        gender_id = uuid.uuid4()

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
            gender_id=gender_id,
        )

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.middle_name = None
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.gender_id = gender_id

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(
            service, "_find_persons_by_address", return_value=[person_id]
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=[person_id]
            ):
                result = service.search_persons(request)

        assert result.total == 1
        assert result.results[0].first_name == "John"

    def test_search_with_birth_year_from_filter(self) -> None:
        """Test search applies birth_year_from filter."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_id = uuid.uuid4()

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
            birth_year_from=1985,
        )

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.middle_name = None
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.gender_id = None

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(
            service, "_find_persons_by_address", return_value=[person_id]
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=[person_id]
            ):
                result = service.search_persons(request)

        assert result.total == 1

    def test_search_with_birth_year_to_filter(self) -> None:
        """Test search applies birth_year_to filter."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_id = uuid.uuid4()

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
            birth_year_to=1995,
        )

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.middle_name = None
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.gender_id = None

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(
            service, "_find_persons_by_address", return_value=[person_id]
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=[person_id]
            ):
                result = service.search_persons(request)

        assert result.total == 1

    def test_search_with_birth_year_range_filter(self) -> None:
        """Test search applies both birth_year_from and birth_year_to filters."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_id = uuid.uuid4()

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
            birth_year_from=1985,
            birth_year_to=1995,
        )

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.middle_name = None
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.gender_id = None

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(
            service, "_find_persons_by_address", return_value=[person_id]
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=[person_id]
            ):
                result = service.search_persons(request)

        assert result.total == 1



@pytest.mark.unit
class TestSearchPersonsNameMatching:
    """Tests for name fuzzy matching functionality.
    
    Validates: Requirements 2.7, 2.8
    """

    def test_search_with_name_filter_exact_match(self) -> None:
        """Test search with exact name match returns high score."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_id = uuid.uuid4()

        request = PersonSearchFilterRequest(
            first_name="John",
            last_name="Doe",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.middle_name = None
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.gender_id = None

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(
            service, "_find_persons_by_address", return_value=[person_id]
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=[person_id]
            ):
                result = service.search_persons(request)

        assert result.total == 1
        assert result.results[0].name_match_score == 100.0

    def test_search_with_name_filter_fuzzy_match(self) -> None:
        """Test search with fuzzy name match returns appropriate score."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_id = uuid.uuid4()

        request = PersonSearchFilterRequest(
            first_name="Jon",  # Similar to John
            last_name="Doe",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.middle_name = None
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.gender_id = None

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(
            service, "_find_persons_by_address", return_value=[person_id]
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=[person_id]
            ):
                result = service.search_persons(request)

        assert result.total == 1
        # Score should be above threshold (40%) but less than 100
        assert result.results[0].name_match_score is not None
        assert 40 <= result.results[0].name_match_score < 100

    def test_search_filters_below_40_percent_threshold(self) -> None:
        """Test search filters out persons with name score below 40%."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_id = uuid.uuid4()

        request = PersonSearchFilterRequest(
            first_name="Xyz",  # Completely different
            last_name="Abc",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.middle_name = None
        mock_person.last_name = "Smith"
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.gender_id = None

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(
            service, "_find_persons_by_address", return_value=[person_id]
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=[person_id]
            ):
                result = service.search_persons(request)

        # Should be empty because name score is below 40%
        assert result.total == 0
        assert len(result.results) == 0

    def test_search_sorts_by_name_match_score_descending(self) -> None:
        """Test search results are sorted by name match score descending."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_id_1 = uuid.uuid4()
        person_id_2 = uuid.uuid4()

        request = PersonSearchFilterRequest(
            first_name="John",
            last_name="Smith",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        # Person with exact match
        mock_person_1 = MagicMock(spec=Person)
        mock_person_1.id = person_id_1
        mock_person_1.first_name = "John"
        mock_person_1.middle_name = None
        mock_person_1.last_name = "Smith"
        mock_person_1.date_of_birth = date(1990, 1, 1)
        mock_person_1.gender_id = None

        # Person with partial match
        mock_person_2 = MagicMock(spec=Person)
        mock_person_2.id = person_id_2
        mock_person_2.first_name = "Jon"  # Similar but not exact
        mock_person_2.middle_name = None
        mock_person_2.last_name = "Smith"
        mock_person_2.date_of_birth = date(1985, 1, 1)
        mock_person_2.gender_id = None

        mock_session.exec.return_value.all.return_value = [
            mock_person_2,
            mock_person_1,
        ]

        with patch.object(
            service,
            "_find_persons_by_address",
            return_value=[person_id_1, person_id_2],
        ):
            with patch.object(
                service,
                "_find_persons_by_religion",
                return_value=[person_id_1, person_id_2],
            ):
                result = service.search_persons(request)

        assert result.total == 2
        # First result should have higher score (exact match)
        assert result.results[0].name_match_score >= result.results[1].name_match_score

    def test_search_without_name_filter_returns_no_score(self) -> None:
        """Test search without name filter returns results without name_match_score."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_id = uuid.uuid4()

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.middle_name = None
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.gender_id = None

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(
            service, "_find_persons_by_address", return_value=[person_id]
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=[person_id]
            ):
                result = service.search_persons(request)

        assert result.total == 1
        assert result.results[0].name_match_score is None


@pytest.mark.unit
class TestSearchPersonsPagination:
    """Tests for pagination functionality.
    
    Validates: Requirements 2.9, 2.10
    """

    def test_search_with_skip_parameter(self) -> None:
        """Test search applies skip parameter correctly."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_ids = [uuid.uuid4() for _ in range(5)]

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
            skip=2,
            limit=10,
        )

        mock_persons = []
        for i, pid in enumerate(person_ids):
            mock_person = MagicMock(spec=Person)
            mock_person.id = pid
            mock_person.first_name = f"Person{i}"
            mock_person.middle_name = None
            mock_person.last_name = f"Last{i}"
            mock_person.date_of_birth = date(1990, 1, 1)
            mock_person.gender_id = None
            mock_persons.append(mock_person)

        mock_session.exec.return_value.all.return_value = mock_persons

        with patch.object(
            service, "_find_persons_by_address", return_value=person_ids
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=person_ids
            ):
                result = service.search_persons(request)

        assert result.total == 5
        assert result.skip == 2
        assert len(result.results) == 3  # 5 - 2 = 3 remaining

    def test_search_with_limit_parameter(self) -> None:
        """Test search applies limit parameter correctly."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_ids = [uuid.uuid4() for _ in range(10)]

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
            skip=0,
            limit=5,
        )

        mock_persons = []
        for i, pid in enumerate(person_ids):
            mock_person = MagicMock(spec=Person)
            mock_person.id = pid
            mock_person.first_name = f"Person{i}"
            mock_person.middle_name = None
            mock_person.last_name = f"Last{i}"
            mock_person.date_of_birth = date(1990, 1, 1)
            mock_person.gender_id = None
            mock_persons.append(mock_person)

        mock_session.exec.return_value.all.return_value = mock_persons

        with patch.object(
            service, "_find_persons_by_address", return_value=person_ids
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=person_ids
            ):
                result = service.search_persons(request)

        assert result.total == 10
        assert result.limit == 5
        assert len(result.results) == 5

    def test_search_empty_results_returns_zero_total(self) -> None:
        """Test search returns total=0 when no matches found."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        with patch.object(service, "_find_persons_by_address", return_value=[]):
            with patch.object(service, "_find_persons_by_religion", return_value=[]):
                result = service.search_persons(request)

        assert result.total == 0
        assert len(result.results) == 0
        assert result.skip == 0
        assert result.limit == 20  # Default limit

    def test_search_pagination_response_includes_metadata(self) -> None:
        """Test search response includes correct pagination metadata."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_id = uuid.uuid4()

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
            skip=5,
            limit=10,
        )

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.middle_name = None
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.gender_id = None

        mock_session.exec.return_value.all.return_value = [mock_person]

        with patch.object(
            service, "_find_persons_by_address", return_value=[person_id]
        ):
            with patch.object(
                service, "_find_persons_by_religion", return_value=[person_id]
            ):
                result = service.search_persons(request)

        assert result.skip == 5
        assert result.limit == 10
        # Total is 1, but skip is 5, so no results returned
        assert result.total == 1
        assert len(result.results) == 0  # Skipped past the only result

    def test_search_without_name_sorts_by_last_name(self) -> None:
        """Test search without name filter sorts results by last name."""
        mock_session = MagicMock()
        service = PersonSearchService(mock_session)

        person_id_1 = uuid.uuid4()
        person_id_2 = uuid.uuid4()
        person_id_3 = uuid.uuid4()

        request = PersonSearchFilterRequest(
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            religion_id=uuid.uuid4(),
            religion_category_id=uuid.uuid4(),
        )

        # Create persons with different last names
        mock_person_1 = MagicMock(spec=Person)
        mock_person_1.id = person_id_1
        mock_person_1.first_name = "John"
        mock_person_1.middle_name = None
        mock_person_1.last_name = "Zebra"  # Should be last
        mock_person_1.date_of_birth = date(1990, 1, 1)
        mock_person_1.gender_id = None

        mock_person_2 = MagicMock(spec=Person)
        mock_person_2.id = person_id_2
        mock_person_2.first_name = "Jane"
        mock_person_2.middle_name = None
        mock_person_2.last_name = "Apple"  # Should be first
        mock_person_2.date_of_birth = date(1985, 1, 1)
        mock_person_2.gender_id = None

        mock_person_3 = MagicMock(spec=Person)
        mock_person_3.id = person_id_3
        mock_person_3.first_name = "Bob"
        mock_person_3.middle_name = None
        mock_person_3.last_name = "Middle"  # Should be second
        mock_person_3.date_of_birth = date(1995, 1, 1)
        mock_person_3.gender_id = None

        mock_session.exec.return_value.all.return_value = [
            mock_person_1,
            mock_person_2,
            mock_person_3,
        ]

        with patch.object(
            service,
            "_find_persons_by_address",
            return_value=[person_id_1, person_id_2, person_id_3],
        ):
            with patch.object(
                service,
                "_find_persons_by_religion",
                return_value=[person_id_1, person_id_2, person_id_3],
            ):
                result = service.search_persons(request)

        assert result.total == 3
        # Results should be sorted by last name alphabetically
        assert result.results[0].last_name == "Apple"
        assert result.results[1].last_name == "Middle"
        assert result.results[2].last_name == "Zebra"

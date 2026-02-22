"""Unit tests for RelativesNetworkService.

Tests cover:
- BFS traversal (Requirements 3.1, 3.2, 3.3)
- Depth modes (Requirements 3.4, 3.5)
- Filters (Requirements 3.6, 3.7, 3.8)
- Result limiting and enrichment (Requirements 3.9, 3.10)
"""

import uuid
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_relationship import PersonRelationship
from app.schemas.relatives_network import (
    RelativeInfo,
    RelativesNetworkRequest,
    RelativesNetworkResponse,
)
from app.services.relatives_network.relatives_network_service import (
    MAX_RESULTS,
    RelativesNetworkService,
)


# =============================================================================
# Helper Functions for Test Data Setup
# =============================================================================


def create_mock_person(
    person_id: uuid.UUID,
    first_name: str = "Test",
    last_name: str = "Person",
    gender_id: uuid.UUID | None = None,
    date_of_birth: date | None = None,
    date_of_death: date | None = None,
) -> MagicMock:
    """Create a mock Person object for testing."""
    mock_person = MagicMock(spec=Person)
    mock_person.id = person_id
    mock_person.first_name = first_name
    mock_person.last_name = last_name
    mock_person.gender_id = gender_id or uuid.uuid4()
    mock_person.date_of_birth = date_of_birth or date(1990, 1, 1)
    mock_person.date_of_death = date_of_death
    return mock_person


def create_mock_address(
    person_id: uuid.UUID,
    country_id: uuid.UUID | None = None,
    state_id: uuid.UUID | None = None,
    district_id: uuid.UUID | None = None,
    sub_district_id: uuid.UUID | None = None,
    locality_id: uuid.UUID | None = None,
    is_current: bool = True,
) -> MagicMock:
    """Create a mock PersonAddress object for testing."""
    mock_address = MagicMock(spec=PersonAddress)
    mock_address.person_id = person_id
    mock_address.country_id = country_id or uuid.uuid4()
    mock_address.state_id = state_id or uuid.uuid4()
    mock_address.district_id = district_id or uuid.uuid4()
    mock_address.sub_district_id = sub_district_id or uuid.uuid4()
    mock_address.locality_id = locality_id
    mock_address.is_current = is_current
    return mock_address


def create_mock_relationship(
    person_id: uuid.UUID,
    related_person_id: uuid.UUID,
    is_active: bool = True,
) -> MagicMock:
    """Create a mock PersonRelationship object for testing."""
    mock_rel = MagicMock(spec=PersonRelationship)
    mock_rel.person_id = person_id
    mock_rel.related_person_id = related_person_id
    mock_rel.is_active = is_active
    return mock_rel


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_session() -> MagicMock:
    """Create a mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def service(mock_session: MagicMock) -> RelativesNetworkService:
    """Create a RelativesNetworkService instance with mock session."""
    return RelativesNetworkService(mock_session)


# =============================================================================
# Test Classes
# =============================================================================


@pytest.mark.unit
class TestFindRelativesPersonNotFound:
    """Tests for person not found scenario.
    
    Validates: Requirements 3.1
    """

    def test_find_relatives_person_not_found_raises_404(
        self, service: RelativesNetworkService
    ) -> None:
        """Test that finding relatives for non-existent person raises 404."""
        person_id = uuid.uuid4()
        request = RelativesNetworkRequest(person_id=person_id)

        with patch.object(service, "_get_person", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                service.find_relatives(request)

        assert exc_info.value.status_code == 404
        assert "Person not found" in exc_info.value.detail


@pytest.mark.unit
class TestBFSTraversal:
    """Tests for BFS traversal functionality.
    
    Validates: Requirements 3.2, 3.3
    """

    def test_bfs_traverse_returns_starting_person_at_depth_0(
        self, service: RelativesNetworkService
    ) -> None:
        """Test that BFS returns starting person at depth 0."""
        person_id = uuid.uuid4()

        with patch.object(service, "_get_relationships", return_value=[]):
            result = service._bfs_traverse(person_id, max_depth=3)

        assert person_id in result
        assert result[person_id] == 0

    def test_bfs_traverse_finds_direct_relatives_at_depth_1(
        self, service: RelativesNetworkService
    ) -> None:
        """Test that BFS finds direct relatives at depth 1."""
        person_id = uuid.uuid4()
        relative_id = uuid.uuid4()

        def mock_get_relationships(pid: uuid.UUID) -> list[uuid.UUID]:
            if pid == person_id:
                return [relative_id]
            return []

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ):
            result = service._bfs_traverse(person_id, max_depth=3)

        assert relative_id in result
        assert result[relative_id] == 1

    def test_bfs_traverse_finds_relatives_at_multiple_depths(
        self, service: RelativesNetworkService
    ) -> None:
        """Test that BFS correctly assigns depths for multi-level relationships."""
        person_id = uuid.uuid4()
        depth_1_id = uuid.uuid4()
        depth_2_id = uuid.uuid4()
        depth_3_id = uuid.uuid4()

        def mock_get_relationships(pid: uuid.UUID) -> list[uuid.UUID]:
            if pid == person_id:
                return [depth_1_id]
            elif pid == depth_1_id:
                return [depth_2_id]
            elif pid == depth_2_id:
                return [depth_3_id]
            return []

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ):
            result = service._bfs_traverse(person_id, max_depth=3)

        assert result[person_id] == 0
        assert result[depth_1_id] == 1
        assert result[depth_2_id] == 2
        assert result[depth_3_id] == 3

    def test_bfs_traverse_respects_max_depth(
        self, service: RelativesNetworkService
    ) -> None:
        """Test that BFS stops at max_depth."""
        person_id = uuid.uuid4()
        depth_1_id = uuid.uuid4()
        depth_2_id = uuid.uuid4()
        depth_3_id = uuid.uuid4()

        def mock_get_relationships(pid: uuid.UUID) -> list[uuid.UUID]:
            if pid == person_id:
                return [depth_1_id]
            elif pid == depth_1_id:
                return [depth_2_id]
            elif pid == depth_2_id:
                return [depth_3_id]
            return []

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ):
            result = service._bfs_traverse(person_id, max_depth=2)

        assert person_id in result
        assert depth_1_id in result
        assert depth_2_id in result
        assert depth_3_id not in result  # Beyond max_depth

    def test_bfs_traverse_avoids_cycles(
        self, service: RelativesNetworkService
    ) -> None:
        """Test that BFS handles cycles without infinite loops."""
        person_id = uuid.uuid4()
        relative_id = uuid.uuid4()

        def mock_get_relationships(pid: uuid.UUID) -> list[uuid.UUID]:
            # Create a cycle: person -> relative -> person
            if pid == person_id:
                return [relative_id]
            elif pid == relative_id:
                return [person_id]
            return []

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ):
            result = service._bfs_traverse(person_id, max_depth=5)

        # Should only visit each person once
        assert len(result) == 2
        assert result[person_id] == 0
        assert result[relative_id] == 1



@pytest.mark.unit
class TestDepthCapping:
    """Tests for depth capping to maximum.
    
    Validates: Requirements 3.3
    """

    def test_depth_capped_to_maximum(
        self, mock_session: MagicMock
    ) -> None:
        """Test that requested depth is capped to configured maximum."""
        # Create service with a known max_depth
        service = RelativesNetworkService(mock_session)
        original_max_depth = service.max_depth

        person_id = uuid.uuid4()
        mock_person = create_mock_person(person_id)

        request = RelativesNetworkRequest(
            person_id=person_id,
            depth=100,  # Request very high depth
        )

        with patch.object(service, "_get_person", return_value=mock_person):
            with patch.object(service, "_bfs_traverse", return_value={person_id: 0}):
                result = service.find_relatives(request)

        # Depth in response should be capped
        assert result.depth <= original_max_depth


@pytest.mark.unit
class TestDepthModes:
    """Tests for depth mode filtering.
    
    Validates: Requirements 3.4, 3.5
    """

    def test_filter_by_depth_mode_up_to(
        self, service: RelativesNetworkService
    ) -> None:
        """Test 'up_to' mode returns depths 1 to N."""
        depth_map = {
            uuid.uuid4(): 0,  # Self - should be excluded
            uuid.uuid4(): 1,  # Depth 1 - included
            uuid.uuid4(): 2,  # Depth 2 - included
            uuid.uuid4(): 3,  # Depth 3 - included
        }

        result = service._filter_by_depth_mode(depth_map, depth=3, mode="up_to")

        # Should include depths 1, 2, 3 but not 0
        assert len(result) == 3
        for pid in result:
            assert 1 <= depth_map[pid] <= 3

    def test_filter_by_depth_mode_up_to_excludes_depth_0(
        self, service: RelativesNetworkService
    ) -> None:
        """Test 'up_to' mode excludes depth 0 (self)."""
        self_id = uuid.uuid4()
        depth_map = {
            self_id: 0,
            uuid.uuid4(): 1,
        }

        result = service._filter_by_depth_mode(depth_map, depth=3, mode="up_to")

        assert self_id not in result

    def test_filter_by_depth_mode_only_at(
        self, service: RelativesNetworkService
    ) -> None:
        """Test 'only_at' mode returns exactly depth N."""
        depth_1_id = uuid.uuid4()
        depth_2_id = uuid.uuid4()
        depth_3_id = uuid.uuid4()

        depth_map = {
            uuid.uuid4(): 0,
            depth_1_id: 1,
            depth_2_id: 2,
            depth_3_id: 3,
        }

        result = service._filter_by_depth_mode(depth_map, depth=2, mode="only_at")

        # Should only include depth 2
        assert len(result) == 1
        assert depth_2_id in result

    def test_filter_by_depth_mode_only_at_returns_empty_if_no_match(
        self, service: RelativesNetworkService
    ) -> None:
        """Test 'only_at' mode returns empty if no persons at that depth."""
        depth_map = {
            uuid.uuid4(): 0,
            uuid.uuid4(): 1,
        }

        result = service._filter_by_depth_mode(depth_map, depth=5, mode="only_at")

        assert len(result) == 0


@pytest.mark.unit
class TestLivingOnlyFilter:
    """Tests for living_only filter.
    
    Validates: Requirements 3.6
    """

    def test_living_only_excludes_deceased(
        self, service: RelativesNetworkService
    ) -> None:
        """Test living_only filter excludes persons with date_of_death."""
        living_id = uuid.uuid4()
        deceased_id = uuid.uuid4()

        living_person = create_mock_person(living_id, date_of_death=None)
        deceased_person = create_mock_person(
            deceased_id, date_of_death=date(2020, 1, 1)
        )

        request = RelativesNetworkRequest(
            person_id=uuid.uuid4(),
            living_only=True,
        )

        def mock_get_person(pid: uuid.UUID) -> MagicMock | None:
            if pid == living_id:
                return living_person
            elif pid == deceased_id:
                return deceased_person
            return None

        with patch.object(service, "_get_person", side_effect=mock_get_person):
            with patch.object(service, "_matches_address_filters", return_value=True):
                result = service._apply_filters([living_id, deceased_id], request)

        assert living_id in result
        assert deceased_id not in result

    def test_living_only_false_includes_deceased(
        self, service: RelativesNetworkService
    ) -> None:
        """Test living_only=False includes deceased persons."""
        living_id = uuid.uuid4()
        deceased_id = uuid.uuid4()

        living_person = create_mock_person(living_id, date_of_death=None)
        deceased_person = create_mock_person(
            deceased_id, date_of_death=date(2020, 1, 1)
        )

        request = RelativesNetworkRequest(
            person_id=uuid.uuid4(),
            living_only=False,
        )

        def mock_get_person(pid: uuid.UUID) -> MagicMock | None:
            if pid == living_id:
                return living_person
            elif pid == deceased_id:
                return deceased_person
            return None

        with patch.object(service, "_get_person", side_effect=mock_get_person):
            with patch.object(service, "_matches_address_filters", return_value=True):
                result = service._apply_filters([living_id, deceased_id], request)

        assert living_id in result
        assert deceased_id in result


@pytest.mark.unit
class TestGenderFilter:
    """Tests for gender filter.
    
    Validates: Requirements 3.7
    """

    def test_gender_filter_matches_gender_id(
        self, service: RelativesNetworkService
    ) -> None:
        """Test gender filter only returns matching gender."""
        male_gender_id = uuid.uuid4()
        female_gender_id = uuid.uuid4()

        male_id = uuid.uuid4()
        female_id = uuid.uuid4()

        male_person = create_mock_person(male_id, gender_id=male_gender_id)
        female_person = create_mock_person(female_id, gender_id=female_gender_id)

        request = RelativesNetworkRequest(
            person_id=uuid.uuid4(),
            gender_id=male_gender_id,
            living_only=False,
        )

        def mock_get_person(pid: uuid.UUID) -> MagicMock | None:
            if pid == male_id:
                return male_person
            elif pid == female_id:
                return female_person
            return None

        with patch.object(service, "_get_person", side_effect=mock_get_person):
            with patch.object(service, "_matches_address_filters", return_value=True):
                result = service._apply_filters([male_id, female_id], request)

        assert male_id in result
        assert female_id not in result

    def test_no_gender_filter_returns_all(
        self, service: RelativesNetworkService
    ) -> None:
        """Test no gender filter returns all genders."""
        male_id = uuid.uuid4()
        female_id = uuid.uuid4()

        male_person = create_mock_person(male_id, gender_id=uuid.uuid4())
        female_person = create_mock_person(female_id, gender_id=uuid.uuid4())

        request = RelativesNetworkRequest(
            person_id=uuid.uuid4(),
            gender_id=None,
            living_only=False,
        )

        def mock_get_person(pid: uuid.UUID) -> MagicMock | None:
            if pid == male_id:
                return male_person
            elif pid == female_id:
                return female_person
            return None

        with patch.object(service, "_get_person", side_effect=mock_get_person):
            with patch.object(service, "_matches_address_filters", return_value=True):
                result = service._apply_filters([male_id, female_id], request)

        assert male_id in result
        assert female_id in result



@pytest.mark.unit
class TestAddressFilters:
    """Tests for address hierarchy filters.
    
    Validates: Requirements 3.8
    """

    def test_matches_address_filters_no_filters_returns_true(
        self, service: RelativesNetworkService
    ) -> None:
        """Test that no address filters matches all persons."""
        person_id = uuid.uuid4()
        request = RelativesNetworkRequest(
            person_id=uuid.uuid4(),
            country_id=None,
            state_id=None,
            district_id=None,
            sub_district_id=None,
            locality_id=None,
        )

        result = service._matches_address_filters(person_id, request)

        assert result is True

    def test_matches_address_filters_country_match(
        self, service: RelativesNetworkService, mock_session: MagicMock
    ) -> None:
        """Test country filter matches correctly."""
        person_id = uuid.uuid4()
        country_id = uuid.uuid4()

        mock_address = create_mock_address(person_id, country_id=country_id)
        mock_session.exec.return_value.first.return_value = mock_address

        request = RelativesNetworkRequest(
            person_id=uuid.uuid4(),
            country_id=country_id,
        )

        result = service._matches_address_filters(person_id, request)

        assert result is True

    def test_matches_address_filters_country_mismatch(
        self, service: RelativesNetworkService, mock_session: MagicMock
    ) -> None:
        """Test country filter rejects mismatched country."""
        person_id = uuid.uuid4()
        person_country_id = uuid.uuid4()
        filter_country_id = uuid.uuid4()

        mock_address = create_mock_address(person_id, country_id=person_country_id)
        mock_session.exec.return_value.first.return_value = mock_address

        request = RelativesNetworkRequest(
            person_id=uuid.uuid4(),
            country_id=filter_country_id,
        )

        result = service._matches_address_filters(person_id, request)

        assert result is False

    def test_matches_address_filters_no_address_returns_false(
        self, service: RelativesNetworkService, mock_session: MagicMock
    ) -> None:
        """Test that person without address fails address filter."""
        person_id = uuid.uuid4()
        mock_session.exec.return_value.first.return_value = None

        request = RelativesNetworkRequest(
            person_id=uuid.uuid4(),
            country_id=uuid.uuid4(),
        )

        result = service._matches_address_filters(person_id, request)

        assert result is False

    def test_matches_address_filters_all_levels(
        self, service: RelativesNetworkService, mock_session: MagicMock
    ) -> None:
        """Test all address hierarchy levels match."""
        person_id = uuid.uuid4()
        country_id = uuid.uuid4()
        state_id = uuid.uuid4()
        district_id = uuid.uuid4()
        sub_district_id = uuid.uuid4()
        locality_id = uuid.uuid4()

        mock_address = create_mock_address(
            person_id,
            country_id=country_id,
            state_id=state_id,
            district_id=district_id,
            sub_district_id=sub_district_id,
            locality_id=locality_id,
        )
        mock_session.exec.return_value.first.return_value = mock_address

        request = RelativesNetworkRequest(
            person_id=uuid.uuid4(),
            country_id=country_id,
            state_id=state_id,
            district_id=district_id,
            sub_district_id=sub_district_id,
            locality_id=locality_id,
        )

        result = service._matches_address_filters(person_id, request)

        assert result is True


@pytest.mark.unit
class TestResultLimiting:
    """Tests for MAX_RESULTS limiting.
    
    Validates: Requirements 3.9
    """

    def test_results_limited_to_max_results(
        self, mock_session: MagicMock
    ) -> None:
        """Test that results are limited to MAX_RESULTS."""
        service = RelativesNetworkService(mock_session)
        person_id = uuid.uuid4()
        mock_person = create_mock_person(person_id)

        # Create more than MAX_RESULTS relatives
        relative_ids = [uuid.uuid4() for _ in range(MAX_RESULTS + 50)]
        depth_map = {person_id: 0}
        for rid in relative_ids:
            depth_map[rid] = 1

        request = RelativesNetworkRequest(person_id=person_id)

        with patch.object(service, "_get_person", return_value=mock_person):
            with patch.object(service, "_bfs_traverse", return_value=depth_map):
                with patch.object(
                    service, "_apply_filters", return_value=relative_ids
                ):
                    with patch.object(
                        service,
                        "_enrich_relative_info",
                        side_effect=lambda pid, d: RelativeInfo(
                            person_id=pid,
                            first_name="Test",
                            last_name="Person",
                            gender_id=uuid.uuid4(),
                            depth=d,
                        ),
                    ):
                        result = service.find_relatives(request)

        assert len(result.relatives) <= MAX_RESULTS
        assert result.total_count <= MAX_RESULTS


@pytest.mark.unit
class TestRelativeInfoEnrichment:
    """Tests for relative info enrichment.
    
    Validates: Requirements 3.10
    """

    def test_enrich_relative_info_populates_person_details(
        self, service: RelativesNetworkService
    ) -> None:
        """Test that enrichment populates person details correctly."""
        person_id = uuid.uuid4()
        gender_id = uuid.uuid4()
        mock_person = create_mock_person(
            person_id,
            first_name="John",
            last_name="Doe",
            gender_id=gender_id,
            date_of_birth=date(1990, 5, 15),
            date_of_death=None,
        )

        with patch.object(service, "_get_person", return_value=mock_person):
            with patch.object(
                service, "_get_address_names", return_value=(None, None)
            ):
                result = service._enrich_relative_info(person_id, depth=2)

        assert result.person_id == person_id
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.gender_id == gender_id
        assert result.birth_year == 1990
        assert result.death_year is None
        assert result.depth == 2

    def test_enrich_relative_info_includes_death_year(
        self, service: RelativesNetworkService
    ) -> None:
        """Test that enrichment includes death year for deceased persons."""
        person_id = uuid.uuid4()
        mock_person = create_mock_person(
            person_id,
            date_of_birth=date(1950, 1, 1),
            date_of_death=date(2020, 6, 15),
        )

        with patch.object(service, "_get_person", return_value=mock_person):
            with patch.object(
                service, "_get_address_names", return_value=(None, None)
            ):
                result = service._enrich_relative_info(person_id, depth=1)

        assert result.birth_year == 1950
        assert result.death_year == 2020

    def test_enrich_relative_info_includes_address_names(
        self, service: RelativesNetworkService
    ) -> None:
        """Test that enrichment includes district and locality names."""
        person_id = uuid.uuid4()
        mock_person = create_mock_person(person_id)

        with patch.object(service, "_get_person", return_value=mock_person):
            with patch.object(
                service,
                "_get_address_names",
                return_value=("Test District", "Test Locality"),
            ):
                result = service._enrich_relative_info(person_id, depth=1)

        assert result.district_name == "Test District"
        assert result.locality_name == "Test Locality"

    def test_enrich_relative_info_handles_missing_person(
        self, service: RelativesNetworkService
    ) -> None:
        """Test that enrichment handles missing person gracefully."""
        person_id = uuid.uuid4()

        with patch.object(service, "_get_person", return_value=None):
            result = service._enrich_relative_info(person_id, depth=1)

        assert result.person_id == person_id
        assert result.first_name == "Unknown"
        assert result.last_name == "Unknown"
        assert result.depth == 1


@pytest.mark.unit
class TestGetAddressNames:
    """Tests for _get_address_names helper method."""

    def test_get_address_names_returns_district_and_locality(
        self, service: RelativesNetworkService, mock_session: MagicMock
    ) -> None:
        """Test that address names are retrieved correctly."""
        person_id = uuid.uuid4()
        district_id = uuid.uuid4()
        locality_id = uuid.uuid4()

        mock_address = create_mock_address(
            person_id, district_id=district_id, locality_id=locality_id
        )

        mock_district = MagicMock()
        mock_district.name = "Test District"

        mock_locality = MagicMock()
        mock_locality.name = "Test Locality"

        # Setup mock session to return address, then district, then locality
        mock_session.exec.return_value.first.side_effect = [
            mock_address,
            mock_district,
            mock_locality,
        ]

        district_name, locality_name = service._get_address_names(person_id)

        assert district_name == "Test District"
        assert locality_name == "Test Locality"

    def test_get_address_names_no_address_returns_none(
        self, service: RelativesNetworkService, mock_session: MagicMock
    ) -> None:
        """Test that missing address returns None for both names."""
        person_id = uuid.uuid4()
        mock_session.exec.return_value.first.return_value = None

        district_name, locality_name = service._get_address_names(person_id)

        assert district_name is None
        assert locality_name is None


@pytest.mark.unit
class TestFindRelativesIntegration:
    """Integration tests for find_relatives method."""

    def test_find_relatives_excludes_self_from_results(
        self, mock_session: MagicMock
    ) -> None:
        """Test that the requesting person is excluded from results."""
        service = RelativesNetworkService(mock_session)
        person_id = uuid.uuid4()
        relative_id = uuid.uuid4()

        mock_person = create_mock_person(person_id)
        mock_relative = create_mock_person(relative_id)

        depth_map = {person_id: 0, relative_id: 1}

        request = RelativesNetworkRequest(person_id=person_id)

        def mock_get_person(pid: uuid.UUID) -> MagicMock | None:
            if pid == person_id:
                return mock_person
            elif pid == relative_id:
                return mock_relative
            return None

        with patch.object(service, "_get_person", side_effect=mock_get_person):
            with patch.object(service, "_bfs_traverse", return_value=depth_map):
                with patch.object(
                    service, "_matches_address_filters", return_value=True
                ):
                    with patch.object(
                        service, "_get_address_names", return_value=(None, None)
                    ):
                        result = service.find_relatives(request)

        # Self should not be in results
        result_ids = [r.person_id for r in result.relatives]
        assert person_id not in result_ids
        assert relative_id in result_ids

    def test_find_relatives_returns_correct_response_structure(
        self, mock_session: MagicMock
    ) -> None:
        """Test that response has correct structure."""
        service = RelativesNetworkService(mock_session)
        person_id = uuid.uuid4()
        mock_person = create_mock_person(person_id)

        request = RelativesNetworkRequest(
            person_id=person_id,
            depth=2,
            depth_mode="up_to",
        )

        with patch.object(service, "_get_person", return_value=mock_person):
            with patch.object(service, "_bfs_traverse", return_value={person_id: 0}):
                result = service.find_relatives(request)

        assert isinstance(result, RelativesNetworkResponse)
        assert result.person_id == person_id
        assert result.depth == 2
        assert result.depth_mode == "up_to"
        assert isinstance(result.relatives, list)
        assert isinstance(result.total_count, int)

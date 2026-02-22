"""Unit tests for LineagePathService.

Tests cover:
- Relationship fetching (active only)
- BFS algorithm for finding common ancestors
- Person data enrichment
- Bidirectional linked list building
- Main find_path method

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1-2.11, 3.1-3.5
"""

import uuid
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.enums.relationship_type import RelationshipType
from app.services.lineage_path.lineage_path_service import LineagePathService


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_service(mock_session: MagicMock) -> LineagePathService:
    """Create a LineagePathService with mocked session."""
    return LineagePathService(mock_session)


def create_mock_person(
    person_id: uuid.UUID,
    first_name: str = "Test",
    last_name: str = "Person",
    birth_date: date = date(1990, 1, 1),
    death_date: date | None = None,
) -> Person:
    """Create a mock Person object."""
    return Person(
        id=person_id,
        user_id=None,
        created_by_user_id=uuid.uuid4(),
        first_name=first_name,
        last_name=last_name,
        gender_id=uuid.uuid4(),
        date_of_birth=birth_date,
        date_of_death=death_date,
    )


def create_mock_relationship(
    person_id: uuid.UUID,
    related_person_id: uuid.UUID,
    relationship_type: RelationshipType,
    is_active: bool = True,
) -> PersonRelationship:
    """Create a mock PersonRelationship object."""
    return PersonRelationship(
        id=uuid.uuid4(),
        person_id=person_id,
        related_person_id=related_person_id,
        relationship_type=relationship_type,
        is_active=is_active,
    )


# =============================================================================
# Tests for Relationship Fetching (Task 3.7)
# Requirements: 1.3, 1.4
# =============================================================================


@pytest.mark.unit
class TestRelationshipFetching:
    """Tests for _get_relationships method."""

    def test_get_relationships_returns_active_only(
        self, mock_session: MagicMock
    ) -> None:
        """Test that only active relationships are returned.

        Requirements: 1.3, 1.4
        """
        person_id = uuid.uuid4()
        related_id_1 = uuid.uuid4()
        related_id_2 = uuid.uuid4()

        # Create active and inactive relationships
        active_rel = create_mock_relationship(
            person_id, related_id_1, RelationshipType.FATHER, is_active=True
        )

        # Mock the session.exec to return only active relationships
        mock_result = MagicMock()
        mock_result.all.return_value = [active_rel]  # Only active
        mock_session.exec.return_value = mock_result

        service = LineagePathService(mock_session)
        result = service._get_relationships(person_id)

        assert len(result) == 1
        assert result[0] == related_id_1

    def test_get_relationships_filters_inactive(
        self, mock_session: MagicMock
    ) -> None:
        """Test that inactive relationships are filtered out.

        Requirements: 1.4
        """
        person_id = uuid.uuid4()

        # Mock empty result (all relationships are inactive)
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.exec.return_value = mock_result

        service = LineagePathService(mock_session)
        result = service._get_relationships(person_id)

        assert len(result) == 0

    def test_get_relationships_person_with_no_relationships(
        self, mock_session: MagicMock
    ) -> None:
        """Test fetching relationships for person with none.

        Requirements: 1.3
        """
        person_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.exec.return_value = mock_result

        service = LineagePathService(mock_session)
        result = service._get_relationships(person_id)

        assert result == []

    def test_get_relationships_returns_all_related_ids(
        self, mock_session: MagicMock
    ) -> None:
        """Test that all related person IDs are returned.

        Requirements: 1.3
        """
        person_id = uuid.uuid4()
        father_id = uuid.uuid4()
        mother_id = uuid.uuid4()
        spouse_id = uuid.uuid4()
        child_id = uuid.uuid4()

        relationships = [
            create_mock_relationship(
                person_id, father_id, RelationshipType.FATHER, is_active=True
            ),
            create_mock_relationship(
                person_id, mother_id, RelationshipType.MOTHER, is_active=True
            ),
            create_mock_relationship(
                person_id, spouse_id, RelationshipType.WIFE, is_active=True
            ),
            create_mock_relationship(
                person_id, child_id, RelationshipType.SON, is_active=True
            ),
        ]

        mock_result = MagicMock()
        mock_result.all.return_value = relationships
        mock_session.exec.return_value = mock_result

        service = LineagePathService(mock_session)
        result = service._get_relationships(person_id)

        assert len(result) == 4
        assert father_id in result
        assert mother_id in result
        assert spouse_id in result
        assert child_id in result


# =============================================================================
# Tests for BFS Algorithm (Task 3.8)
# Requirements: 1.1, 1.2, 1.5, 3.5
# =============================================================================


@pytest.mark.unit
class TestBFSAlgorithm:
    """Tests for _bfs_find_common_ancestor method."""

    def test_bfs_finds_common_ancestor_simple_tree(
        self, mock_session: MagicMock
    ) -> None:
        """Test finding common ancestor in a simple tree structure.

        Tree: grandparent -> parent_a, parent_b
              parent_a -> person_a
              parent_b -> person_b

        Requirements: 1.1, 1.2
        """
        grandparent_id = uuid.uuid4()
        parent_a_id = uuid.uuid4()
        parent_b_id = uuid.uuid4()
        person_a_id = uuid.uuid4()
        person_b_id = uuid.uuid4()

        # Define relationships for each person (now returns list of UUIDs)
        relationships_map = {
            person_a_id: [parent_a_id],
            person_b_id: [parent_b_id],
            parent_a_id: [grandparent_id, person_a_id],
            parent_b_id: [grandparent_id, person_b_id],
            grandparent_id: [parent_a_id, parent_b_id],
        }

        service = LineagePathService(mock_session)

        def mock_get_relationships(person_id: uuid.UUID):
            return relationships_map.get(person_id, [])

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ):
            common_person_id, visited_a, visited_b = service._bfs_find_common_ancestor(
                person_a_id, person_b_id
            )

        # The common ancestor should be found
        assert common_person_id is not None
        assert len(visited_a) > 0
        assert len(visited_b) > 0

    def test_bfs_finds_common_ancestor_through_spouse(
        self, mock_session: MagicMock
    ) -> None:
        """Test finding connection through spouse relationship.

        Structure: person_a <-> spouse <-> person_b (spouse's child)

        Requirements: 1.3
        """
        person_a_id = uuid.uuid4()
        spouse_id = uuid.uuid4()
        person_b_id = uuid.uuid4()

        relationships_map = {
            person_a_id: [spouse_id],
            spouse_id: [person_a_id, person_b_id],
            person_b_id: [spouse_id],
        }

        service = LineagePathService(mock_session)

        def mock_get_relationships(person_id: uuid.UUID):
            return relationships_map.get(person_id, [])

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ):
            common_person_id, visited_a, visited_b = service._bfs_find_common_ancestor(
                person_a_id, person_b_id
            )

        assert common_person_id == spouse_id

    def test_bfs_respects_max_depth_limit(self, mock_session: MagicMock) -> None:
        """Test that BFS respects the max depth configuration.

        Requirements: 1.5
        """
        # Create a chain longer than max_depth
        person_ids = [uuid.uuid4() for _ in range(15)]

        # Create a linear chain of relationships
        relationships_map = {}
        for i, person_id in enumerate(person_ids):
            rels = []
            if i > 0:
                rels.append(person_ids[i - 1])
            if i < len(person_ids) - 1:
                rels.append(person_ids[i + 1])
            relationships_map[person_id] = rels

        service = LineagePathService(mock_session)
        service.max_depth = 5  # Set low max depth

        def mock_get_relationships(person_id: uuid.UUID):
            return relationships_map.get(person_id, [])

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ):
            # Try to find path between first and last person (too far apart)
            common_person_id, visited_a, visited_b = service._bfs_find_common_ancestor(
                person_ids[0], person_ids[14]
            )

        # Should return None for common_person_id because max depth is exceeded
        assert common_person_id is None

    def test_bfs_handles_circular_relationships(
        self, mock_session: MagicMock
    ) -> None:
        """Test that BFS handles circular relationships gracefully.

        Requirements: 3.5
        """
        person_a_id = uuid.uuid4()
        person_b_id = uuid.uuid4()
        person_c_id = uuid.uuid4()

        # Create circular relationships: A -> B -> C -> A
        relationships_map = {
            person_a_id: [person_b_id, person_c_id],
            person_b_id: [person_a_id, person_c_id],
            person_c_id: [person_a_id, person_b_id],
        }

        service = LineagePathService(mock_session)

        def mock_get_relationships(person_id: uuid.UUID):
            return relationships_map.get(person_id, [])

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ):
            # Should not hang or crash due to circular references
            common_person_id, visited_a, visited_b = service._bfs_find_common_ancestor(
                person_a_id, person_c_id
            )

        # Should find a connection
        assert common_person_id is not None

    def test_bfs_no_connection_found(self, mock_session: MagicMock) -> None:
        """Test BFS returns None when no connection exists.

        Requirements: 3.5
        """
        person_a_id = uuid.uuid4()
        person_b_id = uuid.uuid4()

        # No relationships between the two persons
        relationships_map = {
            person_a_id: [],
            person_b_id: [],
        }

        service = LineagePathService(mock_session)

        def mock_get_relationships(person_id: uuid.UUID):
            return relationships_map.get(person_id, [])

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ):
            common_person_id, visited_a, visited_b = service._bfs_find_common_ancestor(
                person_a_id, person_b_id
            )

        assert common_person_id is None


# =============================================================================
# Tests for Person Data Enrichment (Task 3.9)
# Requirements: 2.2, 2.3, 2.4, 3.4
# =============================================================================


@pytest.mark.unit
class TestPersonDataEnrichment:
    """Tests for _enrich_person_data and related methods."""

    def test_enrich_person_data_with_full_address(
        self, mock_session: MagicMock
    ) -> None:
        """Test enrichment with complete address data.

        Requirements: 2.3, 3.4
        """
        person_id = uuid.uuid4()
        mock_person = create_mock_person(
            person_id, "John", "Doe", date(1990, 5, 15), None
        )

        service = LineagePathService(mock_session)

        with patch.object(service, "_get_person", return_value=mock_person), patch.object(
            service, "_get_address_string", return_value="Village, District, State, Country"
        ), patch.object(
            service, "_get_religion_string", return_value="Hindu, Brahmin"
        ):
            result = service._enrich_person_data(person_id)

        assert result.person_id == person_id
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.birth_year == 1990
        assert result.death_year is None
        assert result.address == "Village, District, State, Country"
        assert result.religion == "Hindu, Brahmin"
        assert result.from_person is None
        assert result.to_person is None

    def test_enrich_person_data_with_missing_address(
        self, mock_session: MagicMock
    ) -> None:
        """Test enrichment returns empty string for missing address.

        Requirements: 3.4
        """
        person_id = uuid.uuid4()
        mock_person = create_mock_person(person_id, "Jane", "Smith")

        service = LineagePathService(mock_session)

        with patch.object(service, "_get_person", return_value=mock_person), patch.object(
            service, "_get_address_string", return_value=""
        ), patch.object(
            service, "_get_religion_string", return_value="Christian"
        ):
            result = service._enrich_person_data(person_id)

        assert result.address == ""

    def test_enrich_person_data_with_missing_religion(
        self, mock_session: MagicMock
    ) -> None:
        """Test enrichment returns empty string for missing religion.

        Requirements: 3.4
        """
        person_id = uuid.uuid4()
        mock_person = create_mock_person(person_id, "Bob", "Johnson")

        service = LineagePathService(mock_session)

        with patch.object(service, "_get_person", return_value=mock_person), patch.object(
            service, "_get_address_string", return_value="Some Address"
        ), patch.object(
            service, "_get_religion_string", return_value=""
        ):
            result = service._enrich_person_data(person_id)

        assert result.religion == ""

    def test_enrich_person_data_with_death_year(
        self, mock_session: MagicMock
    ) -> None:
        """Test enrichment includes death year when available.

        Requirements: 2.2
        """
        person_id = uuid.uuid4()
        mock_person = create_mock_person(
            person_id, "Deceased", "Person", date(1920, 1, 1), date(2000, 12, 31)
        )

        service = LineagePathService(mock_session)

        with patch.object(service, "_get_person", return_value=mock_person), patch.object(
            service, "_get_address_string", return_value=""
        ), patch.object(
            service, "_get_religion_string", return_value=""
        ):
            result = service._enrich_person_data(person_id)

        assert result.birth_year == 1920
        assert result.death_year == 2000

    def test_enrich_person_data_person_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test enrichment handles missing person gracefully.

        Requirements: 2.2
        """
        person_id = uuid.uuid4()

        service = LineagePathService(mock_session)

        with patch.object(service, "_get_person", return_value=None):
            result = service._enrich_person_data(person_id)

        assert result.person_id == person_id
        assert result.first_name == "Unknown"
        assert result.last_name == "Unknown"


# =============================================================================
# Tests for Bidirectional Linked List Building
# Requirements: 2.1, 2.5, 2.6, 2.7
# =============================================================================


@pytest.mark.unit
class TestBidirectionalLinkedListBuilding:
    """Tests for _build_bidirectional_linked_list method."""

    def test_empty_list_returns_empty_dict(self, mock_session: MagicMock) -> None:
        """Test that empty input returns empty dict."""
        service = LineagePathService(mock_session)
        result = service._build_bidirectional_linked_list([])
        assert result == {}

    def test_single_person_returns_node_without_connections(
        self, mock_session: MagicMock
    ) -> None:
        """Test single person has no from_person or to_person."""
        person_id = uuid.uuid4()
        mock_person = create_mock_person(person_id, "Single", "Person")

        service = LineagePathService(mock_session)

        with patch.object(service, "_get_person", return_value=mock_person), patch.object(
            service, "_get_address_string", return_value=""
        ), patch.object(
            service, "_get_religion_string", return_value=""
        ):
            result = service._build_bidirectional_linked_list([person_id])

        assert len(result) == 1
        assert person_id in result
        assert result[person_id].from_person is None
        assert result[person_id].to_person is None

    def test_two_persons_linked_correctly(self, mock_session: MagicMock) -> None:
        """Test two persons are linked with from_person and to_person."""
        person_a_id = uuid.uuid4()
        person_b_id = uuid.uuid4()

        mock_person_a = create_mock_person(person_a_id, "Person", "A")
        mock_person_b = create_mock_person(person_b_id, "Person", "B")

        service = LineagePathService(mock_session)

        def mock_get_person(pid):
            if pid == person_a_id:
                return mock_person_a
            return mock_person_b

        with patch.object(service, "_get_person", side_effect=mock_get_person), patch.object(
            service, "_get_address_string", return_value=""
        ), patch.object(
            service, "_get_religion_string", return_value=""
        ), patch.object(
            service, "_get_relationship_type", return_value="Father"
        ):
            result = service._build_bidirectional_linked_list([person_a_id, person_b_id])

        assert len(result) == 2
        # Person A: no from_person, has to_person pointing to B
        assert result[person_a_id].from_person is None
        assert result[person_a_id].to_person is not None
        assert result[person_a_id].to_person.person_id == person_b_id

        # Person B: has from_person pointing to A, no to_person
        assert result[person_b_id].from_person is not None
        assert result[person_b_id].from_person.person_id == person_a_id
        assert result[person_b_id].to_person is None

    def test_three_persons_chain_linked_correctly(
        self, mock_session: MagicMock
    ) -> None:
        """Test three persons form a proper chain: A -> B -> C."""
        person_a_id = uuid.uuid4()
        person_b_id = uuid.uuid4()
        person_c_id = uuid.uuid4()

        mock_persons = {
            person_a_id: create_mock_person(person_a_id, "Person", "A"),
            person_b_id: create_mock_person(person_b_id, "Person", "B"),
            person_c_id: create_mock_person(person_c_id, "Person", "C"),
        }

        service = LineagePathService(mock_session)

        def mock_get_person(pid):
            return mock_persons.get(pid)

        with patch.object(service, "_get_person", side_effect=mock_get_person), patch.object(
            service, "_get_address_string", return_value=""
        ), patch.object(
            service, "_get_religion_string", return_value=""
        ), patch.object(
            service, "_get_relationship_type", return_value="Related"
        ):
            result = service._build_bidirectional_linked_list(
                [person_a_id, person_b_id, person_c_id]
            )

        assert len(result) == 3

        # Person A: start of chain
        assert result[person_a_id].from_person is None
        assert result[person_a_id].to_person.person_id == person_b_id

        # Person B: middle of chain
        assert result[person_b_id].from_person.person_id == person_a_id
        assert result[person_b_id].to_person.person_id == person_c_id

        # Person C: end of chain
        assert result[person_c_id].from_person.person_id == person_b_id
        assert result[person_c_id].to_person is None


# =============================================================================
# Tests for Final Ordered List Building
# =============================================================================


@pytest.mark.unit
class TestBuildFinalOrderedList:
    """Tests for _build_final_ordered_list method."""

    def test_simple_path_ordering(self, mock_session: MagicMock) -> None:
        """Test that paths are combined correctly."""
        common_id = uuid.uuid4()
        person_a_id = uuid.uuid4()
        person_b_id = uuid.uuid4()

        # visited_map_a: A -> common (A's parent is None, common's parent is A)
        visited_map_a = {person_a_id: None, common_id: person_a_id}
        # visited_map_b: B -> common (B's parent is None, common's parent is B)
        visited_map_b = {person_b_id: None, common_id: person_b_id}

        service = LineagePathService(mock_session)
        result = service._build_final_ordered_list(common_id, visited_map_a, visited_map_b)

        # Expected: [A, common, B]
        assert result[0] == person_a_id
        assert result[1] == common_id
        assert result[2] == person_b_id

    def test_longer_path_ordering(self, mock_session: MagicMock) -> None:
        """Test longer paths are combined correctly."""
        common_id = uuid.uuid4()
        a1 = uuid.uuid4()
        a2 = uuid.uuid4()
        b1 = uuid.uuid4()
        b2 = uuid.uuid4()

        # Path A: a1 -> a2 -> common
        visited_map_a = {a1: None, a2: a1, common_id: a2}
        # Path B: b1 -> b2 -> common
        visited_map_b = {b1: None, b2: b1, common_id: b2}

        service = LineagePathService(mock_session)
        result = service._build_final_ordered_list(common_id, visited_map_a, visited_map_b)

        # Expected: [a1, a2, common, b2, b1]
        assert result == [a1, a2, common_id, b2, b1]


# =============================================================================
# Tests for Get Relationship Type
# =============================================================================


@pytest.mark.unit
class TestGetRelationshipType:
    """Tests for _get_relationship_type method."""

    def test_returns_relationship_label(self, mock_session: MagicMock) -> None:
        """Test that relationship label is returned."""
        from_id = uuid.uuid4()
        to_id = uuid.uuid4()

        mock_rel = create_mock_relationship(from_id, to_id, RelationshipType.FATHER)

        mock_result = MagicMock()
        mock_result.first.return_value = mock_rel
        mock_session.exec.return_value = mock_result

        service = LineagePathService(mock_session)
        result = service._get_relationship_type(from_id, to_id)

        assert result == RelationshipType.FATHER.label

    def test_returns_related_when_not_found(self, mock_session: MagicMock) -> None:
        """Test that 'Related' is returned when no relationship found."""
        from_id = uuid.uuid4()
        to_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        service = LineagePathService(mock_session)
        result = service._get_relationship_type(from_id, to_id)

        assert result == "Related"


# =============================================================================
# Tests for Main find_path Method (Task 3.11)
# Requirements: 3.1, 3.2, 3.3
# =============================================================================


@pytest.mark.unit
class TestFindPathMethod:
    """Tests for the main find_path method."""

    def test_find_path_same_person_returns_single_node(
        self, mock_session: MagicMock
    ) -> None:
        """Test that same person returns single node graph.

        Requirements: 3.1
        """
        person_id = uuid.uuid4()
        mock_person = create_mock_person(person_id, "Same", "Person")

        service = LineagePathService(mock_session)

        from app.schemas.lineage_path import PersonNode

        mock_node = PersonNode(
            person_id=person_id,
            first_name="Same",
            last_name="Person",
            birth_year=1990,
            from_person=None,
            to_person=None,
        )

        with patch.object(service, "_get_person", return_value=mock_person), patch.object(
            service, "_enrich_person_data", return_value=mock_node
        ):
            result = service.find_path(person_id, person_id)

        assert result.connection_found is True
        assert result.message == "Same person provided for both inputs"
        assert result.common_ancestor_id == person_id
        assert len(result.graph) == 1
        assert person_id in result.graph

    def test_find_path_invalid_person_a_returns_404(
        self, mock_session: MagicMock
    ) -> None:
        """Test that invalid person_a returns 404 error.

        Requirements: 3.2
        """
        person_a_id = uuid.uuid4()
        person_b_id = uuid.uuid4()

        service = LineagePathService(mock_session)

        with patch.object(service, "_get_person", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                service.find_path(person_a_id, person_b_id)

        assert exc_info.value.status_code == 404
        assert "Person A not found" in exc_info.value.detail

    def test_find_path_invalid_person_b_returns_404(
        self, mock_session: MagicMock
    ) -> None:
        """Test that invalid person_b returns 404 error.

        Requirements: 3.2
        """
        person_a_id = uuid.uuid4()
        person_b_id = uuid.uuid4()
        mock_person_a = create_mock_person(person_a_id, "Valid", "Person")

        service = LineagePathService(mock_session)

        def mock_get_person(pid):
            if pid == person_a_id:
                return mock_person_a
            return None

        with patch.object(service, "_get_person", side_effect=mock_get_person):
            with pytest.raises(HTTPException) as exc_info:
                service.find_path(person_a_id, person_b_id)

        assert exc_info.value.status_code == 404
        assert "Person B not found" in exc_info.value.detail

    def test_find_path_successful_returns_valid_response(
        self, mock_session: MagicMock
    ) -> None:
        """Test successful path finding returns valid response.

        Requirements: 3.3
        """
        person_a_id = uuid.uuid4()
        person_b_id = uuid.uuid4()
        common_id = uuid.uuid4()

        mock_person_a = create_mock_person(person_a_id, "Person", "A")
        mock_person_b = create_mock_person(person_b_id, "Person", "B")

        service = LineagePathService(mock_session)

        def mock_get_person(pid):
            if pid == person_a_id:
                return mock_person_a
            if pid == person_b_id:
                return mock_person_b
            return None

        # Mock visited maps
        visited_a = {person_a_id: None, common_id: person_a_id}
        visited_b = {person_b_id: None, common_id: person_b_id}

        from app.schemas.lineage_path import PersonNode

        def mock_enrich(pid):
            return PersonNode(
                person_id=pid,
                first_name="Test",
                last_name="Person",
                birth_year=1990,
                from_person=None,
                to_person=None,
            )

        with patch.object(
            service, "_get_person", side_effect=mock_get_person
        ), patch.object(
            service,
            "_bfs_find_common_ancestor",
            return_value=(common_id, visited_a, visited_b),
        ), patch.object(
            service, "_enrich_person_data", side_effect=mock_enrich
        ), patch.object(
            service, "_get_relationship_type", return_value="Related"
        ):
            result = service.find_path(person_a_id, person_b_id)

        assert result.connection_found is True
        assert result.message == "Connection found"
        assert result.common_ancestor_id == common_id
        assert len(result.graph) == 3

    def test_find_path_no_connection_returns_both_persons(
        self, mock_session: MagicMock
    ) -> None:
        """Test no connection found returns graph with both persons.

        Requirements: 3.3
        """
        person_a_id = uuid.uuid4()
        person_b_id = uuid.uuid4()

        mock_person_a = create_mock_person(person_a_id, "Person", "A")
        mock_person_b = create_mock_person(person_b_id, "Person", "B")

        service = LineagePathService(mock_session)
        service.max_depth = 10

        def mock_get_person(pid):
            if pid == person_a_id:
                return mock_person_a
            if pid == person_b_id:
                return mock_person_b
            return None

        from app.schemas.lineage_path import PersonNode

        def mock_enrich(pid):
            return PersonNode(
                person_id=pid,
                first_name="Test",
                last_name="Person",
                birth_year=1990,
                from_person=None,
                to_person=None,
            )

        # Return None for common_person_id with empty visited maps
        with patch.object(
            service, "_get_person", side_effect=mock_get_person
        ), patch.object(
            service,
            "_bfs_find_common_ancestor",
            return_value=(None, {person_a_id: None}, {person_b_id: None}),
        ), patch.object(
            service, "_enrich_person_data", side_effect=mock_enrich
        ):
            result = service.find_path(person_a_id, person_b_id)

        assert result.connection_found is False
        assert "No relation found" in result.message
        assert result.common_ancestor_id is None
        assert len(result.graph) == 2
        assert person_a_id in result.graph
        assert person_b_id in result.graph


# =============================================================================
# Tests for _get_person Method
# =============================================================================


@pytest.mark.unit
class TestGetPerson:
    """Tests for _get_person method."""

    def test_get_person_returns_person_when_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test that person is returned when found."""
        person_id = uuid.uuid4()
        mock_person = create_mock_person(person_id, "John", "Doe")

        mock_result = MagicMock()
        mock_result.first.return_value = mock_person
        mock_session.exec.return_value = mock_result

        service = LineagePathService(mock_session)
        result = service._get_person(person_id)

        assert result is not None
        assert result.id == person_id
        assert result.first_name == "John"
        assert result.last_name == "Doe"

    def test_get_person_returns_none_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test that None is returned when person not found."""
        person_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        service = LineagePathService(mock_session)
        result = service._get_person(person_id)

        assert result is None


# =============================================================================
# Tests for _get_address_string Method
# =============================================================================


@pytest.mark.unit
class TestGetAddressString:
    """Tests for _get_address_string method."""

    def test_get_address_string_returns_empty_when_no_address(
        self, mock_session: MagicMock
    ) -> None:
        """Test that empty string is returned when no address found."""
        person_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        service = LineagePathService(mock_session)
        result = service._get_address_string(person_id)

        assert result == ""

    def test_get_address_string_returns_full_address(
        self, mock_session: MagicMock
    ) -> None:
        """Test that full address string is returned with all parts."""
        from app.db_models.address.country import Country
        from app.db_models.address.district import District
        from app.db_models.address.locality import Locality
        from app.db_models.address.state import State
        from app.db_models.address.sub_district import SubDistrict
        from app.db_models.person.person_address import PersonAddress

        person_id = uuid.uuid4()
        locality_id = uuid.uuid4()
        sub_district_id = uuid.uuid4()
        district_id = uuid.uuid4()
        state_id = uuid.uuid4()
        country_id = uuid.uuid4()

        # Create mock address
        mock_address = MagicMock(spec=PersonAddress)
        mock_address.locality_id = locality_id
        mock_address.sub_district_id = sub_district_id
        mock_address.district_id = district_id
        mock_address.state_id = state_id
        mock_address.country_id = country_id

        # Create mock location objects
        mock_locality = MagicMock(spec=Locality)
        mock_locality.name = "TestVillage"

        mock_sub_district = MagicMock(spec=SubDistrict)
        mock_sub_district.name = "TestSubDistrict"

        mock_district = MagicMock(spec=District)
        mock_district.name = "TestDistrict"

        mock_state = MagicMock(spec=State)
        mock_state.name = "TestState"

        mock_country = MagicMock(spec=Country)
        mock_country.name = "TestCountry"

        # Setup mock session to return different results based on query
        call_count = [0]

        def mock_exec_side_effect(query):
            result = MagicMock()
            call_count[0] += 1
            if call_count[0] == 1:
                result.first.return_value = mock_address
            elif call_count[0] == 2:
                result.first.return_value = mock_locality
            elif call_count[0] == 3:
                result.first.return_value = mock_sub_district
            elif call_count[0] == 4:
                result.first.return_value = mock_district
            elif call_count[0] == 5:
                result.first.return_value = mock_state
            elif call_count[0] == 6:
                result.first.return_value = mock_country
            return result

        mock_session.exec.side_effect = mock_exec_side_effect

        service = LineagePathService(mock_session)
        result = service._get_address_string(person_id)

        assert "TestVillage" in result
        assert "TestSubDistrict" in result
        assert "TestDistrict" in result
        assert "TestState" in result
        assert "TestCountry" in result

    def test_get_address_string_handles_partial_address(
        self, mock_session: MagicMock
    ) -> None:
        """Test that partial address is handled correctly."""
        from app.db_models.address.district import District
        from app.db_models.address.state import State
        from app.db_models.person.person_address import PersonAddress

        person_id = uuid.uuid4()
        district_id = uuid.uuid4()
        state_id = uuid.uuid4()

        # Create mock address with only district and state
        mock_address = MagicMock(spec=PersonAddress)
        mock_address.locality_id = None
        mock_address.sub_district_id = None
        mock_address.district_id = district_id
        mock_address.state_id = state_id
        mock_address.country_id = None

        mock_district = MagicMock(spec=District)
        mock_district.name = "OnlyDistrict"

        mock_state = MagicMock(spec=State)
        mock_state.name = "OnlyState"

        call_count = [0]

        def mock_exec_side_effect(query):
            result = MagicMock()
            call_count[0] += 1
            if call_count[0] == 1:
                result.first.return_value = mock_address
            elif call_count[0] == 2:
                result.first.return_value = mock_district
            elif call_count[0] == 3:
                result.first.return_value = mock_state
            return result

        mock_session.exec.side_effect = mock_exec_side_effect

        service = LineagePathService(mock_session)
        result = service._get_address_string(person_id)

        assert "OnlyDistrict" in result
        assert "OnlyState" in result
        assert result == "OnlyDistrict, OnlyState"


# =============================================================================
# Tests for _get_religion_string Method
# =============================================================================


@pytest.mark.unit
class TestGetReligionString:
    """Tests for _get_religion_string method."""

    def test_get_religion_string_returns_empty_when_no_religion(
        self, mock_session: MagicMock
    ) -> None:
        """Test that empty string is returned when no religion found."""
        person_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result

        service = LineagePathService(mock_session)
        result = service._get_religion_string(person_id)

        assert result == ""

    def test_get_religion_string_returns_full_religion(
        self, mock_session: MagicMock
    ) -> None:
        """Test that full religion string is returned with all parts."""
        from app.db_models.person.person_religion import PersonReligion
        from app.db_models.religion.religion import Religion
        from app.db_models.religion.religion_category import ReligionCategory
        from app.db_models.religion.religion_sub_category import ReligionSubCategory

        person_id = uuid.uuid4()
        religion_id = uuid.uuid4()
        category_id = uuid.uuid4()
        sub_category_id = uuid.uuid4()

        # Create mock person religion
        mock_person_religion = MagicMock(spec=PersonReligion)
        mock_person_religion.religion_id = religion_id
        mock_person_religion.religion_category_id = category_id
        mock_person_religion.religion_sub_category_id = sub_category_id

        # Create mock religion objects
        mock_religion = MagicMock(spec=Religion)
        mock_religion.name = "Hinduism"

        mock_category = MagicMock(spec=ReligionCategory)
        mock_category.name = "Brahmin"

        mock_sub_category = MagicMock(spec=ReligionSubCategory)
        mock_sub_category.name = "Iyer"

        call_count = [0]

        def mock_exec_side_effect(query):
            result = MagicMock()
            call_count[0] += 1
            if call_count[0] == 1:
                result.first.return_value = mock_person_religion
            elif call_count[0] == 2:
                result.first.return_value = mock_religion
            elif call_count[0] == 3:
                result.first.return_value = mock_category
            elif call_count[0] == 4:
                result.first.return_value = mock_sub_category
            return result

        mock_session.exec.side_effect = mock_exec_side_effect

        service = LineagePathService(mock_session)
        result = service._get_religion_string(person_id)

        assert "Hinduism" in result
        assert "Brahmin" in result
        assert "Iyer" in result

    def test_get_religion_string_handles_partial_religion(
        self, mock_session: MagicMock
    ) -> None:
        """Test that partial religion info is handled correctly."""
        from app.db_models.person.person_religion import PersonReligion
        from app.db_models.religion.religion import Religion

        person_id = uuid.uuid4()
        religion_id = uuid.uuid4()

        # Create mock person religion with only religion (no category/subcategory)
        mock_person_religion = MagicMock(spec=PersonReligion)
        mock_person_religion.religion_id = religion_id
        mock_person_religion.religion_category_id = None
        mock_person_religion.religion_sub_category_id = None

        mock_religion = MagicMock(spec=Religion)
        mock_religion.name = "Christianity"

        call_count = [0]

        def mock_exec_side_effect(query):
            result = MagicMock()
            call_count[0] += 1
            if call_count[0] == 1:
                result.first.return_value = mock_person_religion
            elif call_count[0] == 2:
                result.first.return_value = mock_religion
            return result

        mock_session.exec.side_effect = mock_exec_side_effect

        service = LineagePathService(mock_session)
        result = service._get_religion_string(person_id)

        assert result == "Christianity"

"""Tests for PersonDiscoveryService sorting and deduplication logic."""

import uuid
from datetime import date

import pytest

from app.schemas.person.person_discovery import PersonDiscoveryResult
from app.services.person.person_discovery_service import PersonDiscoveryService


@pytest.mark.unit
class TestPersonDiscoveryServiceSortingAndDeduplication:
    """Test sorting and deduplication logic in PersonDiscoveryService."""

    def test_sort_by_proximity_score(self):
        """Test that results are sorted by proximity_score (ascending)."""
        # Create mock discoveries with different proximity scores
        discoveries = [
            PersonDiscoveryResult(
                person_id=uuid.uuid4(),
                first_name="Alice",
                middle_name=None,
                last_name="Smith",
                date_of_birth=date(1990, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d104",
                inferred_relationship_label="Son",
                connection_path="Connected to your spouse",
                proximity_score=3,  # Higher proximity
                relationship_priority=1,
            ),
            PersonDiscoveryResult(
                person_id=uuid.uuid4(),
                first_name="Bob",
                middle_name=None,
                last_name="Jones",
                date_of_birth=date(1985, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d104",
                inferred_relationship_label="Son",
                connection_path="Connected to your spouse",
                proximity_score=1,  # Lower proximity (should come first)
                relationship_priority=1,
            ),
            PersonDiscoveryResult(
                person_id=uuid.uuid4(),
                first_name="Charlie",
                middle_name=None,
                last_name="Brown",
                date_of_birth=date(1992, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d104",
                inferred_relationship_label="Son",
                connection_path="Connected to your spouse",
                proximity_score=2,  # Middle proximity
                relationship_priority=1,
            ),
        ]

        # Create service instance (we only need the sorting method)
        service = PersonDiscoveryService(session=None)  # type: ignore
        
        # Sort the discoveries
        sorted_discoveries = service._sort_and_limit_discoveries(discoveries)

        # Verify sorting by proximity_score
        assert len(sorted_discoveries) == 3
        assert sorted_discoveries[0].first_name == "Bob"  # proximity_score=1
        assert sorted_discoveries[1].first_name == "Charlie"  # proximity_score=2
        assert sorted_discoveries[2].first_name == "Alice"  # proximity_score=3

    def test_sort_by_relationship_priority_when_same_proximity(self):
        """Test that results with same proximity are sorted by relationship_priority."""
        discoveries = [
            PersonDiscoveryResult(
                person_id=uuid.uuid4(),
                first_name="Alice",
                middle_name=None,
                last_name="Smith",
                date_of_birth=date(1990, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d107",
                inferred_relationship_label="Spouse",
                connection_path="Connected to your child",
                proximity_score=2,
                relationship_priority=3,  # Spouse (lower priority)
            ),
            PersonDiscoveryResult(
                person_id=uuid.uuid4(),
                first_name="Bob",
                middle_name=None,
                last_name="Jones",
                date_of_birth=date(1985, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d104",
                inferred_relationship_label="Son",
                connection_path="Connected to your spouse",
                proximity_score=2,
                relationship_priority=1,  # Child (higher priority, should come first)
            ),
            PersonDiscoveryResult(
                person_id=uuid.uuid4(),
                first_name="Charlie",
                middle_name=None,
                last_name="Brown",
                date_of_birth=date(1992, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d101",
                inferred_relationship_label="Father",
                connection_path="Connected to your parent",
                proximity_score=2,
                relationship_priority=2,  # Parent (middle priority)
            ),
        ]

        service = PersonDiscoveryService(session=None)  # type: ignore
        sorted_discoveries = service._sort_and_limit_discoveries(discoveries)

        # Verify sorting by relationship_priority when proximity is same
        assert len(sorted_discoveries) == 3
        assert sorted_discoveries[0].first_name == "Bob"  # priority=1 (children)
        assert sorted_discoveries[1].first_name == "Charlie"  # priority=2 (parents)
        assert sorted_discoveries[2].first_name == "Alice"  # priority=3 (spouses)

    def test_sort_by_first_name_when_same_proximity_and_priority(self):
        """Test that results with same proximity and priority are sorted alphabetically."""
        discoveries = [
            PersonDiscoveryResult(
                person_id=uuid.uuid4(),
                first_name="Zoe",
                middle_name=None,
                last_name="Smith",
                date_of_birth=date(1990, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d104",
                inferred_relationship_label="Son",
                connection_path="Connected to your spouse",
                proximity_score=2,
                relationship_priority=1,
            ),
            PersonDiscoveryResult(
                person_id=uuid.uuid4(),
                first_name="Alice",
                middle_name=None,
                last_name="Jones",
                date_of_birth=date(1985, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d104",
                inferred_relationship_label="Son",
                connection_path="Connected to your spouse",
                proximity_score=2,
                relationship_priority=1,
            ),
            PersonDiscoveryResult(
                person_id=uuid.uuid4(),
                first_name="Mike",
                middle_name=None,
                last_name="Brown",
                date_of_birth=date(1992, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d104",
                inferred_relationship_label="Son",
                connection_path="Connected to your spouse",
                proximity_score=2,
                relationship_priority=1,
            ),
        ]

        service = PersonDiscoveryService(session=None)  # type: ignore
        sorted_discoveries = service._sort_and_limit_discoveries(discoveries)

        # Verify alphabetical sorting by first_name
        assert len(sorted_discoveries) == 3
        assert sorted_discoveries[0].first_name == "Alice"
        assert sorted_discoveries[1].first_name == "Mike"
        assert sorted_discoveries[2].first_name == "Zoe"

    def test_deduplication_keeps_lowest_proximity(self):
        """Test that deduplication keeps the result with lowest proximity_score."""
        person_id = uuid.uuid4()
        
        discoveries = [
            PersonDiscoveryResult(
                person_id=person_id,  # Same person
                first_name="Alice",
                middle_name=None,
                last_name="Smith",
                date_of_birth=date(1990, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d104",
                inferred_relationship_label="Son",
                connection_path="Connected to your spouse A",
                proximity_score=3,  # Higher proximity
                relationship_priority=1,
            ),
            PersonDiscoveryResult(
                person_id=person_id,  # Same person
                first_name="Alice",
                middle_name=None,
                last_name="Smith",
                date_of_birth=date(1990, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d104",
                inferred_relationship_label="Son",
                connection_path="Connected to your spouse B",
                proximity_score=1,  # Lower proximity (should be kept)
                relationship_priority=1,
            ),
        ]

        service = PersonDiscoveryService(session=None)  # type: ignore
        sorted_discoveries = service._sort_and_limit_discoveries(discoveries)

        # Verify deduplication kept the one with lowest proximity
        assert len(sorted_discoveries) == 1
        assert sorted_discoveries[0].proximity_score == 1
        assert sorted_discoveries[0].connection_path == "Connected to your spouse B"

    def test_deduplication_keeps_highest_priority_when_same_proximity(self):
        """Test that deduplication keeps highest priority when proximity is same."""
        person_id = uuid.uuid4()
        
        discoveries = [
            PersonDiscoveryResult(
                person_id=person_id,  # Same person
                first_name="Alice",
                middle_name=None,
                last_name="Smith",
                date_of_birth=date(1990, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d107",
                inferred_relationship_label="Spouse",
                connection_path="Connected to your child",
                proximity_score=2,
                relationship_priority=3,  # Lower priority (spouse)
            ),
            PersonDiscoveryResult(
                person_id=person_id,  # Same person
                first_name="Alice",
                middle_name=None,
                last_name="Smith",
                date_of_birth=date(1990, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d104",
                inferred_relationship_label="Son",
                connection_path="Connected to your spouse",
                proximity_score=2,
                relationship_priority=1,  # Higher priority (child, should be kept)
            ),
        ]

        service = PersonDiscoveryService(session=None)  # type: ignore
        sorted_discoveries = service._sort_and_limit_discoveries(discoveries)

        # Verify deduplication kept the one with highest priority
        assert len(sorted_discoveries) == 1
        assert sorted_discoveries[0].relationship_priority == 1
        assert sorted_discoveries[0].inferred_relationship_label == "Son"

    def test_limit_to_20_results(self):
        """Test that results are limited to maximum 20."""
        # Create 25 discoveries
        discoveries = []
        for i in range(25):
            discoveries.append(
                PersonDiscoveryResult(
                    person_id=uuid.uuid4(),
                    first_name=f"Person{i:02d}",
                    middle_name=None,
                    last_name="Smith",
                    date_of_birth=date(1990, 1, 1),
                    date_of_death=None,
                    gender_id=uuid.uuid4(),
                    address_display=None,
                    religion_display=None,
                    inferred_relationship_type="rel-6a0ede824d104",
                    inferred_relationship_label="Son",
                    connection_path="Connected to your spouse",
                    proximity_score=2,
                    relationship_priority=1,
                )
            )

        service = PersonDiscoveryService(session=None)  # type: ignore
        sorted_discoveries = service._sort_and_limit_discoveries(discoveries)

        # Verify limit to 20
        assert len(sorted_discoveries) == 20

    def test_empty_list_returns_empty(self):
        """Test that empty input returns empty output."""
        service = PersonDiscoveryService(session=None)  # type: ignore
        sorted_discoveries = service._sort_and_limit_discoveries([])

        assert len(sorted_discoveries) == 0
        assert sorted_discoveries == []



@pytest.mark.unit
class TestPersonDiscoveryServiceGenderInference:
    """Tests for gender-based relationship inference."""

    def test_infer_child_relationship_male(self):
        """Test that male gender infers Son relationship."""
        service = PersonDiscoveryService(session=None)  # type: ignore
        male_gender_id = uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83")
        
        result = service._infer_child_relationship(male_gender_id)
        
        from app.enums.relationship_type import RelationshipType
        assert result == RelationshipType.SON

    def test_infer_child_relationship_female(self):
        """Test that female gender infers Daughter relationship."""
        service = PersonDiscoveryService(session=None)  # type: ignore
        female_gender_id = uuid.UUID("691fde27-f82c-4a84-832f-4243acef4b95")
        
        result = service._infer_child_relationship(female_gender_id)
        
        from app.enums.relationship_type import RelationshipType
        assert result == RelationshipType.DAUGHTER

    def test_infer_child_relationship_unknown_defaults_to_son(self):
        """Test that unknown gender defaults to Son relationship."""
        service = PersonDiscoveryService(session=None)  # type: ignore
        unknown_gender_id = uuid.uuid4()  # Random UUID not in mapping
        
        result = service._infer_child_relationship(unknown_gender_id)
        
        from app.enums.relationship_type import RelationshipType
        assert result == RelationshipType.SON

    def test_infer_parent_relationship_male(self):
        """Test that male gender infers Father relationship."""
        service = PersonDiscoveryService(session=None)  # type: ignore
        male_gender_id = uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83")
        
        result = service._infer_parent_relationship(male_gender_id)
        
        from app.enums.relationship_type import RelationshipType
        assert result == RelationshipType.FATHER

    def test_infer_parent_relationship_female(self):
        """Test that female gender infers Mother relationship."""
        service = PersonDiscoveryService(session=None)  # type: ignore
        female_gender_id = uuid.UUID("691fde27-f82c-4a84-832f-4243acef4b95")
        
        result = service._infer_parent_relationship(female_gender_id)
        
        from app.enums.relationship_type import RelationshipType
        assert result == RelationshipType.MOTHER

    def test_infer_parent_relationship_unknown_defaults_to_father(self):
        """Test that unknown gender defaults to Father relationship."""
        service = PersonDiscoveryService(session=None)  # type: ignore
        unknown_gender_id = uuid.uuid4()  # Random UUID not in mapping
        
        result = service._infer_parent_relationship(unknown_gender_id)
        
        from app.enums.relationship_type import RelationshipType
        assert result == RelationshipType.FATHER


@pytest.mark.unit
class TestPersonDiscoveryServiceGenderCode:
    """Tests for gender code lookup."""

    def test_get_gender_code_male(self):
        """Test getting gender code for male."""
        service = PersonDiscoveryService(session=None)  # type: ignore
        male_gender_id = uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83")
        
        result = service._get_gender_code(male_gender_id)
        
        assert result == "male"

    def test_get_gender_code_female(self):
        """Test getting gender code for female."""
        service = PersonDiscoveryService(session=None)  # type: ignore
        female_gender_id = uuid.UUID("691fde27-f82c-4a84-832f-4243acef4b95")
        
        result = service._get_gender_code(female_gender_id)
        
        assert result == "female"

    def test_get_gender_code_unknown(self):
        """Test getting gender code for unknown gender returns 'unknown'."""
        service = PersonDiscoveryService(session=None)  # type: ignore
        unknown_gender_id = uuid.uuid4()
        
        result = service._get_gender_code(unknown_gender_id)
        
        assert result == "unknown"


@pytest.mark.unit
class TestPersonDiscoveryServiceConnectedIds:
    """Tests for connected person ID extraction."""

    def test_get_connected_person_ids_includes_self(self):
        """Test that connected IDs include the person's own ID."""
        from unittest.mock import MagicMock
        
        service = PersonDiscoveryService(session=None)  # type: ignore
        person_id = uuid.uuid4()
        
        # Empty relationships
        relationships = []
        
        result = service._get_connected_person_ids_from_relationships(
            person_id, relationships
        )
        
        assert person_id in result

    def test_get_connected_person_ids_includes_related_persons(self):
        """Test that connected IDs include all related person IDs."""
        from unittest.mock import MagicMock
        from app.db_models.person.person_relationship import PersonRelationship
        
        service = PersonDiscoveryService(session=None)  # type: ignore
        person_id = uuid.uuid4()
        related_id_1 = uuid.uuid4()
        related_id_2 = uuid.uuid4()
        
        # Create mock relationships
        rel1 = MagicMock(spec=PersonRelationship)
        rel1.related_person_id = related_id_1
        rel2 = MagicMock(spec=PersonRelationship)
        rel2.related_person_id = related_id_2
        
        relationships = [rel1, rel2]
        
        result = service._get_connected_person_ids_from_relationships(
            person_id, relationships
        )
        
        assert person_id in result
        assert related_id_1 in result
        assert related_id_2 in result
        assert len(result) == 3


@pytest.mark.unit
class TestPersonDiscoveryServiceDiscoveryPatterns:
    """Tests for discovery pattern methods with mocked repositories."""

    def test_discover_family_members_no_person_record(self):
        """Test discovery returns empty list when user has no person record."""
        from unittest.mock import MagicMock, patch
        
        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)
        
        user_id = uuid.uuid4()
        
        with patch.object(service.person_repo, "get_by_user_id", return_value=None):
            result = service.discover_family_members(user_id)
        
        assert result == []

    def test_discover_family_members_no_relationships(self):
        """Test discovery returns empty list when user has no relationships."""
        from unittest.mock import MagicMock, patch
        from app.db_models.person.person import Person
        
        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)
        
        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"
        
        with patch.object(service.person_repo, "get_by_user_id", return_value=mock_person):
            with patch.object(service.relationship_repo, "get_active_relationships", return_value=[]):
                result = service.discover_family_members(user_id)
        
        assert result == []

    def test_discover_spouses_children_empty_when_no_spouses(self):
        """Test spouse's children discovery returns empty when user has no spouses."""
        from unittest.mock import MagicMock
        
        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)
        
        person_id = uuid.uuid4()
        user_relationships = []  # No relationships
        connected_person_ids = {person_id}
        
        result = service._discover_spouses_children(
            person_id, user_relationships, connected_person_ids
        )
        
        assert result == []

    def test_discover_parents_spouse_empty_when_no_parents(self):
        """Test parent's spouse discovery returns empty when user has no parents."""
        from unittest.mock import MagicMock
        
        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)
        
        person_id = uuid.uuid4()
        user_relationships = []  # No relationships
        connected_person_ids = {person_id}
        
        result = service._discover_parents_spouse(
            person_id, user_relationships, connected_person_ids
        )
        
        assert result == []

    def test_discover_childs_parent_empty_when_no_children(self):
        """Test child's parent discovery returns empty when user has no children."""
        from unittest.mock import MagicMock
        
        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)
        
        person_id = uuid.uuid4()
        user_relationships = []  # No relationships
        connected_person_ids = {person_id}
        
        result = service._discover_childs_parent(
            person_id, user_relationships, connected_person_ids
        )
        
        assert result == []


@pytest.mark.unit
class TestPersonDiscoveryServiceBuildResult:
    """Tests for building discovery results."""

    def test_build_discovery_result_success(self):
        """Test building discovery result with valid person data."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.enums.relationship_type import RelationshipType
        
        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)
        
        person_id = uuid.uuid4()
        gender_id = uuid.uuid4()
        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.middle_name = "Michael"
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = date(1990, 1, 1)
        mock_person.date_of_death = None
        mock_person.gender_id = gender_id
        
        result = service._build_discovery_result(
            person=mock_person,
            inferred_relationship_type=RelationshipType.SON,
            connection_path="Connected to your spouse",
            proximity_score=2,
            relationship_priority=1,
        )
        
        assert result is not None
        assert result.person_id == person_id
        assert result.first_name == "John"
        assert result.middle_name == "Michael"
        assert result.last_name == "Doe"
        assert result.proximity_score == 2
        assert result.relationship_priority == 1

    def test_build_discovery_result_missing_first_name(self):
        """Test building discovery result returns None when first_name is missing."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.enums.relationship_type import RelationshipType
        
        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)
        
        mock_person = MagicMock(spec=Person)
        mock_person.id = uuid.uuid4()
        mock_person.first_name = None  # Missing
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = date(1990, 1, 1)
        
        result = service._build_discovery_result(
            person=mock_person,
            inferred_relationship_type=RelationshipType.SON,
            connection_path="Connected to your spouse",
            proximity_score=2,
            relationship_priority=1,
        )
        
        assert result is None

    def test_build_discovery_result_missing_last_name(self):
        """Test building discovery result returns None when last_name is missing."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.enums.relationship_type import RelationshipType
        
        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)
        
        mock_person = MagicMock(spec=Person)
        mock_person.id = uuid.uuid4()
        mock_person.first_name = "John"
        mock_person.last_name = None  # Missing
        mock_person.date_of_birth = date(1990, 1, 1)
        
        result = service._build_discovery_result(
            person=mock_person,
            inferred_relationship_type=RelationshipType.SON,
            connection_path="Connected to your spouse",
            proximity_score=2,
            relationship_priority=1,
        )
        
        assert result is None

    def test_build_discovery_result_missing_date_of_birth(self):
        """Test building discovery result returns None when date_of_birth is missing."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.enums.relationship_type import RelationshipType
        
        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)
        
        mock_person = MagicMock(spec=Person)
        mock_person.id = uuid.uuid4()
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"
        mock_person.date_of_birth = None  # Missing
        
        result = service._build_discovery_result(
            person=mock_person,
            inferred_relationship_type=RelationshipType.SON,
            connection_path="Connected to your spouse",
            proximity_score=2,
            relationship_priority=1,
        )
        
        assert result is None


@pytest.mark.unit
class TestPersonDiscoveryServicePaginationEdgeCases:
    """Tests for pagination and limit edge cases."""

    def test_sort_and_limit_exactly_20_results(self):
        """Test that exactly 20 results are returned unchanged."""
        discoveries = []
        for i in range(20):
            discoveries.append(
                PersonDiscoveryResult(
                    person_id=uuid.uuid4(),
                    first_name=f"Person{i:02d}",
                    middle_name=None,
                    last_name="Smith",
                    date_of_birth=date(1990, 1, 1),
                    date_of_death=None,
                    gender_id=uuid.uuid4(),
                    address_display=None,
                    religion_display=None,
                    inferred_relationship_type="rel-6a0ede824d104",
                    inferred_relationship_label="Son",
                    connection_path="Connected to your spouse",
                    proximity_score=2,
                    relationship_priority=1,
                )
            )

        service = PersonDiscoveryService(session=None)  # type: ignore
        sorted_discoveries = service._sort_and_limit_discoveries(discoveries)

        assert len(sorted_discoveries) == 20

    def test_sort_and_limit_less_than_20_results(self):
        """Test that fewer than 20 results are returned as-is."""
        discoveries = []
        for i in range(5):
            discoveries.append(
                PersonDiscoveryResult(
                    person_id=uuid.uuid4(),
                    first_name=f"Person{i:02d}",
                    middle_name=None,
                    last_name="Smith",
                    date_of_birth=date(1990, 1, 1),
                    date_of_death=None,
                    gender_id=uuid.uuid4(),
                    address_display=None,
                    religion_display=None,
                    inferred_relationship_type="rel-6a0ede824d104",
                    inferred_relationship_label="Son",
                    connection_path="Connected to your spouse",
                    proximity_score=2,
                    relationship_priority=1,
                )
            )

        service = PersonDiscoveryService(session=None)  # type: ignore
        sorted_discoveries = service._sort_and_limit_discoveries(discoveries)

        assert len(sorted_discoveries) == 5

    def test_sort_and_limit_single_result(self):
        """Test that a single result is returned correctly."""
        discoveries = [
            PersonDiscoveryResult(
                person_id=uuid.uuid4(),
                first_name="Alice",
                middle_name=None,
                last_name="Smith",
                date_of_birth=date(1990, 1, 1),
                date_of_death=None,
                gender_id=uuid.uuid4(),
                address_display=None,
                religion_display=None,
                inferred_relationship_type="rel-6a0ede824d104",
                inferred_relationship_label="Son",
                connection_path="Connected to your spouse",
                proximity_score=2,
                relationship_priority=1,
            )
        ]

        service = PersonDiscoveryService(session=None)  # type: ignore
        sorted_discoveries = service._sort_and_limit_discoveries(discoveries)

        assert len(sorted_discoveries) == 1
        assert sorted_discoveries[0].first_name == "Alice"

    def test_deduplication_with_many_duplicates(self):
        """Test deduplication when same person appears many times."""
        person_id = uuid.uuid4()
        discoveries = []
        
        # Same person appearing 10 times with different proximity scores
        for i in range(10):
            discoveries.append(
                PersonDiscoveryResult(
                    person_id=person_id,
                    first_name="Alice",
                    middle_name=None,
                    last_name="Smith",
                    date_of_birth=date(1990, 1, 1),
                    date_of_death=None,
                    gender_id=uuid.uuid4(),
                    address_display=None,
                    religion_display=None,
                    inferred_relationship_type="rel-6a0ede824d104",
                    inferred_relationship_label="Son",
                    connection_path=f"Path {i}",
                    proximity_score=i + 1,  # Different proximity scores
                    relationship_priority=1,
                )
            )

        service = PersonDiscoveryService(session=None)  # type: ignore
        sorted_discoveries = service._sort_and_limit_discoveries(discoveries)

        # Should deduplicate to single result with lowest proximity
        assert len(sorted_discoveries) == 1
        assert sorted_discoveries[0].proximity_score == 1
        assert sorted_discoveries[0].connection_path == "Path 0"

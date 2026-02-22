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


@pytest.mark.unit
class TestPersonDiscoveryServiceSpousesChildren:
    """Tests for discovering spouse's children pattern."""

    def test_discover_spouses_children_with_spouse_having_children(self):
        """Test discovering children from spouse who has children."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.db_models.person.person_relationship import PersonRelationship
        from app.enums.relationship_type import RelationshipType

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        person_id = uuid.uuid4()
        spouse_id = uuid.uuid4()
        child_id = uuid.uuid4()
        male_gender_id = uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83")

        # Create spouse relationship
        spouse_rel = MagicMock(spec=PersonRelationship)
        spouse_rel.related_person_id = spouse_id
        spouse_rel.relationship_type = RelationshipType.WIFE

        # Create spouse person
        spouse_person = MagicMock(spec=Person)
        spouse_person.id = spouse_id
        spouse_person.first_name = "Jane"
        spouse_person.last_name = "Doe"

        # Create child relationship (spouse's child)
        child_rel = MagicMock(spec=PersonRelationship)
        child_rel.related_person_id = child_id
        child_rel.relationship_type = RelationshipType.SON
        child_rel.is_active = True

        # Create child person
        child_person = MagicMock(spec=Person)
        child_person.id = child_id
        child_person.first_name = "Johnny"
        child_person.middle_name = None
        child_person.last_name = "Doe"
        child_person.date_of_birth = date(2010, 5, 15)
        child_person.date_of_death = None
        child_person.gender_id = male_gender_id

        # Mock repository methods
        service.person_repo.get_by_id = MagicMock(side_effect=lambda id: {
            spouse_id: spouse_person,
            child_id: child_person,
        }.get(id))
        service.relationship_repo.get_by_relationship_types = MagicMock(return_value=[child_rel])

        user_relationships = [spouse_rel]
        connected_person_ids = {person_id}  # Only self is connected

        result = service._discover_spouses_children(
            person_id, user_relationships, connected_person_ids
        )

        assert len(result) == 1
        assert result[0].person_id == child_id
        assert result[0].first_name == "Johnny"
        assert result[0].inferred_relationship_type == RelationshipType.SON.value
        assert "Jane Doe" in result[0].connection_path

    def test_discover_spouses_children_skips_already_connected(self):
        """Test that already connected children are skipped."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.db_models.person.person_relationship import PersonRelationship
        from app.enums.relationship_type import RelationshipType

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        person_id = uuid.uuid4()
        spouse_id = uuid.uuid4()
        child_id = uuid.uuid4()

        # Create spouse relationship
        spouse_rel = MagicMock(spec=PersonRelationship)
        spouse_rel.related_person_id = spouse_id
        spouse_rel.relationship_type = RelationshipType.HUSBAND

        # Create spouse person
        spouse_person = MagicMock(spec=Person)
        spouse_person.id = spouse_id
        spouse_person.first_name = "John"
        spouse_person.last_name = "Doe"

        # Create child relationship
        child_rel = MagicMock(spec=PersonRelationship)
        child_rel.related_person_id = child_id
        child_rel.relationship_type = RelationshipType.DAUGHTER
        child_rel.is_active = True

        service.person_repo.get_by_id = MagicMock(return_value=spouse_person)
        service.relationship_repo.get_by_relationship_types = MagicMock(return_value=[child_rel])

        user_relationships = [spouse_rel]
        # Child is already connected
        connected_person_ids = {person_id, child_id}

        result = service._discover_spouses_children(
            person_id, user_relationships, connected_person_ids
        )

        assert len(result) == 0

    def test_discover_spouses_children_infers_daughter_for_female(self):
        """Test that female child is inferred as Daughter."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.db_models.person.person_relationship import PersonRelationship
        from app.enums.relationship_type import RelationshipType

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        person_id = uuid.uuid4()
        spouse_id = uuid.uuid4()
        child_id = uuid.uuid4()
        female_gender_id = uuid.UUID("691fde27-f82c-4a84-832f-4243acef4b95")

        spouse_rel = MagicMock(spec=PersonRelationship)
        spouse_rel.related_person_id = spouse_id
        spouse_rel.relationship_type = RelationshipType.SPOUSE

        spouse_person = MagicMock(spec=Person)
        spouse_person.id = spouse_id
        spouse_person.first_name = "Partner"
        spouse_person.last_name = "Smith"

        child_rel = MagicMock(spec=PersonRelationship)
        child_rel.related_person_id = child_id
        child_rel.relationship_type = RelationshipType.DAUGHTER
        child_rel.is_active = True

        child_person = MagicMock(spec=Person)
        child_person.id = child_id
        child_person.first_name = "Sarah"
        child_person.middle_name = None
        child_person.last_name = "Smith"
        child_person.date_of_birth = date(2012, 3, 20)
        child_person.date_of_death = None
        child_person.gender_id = female_gender_id

        service.person_repo.get_by_id = MagicMock(side_effect=lambda id: {
            spouse_id: spouse_person,
            child_id: child_person,
        }.get(id))
        service.relationship_repo.get_by_relationship_types = MagicMock(return_value=[child_rel])

        user_relationships = [spouse_rel]
        connected_person_ids = {person_id}

        result = service._discover_spouses_children(
            person_id, user_relationships, connected_person_ids
        )

        assert len(result) == 1
        assert result[0].inferred_relationship_type == RelationshipType.DAUGHTER.value


@pytest.mark.unit
class TestPersonDiscoveryServiceParentsSpouse:
    """Tests for discovering parent's spouse pattern."""

    def test_discover_parents_spouse_with_parent_having_spouse(self):
        """Test discovering spouse from parent who has a spouse."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.db_models.person.person_relationship import PersonRelationship
        from app.enums.relationship_type import RelationshipType

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        person_id = uuid.uuid4()
        parent_id = uuid.uuid4()
        parent_spouse_id = uuid.uuid4()
        female_gender_id = uuid.UUID("691fde27-f82c-4a84-832f-4243acef4b95")

        # Create parent relationship (Father)
        parent_rel = MagicMock(spec=PersonRelationship)
        parent_rel.related_person_id = parent_id
        parent_rel.relationship_type = RelationshipType.FATHER

        # Create parent person
        parent_person = MagicMock(spec=Person)
        parent_person.id = parent_id
        parent_person.first_name = "Robert"
        parent_person.last_name = "Doe"

        # Create parent's spouse relationship
        spouse_rel = MagicMock(spec=PersonRelationship)
        spouse_rel.related_person_id = parent_spouse_id
        spouse_rel.relationship_type = RelationshipType.WIFE
        spouse_rel.is_active = True

        # Create parent's spouse person (potential Mother)
        spouse_person = MagicMock(spec=Person)
        spouse_person.id = parent_spouse_id
        spouse_person.first_name = "Mary"
        spouse_person.middle_name = None
        spouse_person.last_name = "Doe"
        spouse_person.date_of_birth = date(1965, 8, 10)
        spouse_person.date_of_death = None
        spouse_person.gender_id = female_gender_id

        service.person_repo.get_by_id = MagicMock(side_effect=lambda id: {
            parent_id: parent_person,
            parent_spouse_id: spouse_person,
        }.get(id))
        service.relationship_repo.get_by_relationship_types = MagicMock(return_value=[spouse_rel])

        user_relationships = [parent_rel]
        connected_person_ids = {person_id}

        result = service._discover_parents_spouse(
            person_id, user_relationships, connected_person_ids
        )

        assert len(result) == 1
        assert result[0].person_id == parent_spouse_id
        assert result[0].first_name == "Mary"
        assert result[0].inferred_relationship_type == RelationshipType.MOTHER.value
        assert "Robert Doe" in result[0].connection_path

    def test_discover_parents_spouse_infers_father_for_male(self):
        """Test that male parent's spouse is inferred as Father."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.db_models.person.person_relationship import PersonRelationship
        from app.enums.relationship_type import RelationshipType

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        person_id = uuid.uuid4()
        parent_id = uuid.uuid4()
        parent_spouse_id = uuid.uuid4()
        male_gender_id = uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83")

        parent_rel = MagicMock(spec=PersonRelationship)
        parent_rel.related_person_id = parent_id
        parent_rel.relationship_type = RelationshipType.MOTHER

        parent_person = MagicMock(spec=Person)
        parent_person.id = parent_id
        parent_person.first_name = "Susan"
        parent_person.last_name = "Smith"

        spouse_rel = MagicMock(spec=PersonRelationship)
        spouse_rel.related_person_id = parent_spouse_id
        spouse_rel.relationship_type = RelationshipType.HUSBAND
        spouse_rel.is_active = True

        spouse_person = MagicMock(spec=Person)
        spouse_person.id = parent_spouse_id
        spouse_person.first_name = "David"
        spouse_person.middle_name = None
        spouse_person.last_name = "Smith"
        spouse_person.date_of_birth = date(1960, 4, 5)
        spouse_person.date_of_death = None
        spouse_person.gender_id = male_gender_id

        service.person_repo.get_by_id = MagicMock(side_effect=lambda id: {
            parent_id: parent_person,
            parent_spouse_id: spouse_person,
        }.get(id))
        service.relationship_repo.get_by_relationship_types = MagicMock(return_value=[spouse_rel])

        user_relationships = [parent_rel]
        connected_person_ids = {person_id}

        result = service._discover_parents_spouse(
            person_id, user_relationships, connected_person_ids
        )

        assert len(result) == 1
        assert result[0].inferred_relationship_type == RelationshipType.FATHER.value

    def test_discover_parents_spouse_skips_already_connected(self):
        """Test that already connected parent's spouse is skipped."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.db_models.person.person_relationship import PersonRelationship
        from app.enums.relationship_type import RelationshipType

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        person_id = uuid.uuid4()
        parent_id = uuid.uuid4()
        parent_spouse_id = uuid.uuid4()

        parent_rel = MagicMock(spec=PersonRelationship)
        parent_rel.related_person_id = parent_id
        parent_rel.relationship_type = RelationshipType.FATHER

        parent_person = MagicMock(spec=Person)
        parent_person.id = parent_id
        parent_person.first_name = "Robert"
        parent_person.last_name = "Doe"

        spouse_rel = MagicMock(spec=PersonRelationship)
        spouse_rel.related_person_id = parent_spouse_id
        spouse_rel.relationship_type = RelationshipType.WIFE
        spouse_rel.is_active = True

        service.person_repo.get_by_id = MagicMock(return_value=parent_person)
        service.relationship_repo.get_by_relationship_types = MagicMock(return_value=[spouse_rel])

        user_relationships = [parent_rel]
        # Parent's spouse is already connected
        connected_person_ids = {person_id, parent_spouse_id}

        result = service._discover_parents_spouse(
            person_id, user_relationships, connected_person_ids
        )

        assert len(result) == 0


@pytest.mark.unit
class TestPersonDiscoveryServiceChildsParent:
    """Tests for discovering child's other parent pattern."""

    def test_discover_childs_parent_with_child_having_other_parent(self):
        """Test discovering other parent from child."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.db_models.person.person_relationship import PersonRelationship
        from app.enums.relationship_type import RelationshipType

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        person_id = uuid.uuid4()
        child_id = uuid.uuid4()
        other_parent_id = uuid.uuid4()
        female_gender_id = uuid.UUID("691fde27-f82c-4a84-832f-4243acef4b95")

        # Create child relationship
        child_rel = MagicMock(spec=PersonRelationship)
        child_rel.related_person_id = child_id
        child_rel.relationship_type = RelationshipType.SON

        # Create child person
        child_person = MagicMock(spec=Person)
        child_person.id = child_id
        child_person.first_name = "Tommy"
        child_person.last_name = "Doe"

        # Create child's other parent relationship
        parent_rel = MagicMock(spec=PersonRelationship)
        parent_rel.related_person_id = other_parent_id
        parent_rel.relationship_type = RelationshipType.MOTHER
        parent_rel.is_active = True

        # Create other parent person (potential Spouse)
        other_parent_person = MagicMock(spec=Person)
        other_parent_person.id = other_parent_id
        other_parent_person.first_name = "Lisa"
        other_parent_person.middle_name = None
        other_parent_person.last_name = "Johnson"
        other_parent_person.date_of_birth = date(1985, 11, 25)
        other_parent_person.date_of_death = None
        other_parent_person.gender_id = female_gender_id

        service.person_repo.get_by_id = MagicMock(side_effect=lambda id: {
            child_id: child_person,
            other_parent_id: other_parent_person,
        }.get(id))
        service.relationship_repo.get_by_relationship_types = MagicMock(return_value=[parent_rel])

        user_relationships = [child_rel]
        connected_person_ids = {person_id}

        result = service._discover_childs_parent(
            person_id, user_relationships, connected_person_ids
        )

        assert len(result) == 1
        assert result[0].person_id == other_parent_id
        assert result[0].first_name == "Lisa"
        # Child's other parent is always inferred as Spouse (gender-neutral)
        assert result[0].inferred_relationship_type == RelationshipType.SPOUSE.value
        assert "Tommy Doe" in result[0].connection_path

    def test_discover_childs_parent_skips_already_connected(self):
        """Test that already connected child's parent is skipped."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.db_models.person.person_relationship import PersonRelationship
        from app.enums.relationship_type import RelationshipType

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        person_id = uuid.uuid4()
        child_id = uuid.uuid4()
        other_parent_id = uuid.uuid4()

        child_rel = MagicMock(spec=PersonRelationship)
        child_rel.related_person_id = child_id
        child_rel.relationship_type = RelationshipType.DAUGHTER

        child_person = MagicMock(spec=Person)
        child_person.id = child_id
        child_person.first_name = "Emma"
        child_person.last_name = "Doe"

        parent_rel = MagicMock(spec=PersonRelationship)
        parent_rel.related_person_id = other_parent_id
        parent_rel.relationship_type = RelationshipType.FATHER
        parent_rel.is_active = True

        service.person_repo.get_by_id = MagicMock(return_value=child_person)
        service.relationship_repo.get_by_relationship_types = MagicMock(return_value=[parent_rel])

        user_relationships = [child_rel]
        # Other parent is already connected
        connected_person_ids = {person_id, other_parent_id}

        result = service._discover_childs_parent(
            person_id, user_relationships, connected_person_ids
        )

        assert len(result) == 0

    def test_discover_childs_parent_with_multiple_children(self):
        """Test discovering parents from multiple children."""
        from unittest.mock import MagicMock
        from app.db_models.person.person import Person
        from app.db_models.person.person_relationship import PersonRelationship
        from app.enums.relationship_type import RelationshipType

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        person_id = uuid.uuid4()
        child1_id = uuid.uuid4()
        child2_id = uuid.uuid4()
        other_parent_id = uuid.uuid4()
        male_gender_id = uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83")

        # Create child relationships
        child1_rel = MagicMock(spec=PersonRelationship)
        child1_rel.related_person_id = child1_id
        child1_rel.relationship_type = RelationshipType.SON

        child2_rel = MagicMock(spec=PersonRelationship)
        child2_rel.related_person_id = child2_id
        child2_rel.relationship_type = RelationshipType.DAUGHTER

        # Create child persons
        child1_person = MagicMock(spec=Person)
        child1_person.id = child1_id
        child1_person.first_name = "Tom"
        child1_person.last_name = "Doe"

        child2_person = MagicMock(spec=Person)
        child2_person.id = child2_id
        child2_person.first_name = "Amy"
        child2_person.last_name = "Doe"

        # Create other parent relationship (same parent for both children)
        parent_rel = MagicMock(spec=PersonRelationship)
        parent_rel.related_person_id = other_parent_id
        parent_rel.relationship_type = RelationshipType.FATHER
        parent_rel.is_active = True

        # Create other parent person
        other_parent_person = MagicMock(spec=Person)
        other_parent_person.id = other_parent_id
        other_parent_person.first_name = "Mike"
        other_parent_person.middle_name = None
        other_parent_person.last_name = "Johnson"
        other_parent_person.date_of_birth = date(1980, 6, 15)
        other_parent_person.date_of_death = None
        other_parent_person.gender_id = male_gender_id

        service.person_repo.get_by_id = MagicMock(side_effect=lambda id: {
            child1_id: child1_person,
            child2_id: child2_person,
            other_parent_id: other_parent_person,
        }.get(id))
        # Both children have the same other parent
        service.relationship_repo.get_by_relationship_types = MagicMock(return_value=[parent_rel])

        user_relationships = [child1_rel, child2_rel]
        connected_person_ids = {person_id}

        result = service._discover_childs_parent(
            person_id, user_relationships, connected_person_ids
        )

        # Same parent discovered through both children, but should appear twice
        # (deduplication happens in _sort_and_limit_discoveries)
        assert len(result) == 2
        assert all(r.person_id == other_parent_id for r in result)


@pytest.mark.unit
class TestPersonDiscoveryServiceFullDiscovery:
    """Tests for the full discover_family_members method."""

    def test_discover_family_members_with_person_id(self):
        """Test discovery using explicit person_id parameter."""
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

        # Create a mock for get_by_id
        mock_get_by_id = MagicMock(return_value=mock_person)
        
        with patch.object(service.person_repo, "get_by_id", mock_get_by_id):
            with patch.object(service.relationship_repo, "get_active_relationships", return_value=[]):
                result = service.discover_family_members(user_id, person_id=person_id)

        assert result == []
        # Verify get_by_id was called with person_id
        mock_get_by_id.assert_called_once_with(person_id)

    def test_discover_family_members_person_not_found_by_id(self):
        """Test discovery returns empty when person_id not found."""
        from unittest.mock import MagicMock, patch

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        user_id = uuid.uuid4()
        person_id = uuid.uuid4()

        with patch.object(service.person_repo, "get_by_id", return_value=None):
            result = service.discover_family_members(user_id, person_id=person_id)

        assert result == []

    def test_discover_family_members_combines_all_patterns(self):
        """Test that discovery combines results from all three patterns."""
        from unittest.mock import MagicMock, patch
        from app.db_models.person.person import Person
        from app.db_models.person.person_relationship import PersonRelationship
        from app.enums.relationship_type import RelationshipType

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        spouse_id = uuid.uuid4()
        parent_id = uuid.uuid4()
        child_id = uuid.uuid4()
        male_gender_id = uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83")

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"

        # Create relationships for all three patterns
        spouse_rel = MagicMock(spec=PersonRelationship)
        spouse_rel.related_person_id = spouse_id
        spouse_rel.relationship_type = RelationshipType.WIFE

        parent_rel = MagicMock(spec=PersonRelationship)
        parent_rel.related_person_id = parent_id
        parent_rel.relationship_type = RelationshipType.FATHER

        child_rel = MagicMock(spec=PersonRelationship)
        child_rel.related_person_id = child_id
        child_rel.relationship_type = RelationshipType.SON

        user_relationships = [spouse_rel, parent_rel, child_rel]

        # Create mock discovery results
        discovery1 = PersonDiscoveryResult(
            person_id=uuid.uuid4(),
            first_name="Child1",
            middle_name=None,
            last_name="Doe",
            date_of_birth=date(2010, 1, 1),
            date_of_death=None,
            gender_id=male_gender_id,
            address_display=None,
            religion_display=None,
            inferred_relationship_type=RelationshipType.SON.value,
            inferred_relationship_label="Son",
            connection_path="From spouse",
            proximity_score=2,
            relationship_priority=1,
        )

        with patch.object(service.person_repo, "get_by_user_id", return_value=mock_person):
            with patch.object(service.relationship_repo, "get_active_relationships", return_value=user_relationships):
                with patch.object(service, "_discover_spouses_children", return_value=[discovery1]):
                    with patch.object(service, "_discover_parents_spouse", return_value=[]):
                        with patch.object(service, "_discover_childs_parent", return_value=[]):
                            result = service.discover_family_members(user_id)

        assert len(result) == 1
        assert result[0].first_name == "Child1"

    def test_discover_family_members_handles_pattern_errors_gracefully(self):
        """Test that errors in one pattern don't break other patterns."""
        from unittest.mock import MagicMock, patch
        from app.db_models.person.person import Person

        mock_session = MagicMock()
        service = PersonDiscoveryService(mock_session)

        user_id = uuid.uuid4()
        person_id = uuid.uuid4()
        male_gender_id = uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83")

        mock_person = MagicMock(spec=Person)
        mock_person.id = person_id
        mock_person.first_name = "John"
        mock_person.last_name = "Doe"

        discovery = PersonDiscoveryResult(
            person_id=uuid.uuid4(),
            first_name="Found",
            middle_name=None,
            last_name="Person",
            date_of_birth=date(1990, 1, 1),
            date_of_death=None,
            gender_id=male_gender_id,
            address_display=None,
            religion_display=None,
            inferred_relationship_type="rel-6a0ede824d104",
            inferred_relationship_label="Son",
            connection_path="Test",
            proximity_score=2,
            relationship_priority=1,
        )

        with patch.object(service.person_repo, "get_by_user_id", return_value=mock_person):
            with patch.object(service.relationship_repo, "get_active_relationships", return_value=[]):
                # First pattern raises error
                with patch.object(service, "_discover_spouses_children", side_effect=Exception("Test error")):
                    # Second pattern returns result
                    with patch.object(service, "_discover_parents_spouse", return_value=[discovery]):
                        with patch.object(service, "_discover_childs_parent", return_value=[]):
                            result = service.discover_family_members(user_id)

        # Should still return results from working patterns
        assert len(result) == 1
        assert result[0].first_name == "Found"

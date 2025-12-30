"""Tests for PersonDiscoveryService sorting and deduplication logic."""

import uuid
from datetime import date

import pytest

from app.schemas.person.person_discovery import PersonDiscoveryResult
from app.services.person.person_discovery_service import PersonDiscoveryService


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

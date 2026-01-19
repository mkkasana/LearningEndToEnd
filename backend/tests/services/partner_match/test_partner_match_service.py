"""Unit tests for PartnerMatchService.

Tests cover:
- Seeker validation (404 for non-existent)
- Gender filter
- Birth year range filter
- Religion inclusion filters
- Gotra exclusion filter
- Living person filter
- Marital status filter
- Graph structure (from_person, to_persons)

Requirements: 1.1, 1.2, 2.1, 3.1, 3.2, 4.1, 5.1, 6.1, 7.1, 7.2, 8.3, 8.4
"""

import uuid
from datetime import date
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.enums.gender import GENDER_DATA, GenderEnum
from app.enums.relationship_type import RelationshipType
from app.schemas.partner_match import PartnerMatchRequest
from app.services.partner_match.partner_match_service import (
    PartnerMatchService,
    PersonReligionIds,
)


# =============================================================================
# Test Fixtures
# =============================================================================


def create_mock_person(
    person_id: uuid.UUID,
    first_name: str = "Test",
    last_name: str = "Person",
    gender_id: uuid.UUID | None = None,
    birth_date: date = date(1990, 1, 1),
    death_date: date | None = None,
) -> Person:
    """Create a mock Person object."""
    if gender_id is None:
        gender_id = GENDER_DATA[GenderEnum.MALE].id
    return Person(
        id=person_id,
        user_id=None,
        created_by_user_id=uuid.uuid4(),
        first_name=first_name,
        last_name=last_name,
        gender_id=gender_id,
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


def create_basic_request(
    seeker_id: uuid.UUID,
    target_gender: str = "MALE",
    max_depth: int = 5,
) -> PartnerMatchRequest:
    """Create a basic partner match request."""
    return PartnerMatchRequest(
        seeker_person_id=seeker_id,
        target_gender_code=target_gender,
        max_depth=max_depth,
    )


# =============================================================================
# Tests for Seeker Validation (Requirements: 1.1, 1.2)
# =============================================================================


@pytest.mark.unit
class TestSeekerValidation:
    """Tests for seeker validation in find_matches method."""

    def test_seeker_not_found_returns_404(self, mock_session: MagicMock) -> None:
        """Test that non-existent seeker returns 404 error.

        Requirements: 1.1, 1.2
        """
        seeker_id = uuid.uuid4()
        request = create_basic_request(seeker_id)

        service = PartnerMatchService(mock_session)

        with patch.object(service, "_get_person", return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                service.find_matches(request)

        assert exc_info.value.status_code == 404
        assert "Seeker person not found" in exc_info.value.detail

    def test_valid_seeker_proceeds(self, mock_session: MagicMock) -> None:
        """Test that valid seeker proceeds with search.

        Requirements: 1.1
        """
        seeker_id = uuid.uuid4()
        mock_seeker = create_mock_person(seeker_id, "Seeker", "Person")
        request = create_basic_request(seeker_id)

        service = PartnerMatchService(mock_session)

        with patch.object(service, "_get_person", return_value=mock_seeker), patch.object(
            service, "_bfs_explore", return_value=({seeker_id: None}, {seeker_id: 0}, [])
        ), patch.object(
            service, "_build_exploration_tree", return_value={}
        ):
            result = service.find_matches(request)

        assert result.seeker_id == seeker_id


# =============================================================================
# Tests for Gender Filter (Requirements: 2.1)
# =============================================================================


@pytest.mark.unit
class TestGenderFilter:
    """Tests for _matches_gender method."""

    def test_matches_gender_male(self, mock_session: MagicMock) -> None:
        """Test gender matching for male.

        Requirements: 2.1
        """
        person_id = uuid.uuid4()
        male_gender_id = GENDER_DATA[GenderEnum.MALE].id
        mock_person = create_mock_person(person_id, gender_id=male_gender_id)

        service = PartnerMatchService(mock_session)
        result = service._matches_gender(mock_person, "MALE")

        assert result is True

    def test_matches_gender_female(self, mock_session: MagicMock) -> None:
        """Test gender matching for female.

        Requirements: 2.1
        """
        person_id = uuid.uuid4()
        female_gender_id = GENDER_DATA[GenderEnum.FEMALE].id
        mock_person = create_mock_person(person_id, gender_id=female_gender_id)

        service = PartnerMatchService(mock_session)
        result = service._matches_gender(mock_person, "FEMALE")

        assert result is True

    def test_gender_mismatch_returns_false(self, mock_session: MagicMock) -> None:
        """Test gender mismatch returns false.

        Requirements: 2.1
        """
        person_id = uuid.uuid4()
        male_gender_id = GENDER_DATA[GenderEnum.MALE].id
        mock_person = create_mock_person(person_id, gender_id=male_gender_id)

        service = PartnerMatchService(mock_session)
        result = service._matches_gender(mock_person, "FEMALE")

        assert result is False

    def test_invalid_gender_code_returns_400(self, mock_session: MagicMock) -> None:
        """Test invalid gender code returns 400 error.

        Requirements: 2.1
        """
        seeker_id = uuid.uuid4()
        mock_seeker = create_mock_person(seeker_id)
        request = PartnerMatchRequest(
            seeker_person_id=seeker_id,
            target_gender_code="INVALID",
            max_depth=5,
        )

        service = PartnerMatchService(mock_session)

        with patch.object(service, "_get_person", return_value=mock_seeker):
            with pytest.raises(HTTPException) as exc_info:
                service.find_matches(request)

        assert exc_info.value.status_code == 400
        assert "Invalid gender code" in exc_info.value.detail


# =============================================================================
# Tests for Birth Year Range Filter (Requirements: 3.1, 3.2)
# =============================================================================


@pytest.mark.unit
class TestBirthYearRangeFilter:
    """Tests for _in_birth_year_range method."""

    def test_birth_year_within_range(self, mock_session: MagicMock) -> None:
        """Test birth year within range returns true.

        Requirements: 3.1, 3.2
        """
        service = PartnerMatchService(mock_session)
        result = service._in_birth_year_range(1995, 1990, 2000)

        assert result is True

    def test_birth_year_at_min_boundary(self, mock_session: MagicMock) -> None:
        """Test birth year at min boundary returns true.

        Requirements: 3.1
        """
        service = PartnerMatchService(mock_session)
        result = service._in_birth_year_range(1990, 1990, 2000)

        assert result is True

    def test_birth_year_at_max_boundary(self, mock_session: MagicMock) -> None:
        """Test birth year at max boundary returns true.

        Requirements: 3.2
        """
        service = PartnerMatchService(mock_session)
        result = service._in_birth_year_range(2000, 1990, 2000)

        assert result is True

    def test_birth_year_below_min(self, mock_session: MagicMock) -> None:
        """Test birth year below min returns false.

        Requirements: 3.1
        """
        service = PartnerMatchService(mock_session)
        result = service._in_birth_year_range(1985, 1990, 2000)

        assert result is False

    def test_birth_year_above_max(self, mock_session: MagicMock) -> None:
        """Test birth year above max returns false.

        Requirements: 3.2
        """
        service = PartnerMatchService(mock_session)
        result = service._in_birth_year_range(2005, 1990, 2000)

        assert result is False

    def test_birth_year_none_returns_false(self, mock_session: MagicMock) -> None:
        """Test None birth year returns false.

        Requirements: 3.1, 3.2
        """
        service = PartnerMatchService(mock_session)
        result = service._in_birth_year_range(None, 1990, 2000)

        assert result is False

    def test_no_min_filter(self, mock_session: MagicMock) -> None:
        """Test no min filter allows any birth year.

        Requirements: 3.1
        """
        service = PartnerMatchService(mock_session)
        result = service._in_birth_year_range(1950, None, 2000)

        assert result is True

    def test_no_max_filter(self, mock_session: MagicMock) -> None:
        """Test no max filter allows any birth year.

        Requirements: 3.2
        """
        service = PartnerMatchService(mock_session)
        result = service._in_birth_year_range(2020, 1990, None)

        assert result is True


# =============================================================================
# Tests for Religion Filters (Requirements: 4.1, 5.1)
# =============================================================================


@pytest.mark.unit
class TestReligionFilters:
    """Tests for _passes_religion_filters method."""

    def test_religion_inclusion_passes(self, mock_session: MagicMock) -> None:
        """Test religion inclusion filter passes when matched.

        Requirements: 4.1
        """
        person_id = uuid.uuid4()
        religion_id = uuid.uuid4()

        service = PartnerMatchService(mock_session)

        request = PartnerMatchRequest(
            seeker_person_id=uuid.uuid4(),
            target_gender_code="MALE",
            include_religion_ids=[religion_id],
        )

        with patch.object(
            service,
            "_get_person_religion_ids",
            return_value=PersonReligionIds(religion_id=religion_id),
        ):
            result = service._passes_religion_filters(person_id, request)

        assert result is True

    def test_religion_inclusion_fails(self, mock_session: MagicMock) -> None:
        """Test religion inclusion filter fails when not matched.

        Requirements: 4.1
        """
        person_id = uuid.uuid4()
        religion_id = uuid.uuid4()
        other_religion_id = uuid.uuid4()

        service = PartnerMatchService(mock_session)

        request = PartnerMatchRequest(
            seeker_person_id=uuid.uuid4(),
            target_gender_code="MALE",
            include_religion_ids=[religion_id],
        )

        with patch.object(
            service,
            "_get_person_religion_ids",
            return_value=PersonReligionIds(religion_id=other_religion_id),
        ):
            result = service._passes_religion_filters(person_id, request)

        assert result is False

    def test_gotra_exclusion_filters_out(self, mock_session: MagicMock) -> None:
        """Test gotra exclusion filter excludes matching sub-category.

        Requirements: 5.1
        """
        person_id = uuid.uuid4()
        gotra_id = uuid.uuid4()

        service = PartnerMatchService(mock_session)

        request = PartnerMatchRequest(
            seeker_person_id=uuid.uuid4(),
            target_gender_code="MALE",
            exclude_sub_category_ids=[gotra_id],
        )

        with patch.object(
            service,
            "_get_person_religion_ids",
            return_value=PersonReligionIds(sub_category_id=gotra_id),
        ):
            result = service._passes_religion_filters(person_id, request)

        assert result is False

    def test_gotra_exclusion_passes_different_gotra(
        self, mock_session: MagicMock
    ) -> None:
        """Test gotra exclusion passes for different sub-category.

        Requirements: 5.1
        """
        person_id = uuid.uuid4()
        excluded_gotra_id = uuid.uuid4()
        person_gotra_id = uuid.uuid4()

        service = PartnerMatchService(mock_session)

        request = PartnerMatchRequest(
            seeker_person_id=uuid.uuid4(),
            target_gender_code="MALE",
            exclude_sub_category_ids=[excluded_gotra_id],
        )

        with patch.object(
            service,
            "_get_person_religion_ids",
            return_value=PersonReligionIds(sub_category_id=person_gotra_id),
        ):
            result = service._passes_religion_filters(person_id, request)

        assert result is True


# =============================================================================
# Tests for Living Person Filter (Requirements: 6.1)
# =============================================================================


@pytest.mark.unit
class TestLivingPersonFilter:
    """Tests for living person filter in _is_eligible_match."""

    def test_living_person_passes(self, mock_session: MagicMock) -> None:
        """Test living person passes filter.

        Requirements: 6.1
        """
        person_id = uuid.uuid4()
        mock_person = create_mock_person(
            person_id,
            gender_id=GENDER_DATA[GenderEnum.FEMALE].id,
            death_date=None,
        )

        service = PartnerMatchService(mock_session)
        request = create_basic_request(uuid.uuid4(), target_gender="FEMALE")

        with patch.object(service, "_get_person", return_value=mock_person), patch.object(
            service, "_passes_religion_filters", return_value=True
        ), patch.object(
            service, "_is_married_or_has_children", return_value=False
        ):
            result = service._is_eligible_match(person_id, request)

        assert result is True

    def test_deceased_person_fails(self, mock_session: MagicMock) -> None:
        """Test deceased person fails filter.

        Requirements: 6.1
        """
        person_id = uuid.uuid4()
        mock_person = create_mock_person(
            person_id,
            gender_id=GENDER_DATA[GenderEnum.FEMALE].id,
            death_date=date(2020, 1, 1),
        )

        service = PartnerMatchService(mock_session)
        request = create_basic_request(uuid.uuid4(), target_gender="FEMALE")

        with patch.object(service, "_get_person", return_value=mock_person):
            result = service._is_eligible_match(person_id, request)

        assert result is False


# =============================================================================
# Tests for Marital Status Filter (Requirements: 7.1, 7.2)
# =============================================================================


@pytest.mark.unit
class TestMaritalStatusFilter:
    """Tests for _is_married_or_has_children method."""

    def test_unmarried_no_children_returns_false(
        self, mock_session: MagicMock
    ) -> None:
        """Test unmarried person without children returns false.

        Requirements: 7.1, 7.2
        """
        person_id = uuid.uuid4()

        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.exec.return_value = mock_result

        service = PartnerMatchService(mock_session)
        result = service._is_married_or_has_children(person_id)

        assert result is False

    def test_married_with_wife_returns_true(self, mock_session: MagicMock) -> None:
        """Test person with wife relationship returns true.

        Requirements: 7.1
        """
        person_id = uuid.uuid4()
        wife_id = uuid.uuid4()

        wife_rel = create_mock_relationship(
            person_id, wife_id, RelationshipType.WIFE, is_active=True
        )

        mock_result = MagicMock()
        mock_result.all.return_value = [wife_rel]
        mock_session.exec.return_value = mock_result

        service = PartnerMatchService(mock_session)
        result = service._is_married_or_has_children(person_id)

        assert result is True

    def test_married_with_husband_returns_true(self, mock_session: MagicMock) -> None:
        """Test person with husband relationship returns true.

        Requirements: 7.1
        """
        person_id = uuid.uuid4()
        husband_id = uuid.uuid4()

        husband_rel = create_mock_relationship(
            person_id, husband_id, RelationshipType.HUSBAND, is_active=True
        )

        mock_result = MagicMock()
        mock_result.all.return_value = [husband_rel]
        mock_session.exec.return_value = mock_result

        service = PartnerMatchService(mock_session)
        result = service._is_married_or_has_children(person_id)

        assert result is True

    def test_has_son_returns_true(self, mock_session: MagicMock) -> None:
        """Test person with son relationship returns true.

        Requirements: 7.2
        """
        person_id = uuid.uuid4()
        son_id = uuid.uuid4()

        son_rel = create_mock_relationship(
            person_id, son_id, RelationshipType.SON, is_active=True
        )

        mock_result = MagicMock()
        mock_result.all.return_value = [son_rel]
        mock_session.exec.return_value = mock_result

        service = PartnerMatchService(mock_session)
        result = service._is_married_or_has_children(person_id)

        assert result is True

    def test_has_daughter_returns_true(self, mock_session: MagicMock) -> None:
        """Test person with daughter relationship returns true.

        Requirements: 7.2
        """
        person_id = uuid.uuid4()
        daughter_id = uuid.uuid4()

        daughter_rel = create_mock_relationship(
            person_id, daughter_id, RelationshipType.DAUGHTER, is_active=True
        )

        mock_result = MagicMock()
        mock_result.all.return_value = [daughter_rel]
        mock_session.exec.return_value = mock_result

        service = PartnerMatchService(mock_session)
        result = service._is_married_or_has_children(person_id)

        assert result is True

    def test_parent_relationship_does_not_count(
        self, mock_session: MagicMock
    ) -> None:
        """Test parent relationships (FATHER, MOTHER) don't count as married.

        Requirements: 7.1, 7.2
        """
        person_id = uuid.uuid4()
        father_id = uuid.uuid4()

        father_rel = create_mock_relationship(
            person_id, father_id, RelationshipType.FATHER, is_active=True
        )

        mock_result = MagicMock()
        mock_result.all.return_value = [father_rel]
        mock_session.exec.return_value = mock_result

        service = PartnerMatchService(mock_session)
        result = service._is_married_or_has_children(person_id)

        assert result is False


# =============================================================================
# Tests for Graph Structure (Requirements: 8.3, 8.4)
# =============================================================================


@pytest.mark.unit
class TestGraphStructure:
    """Tests for _build_exploration_tree method."""

    def test_seeker_node_has_null_from_person(self, mock_session: MagicMock) -> None:
        """Test seeker node has from_person as null.

        Requirements: 8.3
        """
        seeker_id = uuid.uuid4()
        parent_map = {seeker_id: None}
        depth_map = {seeker_id: 0}
        matches: list[uuid.UUID] = []

        service = PartnerMatchService(mock_session)

        from app.schemas.partner_match import MatchGraphNode

        mock_node = MatchGraphNode(
            person_id=seeker_id,
            first_name="Seeker",
            last_name="Person",
            is_match=False,
            depth=0,
        )

        with patch.object(service, "_enrich_node_data", return_value=mock_node):
            result = service._build_exploration_tree(
                parent_map, depth_map, matches, seeker_id
            )

        assert seeker_id in result
        assert result[seeker_id].from_person is None
        assert result[seeker_id].depth == 0

    def test_child_node_has_from_person_set(self, mock_session: MagicMock) -> None:
        """Test child node has from_person pointing to parent.

        Requirements: 8.3
        """
        seeker_id = uuid.uuid4()
        child_id = uuid.uuid4()
        parent_map = {seeker_id: None, child_id: seeker_id}
        depth_map = {seeker_id: 0, child_id: 1}
        matches: list[uuid.UUID] = []

        service = PartnerMatchService(mock_session)

        from app.schemas.partner_match import MatchGraphNode

        def mock_enrich(pid: uuid.UUID) -> MatchGraphNode:
            return MatchGraphNode(
                person_id=pid,
                first_name="Test",
                last_name="Person",
                is_match=False,
                depth=0,
            )

        with patch.object(
            service, "_enrich_node_data", side_effect=mock_enrich
        ), patch.object(service, "_get_relationship_type", return_value="Father"):
            result = service._build_exploration_tree(
                parent_map, depth_map, matches, seeker_id
            )

        assert child_id in result
        assert result[child_id].from_person is not None
        assert result[child_id].from_person.person_id == seeker_id

    def test_parent_node_has_to_persons_set(self, mock_session: MagicMock) -> None:
        """Test parent node has to_persons list populated.

        Requirements: 8.4
        """
        seeker_id = uuid.uuid4()
        child_id = uuid.uuid4()
        parent_map = {seeker_id: None, child_id: seeker_id}
        depth_map = {seeker_id: 0, child_id: 1}
        matches: list[uuid.UUID] = []

        service = PartnerMatchService(mock_session)

        from app.schemas.partner_match import MatchGraphNode

        def mock_enrich(pid: uuid.UUID) -> MatchGraphNode:
            return MatchGraphNode(
                person_id=pid,
                first_name="Test",
                last_name="Person",
                is_match=False,
                depth=0,
            )

        with patch.object(
            service, "_enrich_node_data", side_effect=mock_enrich
        ), patch.object(service, "_get_relationship_type", return_value="Son"):
            result = service._build_exploration_tree(
                parent_map, depth_map, matches, seeker_id
            )

        assert seeker_id in result
        assert len(result[seeker_id].to_persons) == 1
        assert result[seeker_id].to_persons[0].person_id == child_id

    def test_match_flag_set_correctly(self, mock_session: MagicMock) -> None:
        """Test is_match flag is set for eligible matches.

        Requirements: 8.3
        """
        seeker_id = uuid.uuid4()
        match_id = uuid.uuid4()
        non_match_id = uuid.uuid4()
        parent_map = {seeker_id: None, match_id: seeker_id, non_match_id: seeker_id}
        depth_map = {seeker_id: 0, match_id: 1, non_match_id: 1}
        matches = [match_id]

        service = PartnerMatchService(mock_session)

        from app.schemas.partner_match import MatchGraphNode

        def mock_enrich(pid: uuid.UUID) -> MatchGraphNode:
            return MatchGraphNode(
                person_id=pid,
                first_name="Test",
                last_name="Person",
                is_match=False,
                depth=0,
            )

        with patch.object(
            service, "_enrich_node_data", side_effect=mock_enrich
        ), patch.object(service, "_get_relationship_type", return_value="Related"):
            result = service._build_exploration_tree(
                parent_map, depth_map, matches, seeker_id
            )

        assert result[match_id].is_match is True
        assert result[non_match_id].is_match is False
        assert result[seeker_id].is_match is False


# =============================================================================
# Tests for BFS Exploration (Requirements: 1.3, 10.1)
# =============================================================================


@pytest.mark.unit
class TestBFSExploration:
    """Tests for _bfs_explore method."""

    def test_bfs_respects_max_depth(self, mock_session: MagicMock) -> None:
        """Test BFS respects max_depth limit.

        Requirements: 1.3, 10.1
        """
        seeker_id = uuid.uuid4()
        level1_id = uuid.uuid4()
        level2_id = uuid.uuid4()
        level3_id = uuid.uuid4()

        relationships_map = {
            seeker_id: [level1_id],
            level1_id: [seeker_id, level2_id],
            level2_id: [level1_id, level3_id],
            level3_id: [level2_id],
        }

        service = PartnerMatchService(mock_session)
        request = create_basic_request(seeker_id, max_depth=2)

        def mock_get_relationships(pid: uuid.UUID) -> list[uuid.UUID]:
            return relationships_map.get(pid, [])

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ), patch.object(service, "_is_eligible_match", return_value=False):
            parent_map, depth_map, matches = service._bfs_explore(
                seeker_id, max_depth=2, request=request
            )

        # Should visit seeker (depth 0), level1 (depth 1), level2 (depth 2)
        # Should NOT visit level3 (depth 3)
        assert seeker_id in parent_map
        assert level1_id in parent_map
        assert level2_id in parent_map
        assert level3_id not in parent_map

    def test_bfs_finds_matches(self, mock_session: MagicMock) -> None:
        """Test BFS correctly identifies matches.

        Requirements: 1.3
        """
        seeker_id = uuid.uuid4()
        match_id = uuid.uuid4()

        relationships_map = {
            seeker_id: [match_id],
            match_id: [seeker_id],
        }

        service = PartnerMatchService(mock_session)
        request = create_basic_request(seeker_id)

        def mock_get_relationships(pid: uuid.UUID) -> list[uuid.UUID]:
            return relationships_map.get(pid, [])

        def mock_is_eligible(pid: uuid.UUID, req: PartnerMatchRequest) -> bool:
            return pid == match_id

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ), patch.object(service, "_is_eligible_match", side_effect=mock_is_eligible):
            parent_map, depth_map, matches = service._bfs_explore(
                seeker_id, max_depth=5, request=request
            )

        assert match_id in matches
        assert seeker_id not in matches

    def test_bfs_tracks_depth_correctly(self, mock_session: MagicMock) -> None:
        """Test BFS tracks depth correctly for each node.

        Requirements: 10.1
        """
        seeker_id = uuid.uuid4()
        level1_id = uuid.uuid4()
        level2_id = uuid.uuid4()

        relationships_map = {
            seeker_id: [level1_id],
            level1_id: [seeker_id, level2_id],
            level2_id: [level1_id],
        }

        service = PartnerMatchService(mock_session)
        request = create_basic_request(seeker_id)

        def mock_get_relationships(pid: uuid.UUID) -> list[uuid.UUID]:
            return relationships_map.get(pid, [])

        with patch.object(
            service, "_get_relationships", side_effect=mock_get_relationships
        ), patch.object(service, "_is_eligible_match", return_value=False):
            parent_map, depth_map, matches = service._bfs_explore(
                seeker_id, max_depth=5, request=request
            )

        assert depth_map[seeker_id] == 0
        assert depth_map[level1_id] == 1
        assert depth_map[level2_id] == 2

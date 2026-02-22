"""Unit tests for RelationshipTypeHelper utility class."""

import uuid

import pytest

from app.enums import RelationshipType
from app.utils.relationship_helper import RelationshipTypeHelper


class TestGetInverseType:
    """Test suite for RelationshipTypeHelper.get_inverse_type() method."""

    @pytest.fixture
    def gender_mapping(self) -> dict[uuid.UUID, str]:
        """Create a mock gender mapping for tests."""
        male_id = uuid.uuid4()
        female_id = uuid.uuid4()
        return {
            male_id: "male",
            female_id: "female",
        }

    @pytest.fixture
    def male_gender_id(self, gender_mapping: dict[uuid.UUID, str]) -> uuid.UUID:
        """Get the male gender ID from the mapping."""
        return next(k for k, v in gender_mapping.items() if v == "male")

    @pytest.fixture
    def female_gender_id(self, gender_mapping: dict[uuid.UUID, str]) -> uuid.UUID:
        """Get the female gender ID from the mapping."""
        return next(k for k, v in gender_mapping.items() if v == "female")

    # Parent → Child relationships (Father/Mother)
    def test_father_with_male_person_returns_son(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: A → B as Father (B is A's father) + A is male → B → A as Son.
        
        When a male person (A) creates a Father relationship with person B,
        the inverse should be Son (A is B's son).
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.FATHER,
            person_gender_id=male_gender_id,  # A is male
            related_person_gender_id=female_gender_id,  # B's gender (doesn't matter)
            gender_mapping=gender_mapping,
        )
        assert result == RelationshipType.SON

    def test_father_with_female_person_returns_daughter(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: A → B as Father (B is A's father) + A is female → B → A as Daughter.
        
        When a female person (A) creates a Father relationship with person B,
        the inverse should be Daughter (A is B's daughter).
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.FATHER,
            person_gender_id=female_gender_id,  # A is female
            related_person_gender_id=male_gender_id,  # B's gender (doesn't matter)
            gender_mapping=gender_mapping,
        )
        assert result == RelationshipType.DAUGHTER

    def test_mother_with_male_person_returns_son(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: A → B as Mother (B is A's mother) + A is male → B → A as Son.
        
        When a male person (A) creates a Mother relationship with person B,
        the inverse should be Son (A is B's son).
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.MOTHER,
            person_gender_id=male_gender_id,  # A is male
            related_person_gender_id=female_gender_id,  # B's gender (doesn't matter)
            gender_mapping=gender_mapping,
        )
        assert result == RelationshipType.SON

    def test_mother_with_female_person_returns_daughter(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: A → B as Mother (B is A's mother) + A is female → B → A as Daughter.
        
        When a female person (A) creates a Mother relationship with person B,
        the inverse should be Daughter (A is B's daughter).
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.MOTHER,
            person_gender_id=female_gender_id,  # A is female
            related_person_gender_id=male_gender_id,  # B's gender (doesn't matter)
            gender_mapping=gender_mapping,
        )
        assert result == RelationshipType.DAUGHTER

    # Child → Parent relationships (Son/Daughter)
    def test_son_with_male_person_returns_father(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: A → B as Son (B is A's son) + A is male → B → A as Father.
        
        When a male person (A) creates a Son relationship with person B,
        the inverse should be Father (A is B's father).
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.SON,
            person_gender_id=male_gender_id,  # A is male
            related_person_gender_id=male_gender_id,  # B's gender (doesn't matter)
            gender_mapping=gender_mapping,
        )
        assert result == RelationshipType.FATHER

    def test_son_with_female_person_returns_mother(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: A → B as Son (B is A's son) + A is female → B → A as Mother.
        
        When a female person (A) creates a Son relationship with person B,
        the inverse should be Mother (A is B's mother).
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.SON,
            person_gender_id=female_gender_id,  # A is female
            related_person_gender_id=male_gender_id,  # B's gender (doesn't matter)
            gender_mapping=gender_mapping,
        )
        assert result == RelationshipType.MOTHER

    def test_daughter_with_male_person_returns_father(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: A → B as Daughter (B is A's daughter) + A is male → B → A as Father.
        
        When a male person (A) creates a Daughter relationship with person B,
        the inverse should be Father (A is B's father).
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.DAUGHTER,
            person_gender_id=male_gender_id,  # A is male
            related_person_gender_id=female_gender_id,  # B's gender (doesn't matter)
            gender_mapping=gender_mapping,
        )
        assert result == RelationshipType.FATHER

    def test_daughter_with_female_person_returns_mother(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: A → B as Daughter (B is A's daughter) + A is female → B → A as Mother.
        
        When a female person (A) creates a Daughter relationship with person B,
        the inverse should be Mother (A is B's mother).
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.DAUGHTER,
            person_gender_id=female_gender_id,  # A is female
            related_person_gender_id=male_gender_id,  # B's gender (doesn't matter)
            gender_mapping=gender_mapping,
        )
        assert result == RelationshipType.MOTHER

    # Spouse relationships (gender-independent)
    def test_husband_returns_wife(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: A → B as Husband (B is A's husband) → B → A as Wife.
        
        When person A creates a Husband relationship with person B,
        the inverse should be Wife (A is B's wife).
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.HUSBAND,
            person_gender_id=female_gender_id,  # Gender doesn't matter for spouse
            related_person_gender_id=male_gender_id,
            gender_mapping=gender_mapping,
        )
        assert result == RelationshipType.WIFE

    def test_wife_returns_husband(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: A → B as Wife (B is A's wife) → B → A as Husband.
        
        When person A creates a Wife relationship with person B,
        the inverse should be Husband (A is B's husband).
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.WIFE,
            person_gender_id=male_gender_id,  # Gender doesn't matter for spouse
            related_person_gender_id=female_gender_id,
            gender_mapping=gender_mapping,
        )
        assert result == RelationshipType.HUSBAND

    def test_spouse_returns_spouse(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: A → B as Spouse (B is A's spouse) → B → A as Spouse.
        
        When person A creates a Spouse relationship with person B,
        the inverse should be Spouse (A is B's spouse).
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.SPOUSE,
            person_gender_id=male_gender_id,  # Gender doesn't matter for spouse
            related_person_gender_id=female_gender_id,
            gender_mapping=gender_mapping,
        )
        assert result == RelationshipType.SPOUSE

    # Edge cases
    def test_unknown_gender_returns_none(
        self,
        male_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """
        Test: Unknown gender returns None.
        
        When the person's gender is not in the mapping,
        the method should return None for parent-child relationships.
        """
        unknown_gender_id = uuid.uuid4()  # Not in mapping
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.FATHER,
            person_gender_id=unknown_gender_id,  # Unknown gender
            related_person_gender_id=male_gender_id,
            gender_mapping=gender_mapping,
        )
        assert result is None

    def test_empty_gender_mapping_returns_none(
        self,
        male_gender_id: uuid.UUID,
        female_gender_id: uuid.UUID,
    ):
        """
        Test: Empty gender mapping returns None.
        
        When the gender mapping is empty,
        the method should return None for parent-child relationships.
        """
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.FATHER,
            person_gender_id=male_gender_id,
            related_person_gender_id=female_gender_id,
            gender_mapping={},  # Empty mapping
        )
        assert result is None


class TestGetInverseTypeEdgeCases:
    """Additional edge case tests for get_inverse_type."""

    @pytest.fixture
    def gender_mapping(self) -> dict[uuid.UUID, str]:
        """Create a mock gender mapping for tests."""
        male_id = uuid.uuid4()
        female_id = uuid.uuid4()
        return {
            male_id: "male",
            female_id: "female",
        }

    @pytest.fixture
    def male_gender_id(self, gender_mapping: dict[uuid.UUID, str]) -> uuid.UUID:
        """Get the male gender ID from the mapping."""
        return next(k for k, v in gender_mapping.items() if v == "male")

    @pytest.fixture
    def female_gender_id(self, gender_mapping: dict[uuid.UUID, str]) -> uuid.UUID:
        """Get the female gender ID from the mapping."""
        return next(k for k, v in gender_mapping.items() if v == "female")

    def test_mother_with_unknown_gender_returns_none(
        self,
        male_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """Test Mother relationship with unknown person gender returns None."""
        unknown_gender_id = uuid.uuid4()
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.MOTHER,
            person_gender_id=unknown_gender_id,
            related_person_gender_id=male_gender_id,
            gender_mapping=gender_mapping,
        )
        assert result is None

    def test_son_with_unknown_gender_returns_none(
        self,
        male_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """Test Son relationship with unknown person gender returns None."""
        unknown_gender_id = uuid.uuid4()
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.SON,
            person_gender_id=unknown_gender_id,
            related_person_gender_id=male_gender_id,
            gender_mapping=gender_mapping,
        )
        assert result is None

    def test_daughter_with_unknown_gender_returns_none(
        self,
        male_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """Test Daughter relationship with unknown person gender returns None."""
        unknown_gender_id = uuid.uuid4()
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.DAUGHTER,
            person_gender_id=unknown_gender_id,
            related_person_gender_id=male_gender_id,
            gender_mapping=gender_mapping,
        )
        assert result is None

    def test_case_insensitive_gender_matching(
        self,
        gender_mapping: dict[uuid.UUID, str],
    ):
        """Test that gender matching is case-insensitive."""
        # Create mapping with uppercase gender
        male_id = uuid.uuid4()
        female_id = uuid.uuid4()
        uppercase_mapping = {
            male_id: "MALE",
            female_id: "FEMALE",
        }
        
        result = RelationshipTypeHelper.get_inverse_type(
            relationship_type=RelationshipType.FATHER,
            person_gender_id=male_id,
            related_person_gender_id=female_id,
            gender_mapping=uppercase_mapping,
        )
        assert result == RelationshipType.SON


class TestGetGenderMapping:
    """Test suite for RelationshipTypeHelper.get_gender_mapping() method."""

    def test_get_gender_mapping_returns_dict(self):
        """Test that get_gender_mapping returns a dictionary."""
        result = RelationshipTypeHelper.get_gender_mapping()
        assert isinstance(result, dict)

    def test_get_gender_mapping_contains_male_and_female(self):
        """Test that get_gender_mapping contains male and female genders."""
        result = RelationshipTypeHelper.get_gender_mapping()
        values = [v.lower() for v in result.values()]
        assert "male" in values
        assert "female" in values

    def test_get_gender_mapping_with_session_parameter(self):
        """Test that get_gender_mapping accepts session parameter for compatibility."""
        # Session parameter is kept for API compatibility but not used
        result = RelationshipTypeHelper.get_gender_mapping(session=None)
        assert isinstance(result, dict)


class TestRequiresGenderContext:
    """Test suite for RelationshipTypeHelper.requires_gender_context() method."""

    def test_father_requires_gender_context(self):
        """Test that Father relationship requires gender context."""
        result = RelationshipTypeHelper.requires_gender_context(RelationshipType.FATHER)
        assert result is True

    def test_mother_requires_gender_context(self):
        """Test that Mother relationship requires gender context."""
        result = RelationshipTypeHelper.requires_gender_context(RelationshipType.MOTHER)
        assert result is True

    def test_son_requires_gender_context(self):
        """Test that Son relationship requires gender context."""
        result = RelationshipTypeHelper.requires_gender_context(RelationshipType.SON)
        assert result is True

    def test_daughter_requires_gender_context(self):
        """Test that Daughter relationship requires gender context."""
        result = RelationshipTypeHelper.requires_gender_context(RelationshipType.DAUGHTER)
        assert result is True

    def test_husband_does_not_require_gender_context(self):
        """Test that Husband relationship does not require gender context."""
        result = RelationshipTypeHelper.requires_gender_context(RelationshipType.HUSBAND)
        assert result is False

    def test_wife_does_not_require_gender_context(self):
        """Test that Wife relationship does not require gender context."""
        result = RelationshipTypeHelper.requires_gender_context(RelationshipType.WIFE)
        assert result is False

    def test_spouse_does_not_require_gender_context(self):
        """Test that Spouse relationship does not require gender context."""
        result = RelationshipTypeHelper.requires_gender_context(RelationshipType.SPOUSE)
        assert result is False

"""Unit tests for PersonRepository."""

import uuid
from datetime import date
from unittest.mock import MagicMock

import pytest
from sqlmodel import Session, select

from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.models import User
from app.repositories.person.person_repository import PersonRepository


# ============================================================================
# Unit Tests (Mocked)
# ============================================================================


@pytest.mark.unit
class TestPersonRepositoryGetByUserId:
    """Unit tests for get_by_user_id method."""

    def test_get_by_user_id_returns_person_when_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_user_id returns person when exists."""
        repo = PersonRepository(mock_session)
        user_id = uuid.uuid4()
        expected_person = Person(
            id=uuid.uuid4(),
            user_id=user_id,
            created_by_user_id=user_id,
            is_primary=True,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 1),
        )
        mock_session.exec.return_value.first.return_value = expected_person

        result = repo.get_by_user_id(user_id)

        assert result == expected_person
        mock_session.exec.assert_called_once()

    def test_get_by_user_id_returns_none_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_user_id returns None when no person exists."""
        repo = PersonRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_by_user_id(uuid.uuid4())

        assert result is None


@pytest.mark.unit
class TestPersonRepositoryUserHasPerson:
    """Unit tests for user_has_person method."""

    def test_user_has_person_returns_true_when_exists(
        self, mock_session: MagicMock
    ) -> None:
        """Test user_has_person returns True when person exists."""
        repo = PersonRepository(mock_session)
        user_id = uuid.uuid4()
        mock_session.exec.return_value.first.return_value = Person(
            id=uuid.uuid4(),
            user_id=user_id,
            created_by_user_id=user_id,
            is_primary=True,
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 1),
        )

        result = repo.user_has_person(user_id)

        assert result is True

    def test_user_has_person_returns_false_when_not_exists(
        self, mock_session: MagicMock
    ) -> None:
        """Test user_has_person returns False when no person exists."""
        repo = PersonRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.user_has_person(uuid.uuid4())

        assert result is False


@pytest.mark.unit
class TestPersonRepositoryGetByCreatorUnit:
    """Unit tests for get_by_creator method."""

    def test_get_by_creator_returns_list(self, mock_session: MagicMock) -> None:
        """Test get_by_creator returns list of persons."""
        repo = PersonRepository(mock_session)
        creator_id = uuid.uuid4()
        persons = [
            Person(
                id=uuid.uuid4(),
                user_id=creator_id,
                created_by_user_id=creator_id,
                is_primary=True,
                first_name="John",
                last_name="Doe",
                gender_id=uuid.uuid4(),
                date_of_birth=date(1990, 1, 1),
            ),
            Person(
                id=uuid.uuid4(),
                user_id=None,
                created_by_user_id=creator_id,
                is_primary=False,
                first_name="Jane",
                last_name="Doe",
                gender_id=uuid.uuid4(),
                date_of_birth=date(1960, 1, 1),
            ),
        ]
        mock_session.exec.return_value.all.return_value = persons

        result = repo.get_by_creator(creator_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_by_creator_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_creator returns empty list when no persons."""
        repo = PersonRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_creator(uuid.uuid4())

        assert result == []


# ============================================================================
# Integration Tests (Real Database)
# ============================================================================


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        hashed_password="test_password",
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def another_test_user(db: Session) -> User:
    """Create another test user."""
    user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        hashed_password="test_password",
        is_active=True,
        is_superuser=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def male_gender(db: Session) -> Gender:
    """Get or create male gender."""
    gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
    if not gender:
        gender = Gender(
            id=uuid.uuid4(),
            name="Male",
            code="MALE",
            description="Male gender",
            is_active=True
        )
        db.add(gender)
        db.commit()
        db.refresh(gender)
    return gender


@pytest.mark.integration
class TestGetByCreator:
    """Tests for get_by_creator method."""

    def test_get_by_creator_with_no_persons(
        self, db: Session, test_user: User
    ) -> None:
        """Test get_by_creator with user who created no persons."""
        repo = PersonRepository(db)
        
        # Test with user who has created no persons
        result = repo.get_by_creator(test_user.id)
        
        assert result == []
        assert len(result) == 0

    def test_get_by_creator_with_multiple_persons(
        self, db: Session, test_user: User, male_gender: Gender
    ) -> None:
        """Test get_by_creator with user who created multiple persons."""
        repo = PersonRepository(db)
        
        # Create multiple persons by the same user
        person1 = Person(
            user_id=test_user.id,
            created_by_user_id=test_user.id,
            is_primary=True,
            first_name="John",
            last_name="Doe",
            gender_id=male_gender.id,
            date_of_birth=date(1990, 1, 1),
        )
        person2 = Person(
            user_id=None,
            created_by_user_id=test_user.id,
            is_primary=False,
            first_name="Jane",
            last_name="Doe",
            gender_id=male_gender.id,
            date_of_birth=date(1960, 1, 1),
        )
        person3 = Person(
            user_id=None,
            created_by_user_id=test_user.id,
            is_primary=False,
            first_name="Bob",
            last_name="Smith",
            gender_id=male_gender.id,
            date_of_birth=date(1985, 5, 15),
        )
        
        db.add(person1)
        db.add(person2)
        db.add(person3)
        db.commit()
        
        # Test retrieval
        result = repo.get_by_creator(test_user.id)
        
        assert len(result) == 3
        # Verify all returned persons have the correct creator
        for person in result:
            assert person.created_by_user_id == test_user.id
        
        # Clean up
        db.delete(person1)
        db.delete(person2)
        db.delete(person3)
        db.commit()

    def test_get_by_creator_only_returns_creator_persons(
        self, db: Session, test_user: User, another_test_user: User, male_gender: Gender
    ) -> None:
        """Test that only persons by that creator are returned."""
        repo = PersonRepository(db)
        
        # Create persons by first user
        person1 = Person(
            user_id=test_user.id,
            created_by_user_id=test_user.id,
            is_primary=True,
            first_name="John",
            last_name="Doe",
            gender_id=male_gender.id,
            date_of_birth=date(1990, 1, 1),
        )
        person2 = Person(
            user_id=None,
            created_by_user_id=test_user.id,
            is_primary=False,
            first_name="Jane",
            last_name="Doe",
            gender_id=male_gender.id,
            date_of_birth=date(1960, 1, 1),
        )
        
        # Create persons by second user
        person3 = Person(
            user_id=another_test_user.id,
            created_by_user_id=another_test_user.id,
            is_primary=True,
            first_name="Alice",
            last_name="Smith",
            gender_id=male_gender.id,
            date_of_birth=date(1985, 5, 15),
        )
        person4 = Person(
            user_id=None,
            created_by_user_id=another_test_user.id,
            is_primary=False,
            first_name="Bob",
            last_name="Smith",
            gender_id=male_gender.id,
            date_of_birth=date(1980, 3, 20),
        )
        
        db.add(person1)
        db.add(person2)
        db.add(person3)
        db.add(person4)
        db.commit()
        
        # Test retrieval for first user
        result = repo.get_by_creator(test_user.id)
        
        assert len(result) == 2
        # Verify all returned persons have the correct creator
        for person in result:
            assert person.created_by_user_id == test_user.id
        
        # Verify the correct persons are returned
        returned_ids = {person.id for person in result}
        assert person1.id in returned_ids
        assert person2.id in returned_ids
        assert person3.id not in returned_ids
        assert person4.id not in returned_ids
        
        # Clean up
        db.delete(person1)
        db.delete(person2)
        db.delete(person3)
        db.delete(person4)
        db.commit()


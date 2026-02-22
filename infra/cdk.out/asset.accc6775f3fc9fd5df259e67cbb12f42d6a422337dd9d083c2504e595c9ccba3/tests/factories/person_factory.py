"""Person factory for creating test Person entities."""

import uuid
from datetime import date, datetime
from typing import Any

from sqlmodel import Session

from app.db_models.person.person import Person
from app.db_models.user import User
from app.enums import GENDER_DATA, GenderEnum


class PersonFactory:
    """Factory for creating Person test entities."""

    _counter = 0

    @classmethod
    def _get_unique_suffix(cls) -> str:
        """Generate a unique suffix for test data."""
        cls._counter += 1
        return f"{cls._counter}"

    @classmethod
    def get_default_gender_id(cls, gender: GenderEnum = GenderEnum.MALE) -> uuid.UUID:
        """Get the default gender ID from enum data."""
        return GENDER_DATA[gender].id

    @classmethod
    def create(
        cls,
        session: Session,
        *,
        created_by_user: User,
        user: User | None = None,
        first_name: str | None = None,
        middle_name: str | None = None,
        last_name: str | None = None,
        gender_id: uuid.UUID | None = None,
        gender: GenderEnum = GenderEnum.MALE,
        date_of_birth: date | None = None,
        date_of_death: date | None = None,
        is_primary: bool = False,
        commit: bool = True,
    ) -> Person:
        """Create a Person entity with sensible defaults.

        Args:
            session: Database session
            created_by_user: User who created this person record
            user: Optional user account linked to this person
            first_name: First name (auto-generated if not provided)
            middle_name: Middle name
            last_name: Last name (auto-generated if not provided)
            gender_id: Gender UUID (uses gender enum if not provided)
            gender: Gender enum (used if gender_id not provided)
            date_of_birth: Date of birth (defaults to 1990-01-01)
            date_of_death: Date of death
            is_primary: Whether this is the primary person for the user
            commit: Whether to commit the transaction

        Returns:
            Created Person entity
        """
        suffix = cls._get_unique_suffix()

        if first_name is None:
            first_name = f"TestFirst{suffix}"
        if last_name is None:
            last_name = f"TestLast{suffix}"
        if gender_id is None:
            gender_id = cls.get_default_gender_id(gender)
        if date_of_birth is None:
            date_of_birth = date(1990, 1, 1)

        person = Person(
            user_id=user.id if user else None,
            created_by_user_id=created_by_user.id,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            gender_id=gender_id,
            date_of_birth=date_of_birth,
            date_of_death=date_of_death,
            is_primary=is_primary,
        )

        session.add(person)
        if commit:
            session.commit()
            session.refresh(person)

        return person

    @classmethod
    def create_with_user(
        cls,
        session: Session,
        user: User,
        *,
        is_primary: bool = True,
        **kwargs: Any,
    ) -> Person:
        """Create a Person linked to a User account.

        Args:
            session: Database session
            user: User to link the person to
            is_primary: Whether this is the primary person for the user
            **kwargs: Additional arguments passed to create()

        Returns:
            Created Person entity linked to the user
        """
        return cls.create(
            session,
            created_by_user=user,
            user=user,
            is_primary=is_primary,
            **kwargs,
        )

    @classmethod
    def build(
        cls,
        *,
        created_by_user_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
        first_name: str | None = None,
        middle_name: str | None = None,
        last_name: str | None = None,
        gender_id: uuid.UUID | None = None,
        gender: GenderEnum = GenderEnum.MALE,
        date_of_birth: date | None = None,
        date_of_death: date | None = None,
        is_primary: bool = False,
    ) -> Person:
        """Build a Person entity without persisting to database.

        Useful for unit tests with mocked sessions.

        Args:
            created_by_user_id: UUID of user who created this person
            user_id: Optional UUID of linked user account
            first_name: First name (auto-generated if not provided)
            middle_name: Middle name
            last_name: Last name (auto-generated if not provided)
            gender_id: Gender UUID (uses gender enum if not provided)
            gender: Gender enum (used if gender_id not provided)
            date_of_birth: Date of birth (defaults to 1990-01-01)
            date_of_death: Date of death
            is_primary: Whether this is the primary person for the user

        Returns:
            Person entity (not persisted)
        """
        suffix = cls._get_unique_suffix()

        if first_name is None:
            first_name = f"TestFirst{suffix}"
        if last_name is None:
            last_name = f"TestLast{suffix}"
        if gender_id is None:
            gender_id = cls.get_default_gender_id(gender)
        if date_of_birth is None:
            date_of_birth = date(1990, 1, 1)

        return Person(
            id=uuid.uuid4(),
            user_id=user_id,
            created_by_user_id=created_by_user_id,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            gender_id=gender_id,
            date_of_birth=date_of_birth,
            date_of_death=date_of_death,
            is_primary=is_primary,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @classmethod
    def create_batch(
        cls,
        session: Session,
        count: int,
        *,
        created_by_user: User,
        commit: bool = True,
        **kwargs: Any,
    ) -> list[Person]:
        """Create multiple Person entities.

        Args:
            session: Database session
            count: Number of persons to create
            created_by_user: User who created these person records
            commit: Whether to commit after all persons are created
            **kwargs: Additional arguments passed to create()

        Returns:
            List of created Person entities
        """
        persons = []
        for _ in range(count):
            person = cls.create(
                session,
                created_by_user=created_by_user,
                commit=False,
                **kwargs,
            )
            persons.append(person)

        if commit:
            session.commit()
            for person in persons:
                session.refresh(person)

        return persons

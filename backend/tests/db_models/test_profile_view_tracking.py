"""Unit tests for ProfileViewTracking model."""

import uuid
from datetime import datetime, timezone

import pytest
from sqlmodel import Session, select

from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.db_models.profile_view_tracking import ProfileViewTracking
from app.models import User


class TestProfileViewTrackingModel:
    """Tests for ProfileViewTracking model instantiation and defaults.
    
    **Requirements: 2.7, 2.8**
    """

    def test_model_instantiation_with_defaults(self, db: Session) -> None:
        """Test that ProfileViewTracking model can be instantiated with default values."""
        # Create test users
        user1 = User(
            email=f"viewer_{uuid.uuid4()}@example.com",
            hashed_password="test_password",
            is_active=True,
        )
        user2 = User(
            email=f"viewed_{uuid.uuid4()}@example.com",
            hashed_password="test_password",
            is_active=True,
        )
        db.add(user1)
        db.add(user2)
        db.commit()
        db.refresh(user1)
        db.refresh(user2)

        # Get a gender for the persons
        gender = db.exec(select(Gender)).first()
        assert gender is not None, "Gender must exist in database"

        # Create test persons
        viewer_person = Person(
            user_id=user1.id,
            created_by_user_id=user1.id,
            first_name="Viewer",
            last_name="Test",
            gender_id=gender.id,
            date_of_birth="1990-01-01",
        )
        viewed_person = Person(
            user_id=user2.id,
            created_by_user_id=user2.id,
            first_name="Viewed",
            last_name="Test",
            gender_id=gender.id,
            date_of_birth="1990-01-01",
        )
        db.add(viewer_person)
        db.add(viewed_person)
        db.commit()
        db.refresh(viewer_person)
        db.refresh(viewed_person)

        # Create ProfileViewTracking record with defaults
        view_record = ProfileViewTracking(
            viewer_person_id=viewer_person.id,
            viewed_person_id=viewed_person.id,
        )
        db.add(view_record)
        db.commit()
        db.refresh(view_record)

        # Verify default values
        assert view_record.id is not None, "ID should be auto-generated"
        assert isinstance(view_record.id, uuid.UUID), "ID should be a UUID"
        assert view_record.view_count == 1, "Default view_count should be 1"
        assert view_record.is_aggregated is False, "Default is_aggregated should be False"
        assert view_record.last_viewed_at is not None, "last_viewed_at should be set"
        assert isinstance(view_record.last_viewed_at, datetime), "last_viewed_at should be datetime"
        assert view_record.created_at is not None, "created_at should be set"
        assert isinstance(view_record.created_at, datetime), "created_at should be datetime"
        assert view_record.updated_at is not None, "updated_at should be set"
        assert isinstance(view_record.updated_at, datetime), "updated_at should be datetime"

    def test_field_constraints_and_types(self, db: Session) -> None:
        """Test that ProfileViewTracking fields have correct types and constraints."""
        # Create test users
        user1 = User(
            email=f"viewer_{uuid.uuid4()}@example.com",
            hashed_password="test_password",
            is_active=True,
        )
        user2 = User(
            email=f"viewed_{uuid.uuid4()}@example.com",
            hashed_password="test_password",
            is_active=True,
        )
        db.add(user1)
        db.add(user2)
        db.commit()
        db.refresh(user1)
        db.refresh(user2)

        # Get a gender for the persons
        gender = db.exec(select(Gender)).first()
        assert gender is not None, "Gender must exist in database"

        # Create test persons
        viewer_person = Person(
            user_id=user1.id,
            created_by_user_id=user1.id,
            first_name="Viewer",
            last_name="Test",
            gender_id=gender.id,
            date_of_birth="1990-01-01",
        )
        viewed_person = Person(
            user_id=user2.id,
            created_by_user_id=user2.id,
            first_name="Viewed",
            last_name="Test",
            gender_id=gender.id,
            date_of_birth="1990-01-01",
        )
        db.add(viewer_person)
        db.add(viewed_person)
        db.commit()
        db.refresh(viewer_person)
        db.refresh(viewed_person)

        # Create ProfileViewTracking record with explicit values
        custom_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        view_record = ProfileViewTracking(
            viewer_person_id=viewer_person.id,
            viewed_person_id=viewed_person.id,
            view_count=5,
            is_aggregated=True,
            last_viewed_at=custom_time,
            created_at=custom_time,
            updated_at=custom_time,
        )
        db.add(view_record)
        db.commit()
        db.refresh(view_record)

        # Verify custom values are preserved
        assert view_record.viewer_person_id == viewer_person.id
        assert view_record.viewed_person_id == viewed_person.id
        assert view_record.view_count == 5
        assert view_record.is_aggregated is True
        # Compare timestamps (allowing for timezone differences)
        assert view_record.last_viewed_at.replace(tzinfo=None) == custom_time.replace(tzinfo=None)
        assert view_record.created_at.replace(tzinfo=None) == custom_time.replace(tzinfo=None)
        assert view_record.updated_at.replace(tzinfo=None) == custom_time.replace(tzinfo=None)

        # Verify foreign key relationships work
        # Query the record back
        retrieved = db.exec(
            select(ProfileViewTracking).where(ProfileViewTracking.id == view_record.id)
        ).first()
        assert retrieved is not None
        assert retrieved.viewer_person_id == viewer_person.id
        assert retrieved.viewed_person_id == viewed_person.id

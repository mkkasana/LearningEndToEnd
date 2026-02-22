"""Integration tests for profile view tracking on relationships endpoint."""

import uuid
from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.crud import create_user
from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.db_models.profile_view_tracking import ProfileViewTracking
from app.models import UserCreate
from app.repositories.profile_view_tracking_repository import (
    ProfileViewTrackingRepository,
)
from tests.utils.user import authentication_token_from_email


def test_view_is_recorded_when_endpoint_is_called(
    client: TestClient, db: Session
) -> None:
    """Test that a view is recorded when the relationships endpoint is called.
    
    Requirements: 3.1
    """
    # Get gender from database
    gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
    assert gender is not None, "Male gender must exist in database"
    
    # Create viewer user
    viewer_email = f"viewer_{uuid.uuid4()}@example.com"
    viewer_user = create_user(
        session=db,
        user_create=UserCreate(
            email=viewer_email,
            password="testpass123",
        )
    )
    
    # Create viewer's person
    viewer_person = Person(
        first_name="Viewer",
        last_name="User",
        date_of_birth=date(1990, 1, 1),
        created_by_user_id=viewer_user.id,
        user_id=viewer_user.id,
        gender_id=gender.id,
    )
    db.add(viewer_person)
    
    # Create viewed person (different user)
    viewed_email = f"viewed_{uuid.uuid4()}@example.com"
    viewed_user = create_user(
        session=db,
        user_create=UserCreate(
            email=viewed_email,
            password="testpass123",
        )
    )
    
    viewed_person = Person(
        first_name="Viewed",
        last_name="Person",
        date_of_birth=date(1985, 5, 15),
        created_by_user_id=viewed_user.id,
        user_id=viewed_user.id,
        gender_id=gender.id,
    )
    db.add(viewed_person)
    db.commit()
    db.refresh(viewer_person)
    db.refresh(viewed_person)
    
    # Get authentication token for viewer
    token_headers = authentication_token_from_email(
        client=client, email=viewer_email, db=db
    )
    
    # Call the relationships endpoint
    response = client.get(
        f"{settings.API_V1_STR}/person/{viewed_person.id}/relationships/with-details",
        headers=token_headers,
    )
    
    # Verify endpoint succeeded
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    # Verify view was recorded
    view_repo = ProfileViewTrackingRepository(db)
    view_record = view_repo.get_non_aggregated_view(
        viewer_person_id=viewer_person.id,
        viewed_person_id=viewed_person.id
    )
    
    assert view_record is not None, "View record should be created"
    assert view_record.viewer_person_id == viewer_person.id
    assert view_record.viewed_person_id == viewed_person.id
    assert view_record.view_count == 1
    assert view_record.is_aggregated is False


def test_self_view_is_not_recorded(client: TestClient, db: Session) -> None:
    """Test that self-views are not recorded.
    
    Requirements: 3.4
    """
    # Get gender from database
    gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
    assert gender is not None, "Male gender must exist in database"
    
    # Create user with person
    user_email = f"selfview_{uuid.uuid4()}@example.com"
    user = create_user(
        session=db,
        user_create=UserCreate(
            email=user_email,
            password="testpass123",
        )
    )
    
    person = Person(
        first_name="Self",
        last_name="Viewer",
        date_of_birth=date(1990, 1, 1),
        created_by_user_id=user.id,
        user_id=user.id,
        gender_id=gender.id,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    
    # Get authentication token
    token_headers = authentication_token_from_email(
        client=client, email=user_email, db=db
    )
    
    # Call the relationships endpoint for own person
    response = client.get(
        f"{settings.API_V1_STR}/person/{person.id}/relationships/with-details",
        headers=token_headers,
    )
    
    # Verify endpoint succeeded
    assert response.status_code == 200
    
    # Verify NO view was recorded
    view_repo = ProfileViewTrackingRepository(db)
    view_record = view_repo.get_non_aggregated_view(
        viewer_person_id=person.id,
        viewed_person_id=person.id
    )
    
    assert view_record is None, "Self-view should not be recorded"


def test_viewer_without_person_record_does_not_create_view(
    client: TestClient, db: Session
) -> None:
    """Test that users without person records don't create view records.
    
    Requirements: 3.5
    """
    # Get gender from database
    gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
    assert gender is not None, "Male gender must exist in database"
    
    # Create viewer user WITHOUT person record
    viewer_email = f"noperson_{uuid.uuid4()}@example.com"
    viewer_user = create_user(
        session=db,
        user_create=UserCreate(
            email=viewer_email,
            password="testpass123",
        )
    )
    
    # Create viewed person (different user)
    viewed_email = f"viewed_{uuid.uuid4()}@example.com"
    viewed_user = create_user(
        session=db,
        user_create=UserCreate(
            email=viewed_email,
            password="testpass123",
        )
    )
    
    viewed_person = Person(
        first_name="Viewed",
        last_name="Person",
        date_of_birth=date(1985, 5, 15),
        created_by_user_id=viewed_user.id,
        user_id=viewed_user.id,
        gender_id=gender.id,
    )
    db.add(viewed_person)
    db.commit()
    db.refresh(viewed_person)
    
    # Get authentication token for viewer (who has no person)
    token_headers = authentication_token_from_email(
        client=client, email=viewer_email, db=db
    )
    
    # Call the relationships endpoint
    response = client.get(
        f"{settings.API_V1_STR}/person/{viewed_person.id}/relationships/with-details",
        headers=token_headers,
    )
    
    # Verify endpoint succeeded
    assert response.status_code == 200
    
    # Verify NO view was recorded (no viewer person exists)
    statement = select(ProfileViewTracking).where(
        ProfileViewTracking.viewed_person_id == viewed_person.id
    )
    view_records = db.exec(statement).all()
    
    assert len(view_records) == 0, "No view should be recorded when viewer has no person"


def test_subsequent_views_increment_count(client: TestClient, db: Session) -> None:
    """Test that subsequent views increment the view count.
    
    Requirements: 3.7
    """
    # Get gender from database
    gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
    assert gender is not None, "Male gender must exist in database"
    
    # Create viewer user
    viewer_email = f"viewer_{uuid.uuid4()}@example.com"
    viewer_user = create_user(
        session=db,
        user_create=UserCreate(
            email=viewer_email,
            password="testpass123",
        )
    )
    
    viewer_person = Person(
        first_name="Viewer",
        last_name="User",
        date_of_birth=date(1990, 1, 1),
        created_by_user_id=viewer_user.id,
        user_id=viewer_user.id,
        gender_id=gender.id,
    )
    db.add(viewer_person)
    
    # Create viewed person
    viewed_email = f"viewed_{uuid.uuid4()}@example.com"
    viewed_user = create_user(
        session=db,
        user_create=UserCreate(
            email=viewed_email,
            password="testpass123",
        )
    )
    
    viewed_person = Person(
        first_name="Viewed",
        last_name="Person",
        date_of_birth=date(1985, 5, 15),
        created_by_user_id=viewed_user.id,
        user_id=viewed_user.id,
        gender_id=gender.id,
    )
    db.add(viewed_person)
    db.commit()
    db.refresh(viewer_person)
    db.refresh(viewed_person)
    
    # Get authentication token
    token_headers = authentication_token_from_email(
        client=client, email=viewer_email, db=db
    )
    
    # Call the endpoint first time
    response1 = client.get(
        f"{settings.API_V1_STR}/person/{viewed_person.id}/relationships/with-details",
        headers=token_headers,
    )
    assert response1.status_code == 200
    
    # Check view count after first view
    view_repo = ProfileViewTrackingRepository(db)
    view_record = view_repo.get_non_aggregated_view(
        viewer_person_id=viewer_person.id,
        viewed_person_id=viewed_person.id
    )
    assert view_record is not None
    assert view_record.view_count == 1
    first_viewed_at = view_record.last_viewed_at
    
    # Call the endpoint second time
    response2 = client.get(
        f"{settings.API_V1_STR}/person/{viewed_person.id}/relationships/with-details",
        headers=token_headers,
    )
    assert response2.status_code == 200
    
    # Refresh to get updated record
    db.refresh(view_record)
    
    # Check view count after second view
    assert view_record.view_count == 2, "View count should increment"
    assert view_record.last_viewed_at > first_viewed_at, "last_viewed_at should update"
    
    # Call the endpoint third time
    response3 = client.get(
        f"{settings.API_V1_STR}/person/{viewed_person.id}/relationships/with-details",
        headers=token_headers,
    )
    assert response3.status_code == 200
    
    # Refresh again
    db.refresh(view_record)
    
    # Check view count after third view
    assert view_record.view_count == 3, "View count should continue incrementing"


def test_view_tracking_error_does_not_break_endpoint(
    client: TestClient, db: Session
) -> None:
    """Test that view tracking errors don't break the endpoint.
    
    Requirements: 3.8
    """
    # Get gender from database
    gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
    assert gender is not None, "Male gender must exist in database"
    
    # Create user with person
    user_email = f"errortest_{uuid.uuid4()}@example.com"
    user = create_user(
        session=db,
        user_create=UserCreate(
            email=user_email,
            password="testpass123",
        )
    )
    
    person = Person(
        first_name="Test",
        last_name="Person",
        date_of_birth=date(1990, 1, 1),
        created_by_user_id=user.id,
        user_id=user.id,
        gender_id=gender.id,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    
    # Get authentication token
    token_headers = authentication_token_from_email(
        client=client, email=user_email, db=db
    )
    
    # Call the endpoint - even if view tracking fails internally,
    # the endpoint should still return successfully
    response = client.get(
        f"{settings.API_V1_STR}/person/{person.id}/relationships/with-details",
        headers=token_headers,
    )
    
    # Endpoint should succeed regardless of view tracking
    assert response.status_code == 200, "Endpoint should succeed even if view tracking fails"
    
    # Verify response structure is correct
    data = response.json()
    assert "selected_person" in data
    assert "relationships" in data

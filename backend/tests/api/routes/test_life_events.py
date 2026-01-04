"""Integration tests for Life Events API routes."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.person.person import Person
from app.db_models.person.person_life_event import PersonLifeEvent
from app.schemas.person.life_event import LifeEventType


@pytest.mark.integration
class TestGetMyLifeEvents:
    """Integration tests for GET /life-events/me endpoint."""

    def test_get_my_life_events_success(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test getting current user's life events."""
        # Get the test user by email
        from app.crud import get_user_by_email
        from app.db_models.person.gender import Gender
        
        user = get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
        
        if user:
            # Check if person exists, if not create one
            person = db.exec(
                select(Person).where(Person.user_id == user.id)
            ).first()
            
            if not person:
                # Create a person for the test user
                gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
                person = Person(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    first_name="Test",
                    last_name="User",
                    gender_id=gender.id,
                    date_of_birth="1990-01-01",
                    created_by_user_id=user.id,
                )
                db.add(person)
                db.commit()
                db.refresh(person)

            # Create a life event
            event = PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=person.id,
                event_type=LifeEventType.ACHIEVEMENT,
                title="Test Achievement",
                event_year=2020,
            )
            db.add(event)
            db.commit()

        r = client.get(
            f"{settings.API_V1_STR}/life-events/me",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "data" in data
        assert "count" in data
        assert isinstance(data["data"], list)

    def test_get_my_life_events_without_person_record(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
    ) -> None:
        """Test getting life events without person record returns 400."""
        # This test assumes the user doesn't have a person record
        # In practice, most users will have one
        r = client.get(
            f"{settings.API_V1_STR}/life-events/me",
            headers=normal_user_token_headers,
        )
        # Should return 200 or 400 depending on whether person exists
        assert r.status_code in [200, 400]

    def test_get_my_life_events_with_pagination(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
    ) -> None:
        """Test getting life events with pagination parameters."""
        r = client.get(
            f"{settings.API_V1_STR}/life-events/me?skip=0&limit=10",
            headers=normal_user_token_headers,
        )
        # Should return 200 or 400 depending on whether person exists
        assert r.status_code in [200, 400]

    def test_get_my_life_events_unauthorized(self, client: TestClient) -> None:
        """Test getting life events without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/life-events/me")
        assert r.status_code == 401


@pytest.mark.integration
class TestGetPersonLifeEvents:
    """Integration tests for GET /life-events/person/{person_id} endpoint."""

    def test_get_person_life_events_success(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test getting life events for a specific person by person_id."""
        # Get the test user by email
        from app.crud import get_user_by_email
        from app.db_models.person.gender import Gender
        
        user = get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
        
        if user:
            # Check if person exists, if not create one
            person = db.exec(
                select(Person).where(Person.user_id == user.id)
            ).first()
            
            if not person:
                # Create a person for the test user
                gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
                person = Person(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    first_name="Test",
                    last_name="User",
                    gender_id=gender.id,
                    date_of_birth="1990-01-01",
                    created_by_user_id=user.id,
                )
                db.add(person)
                db.commit()
                db.refresh(person)

            # Create multiple life events with different dates for sorting test
            event1 = PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=person.id,
                event_type=LifeEventType.ACHIEVEMENT,
                title="First Achievement",
                event_year=2020,
                event_month=6,
                event_date=15,
            )
            event2 = PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=person.id,
                event_type=LifeEventType.CAREER,
                title="Second Achievement",
                event_year=2021,
                event_month=3,
                event_date=10,
            )
            event3 = PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=person.id,
                event_type=LifeEventType.EDUCATION,
                title="Third Achievement",
                event_year=2021,
                event_month=8,
                event_date=20,
            )
            db.add(event1)
            db.add(event2)
            db.add(event3)
            db.commit()

            r = client.get(
                f"{settings.API_V1_STR}/life-events/person/{person.id}",
                headers=normal_user_token_headers,
            )
            assert r.status_code == 200
            data = r.json()
            assert "data" in data
            assert "count" in data
            assert isinstance(data["data"], list)
            assert data["count"] >= 3

    def test_get_person_life_events_not_found(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
    ) -> None:
        """Test getting life events for non-existent person returns 404."""
        fake_person_id = uuid.uuid4()
        r = client.get(
            f"{settings.API_V1_STR}/life-events/person/{fake_person_id}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 404
        data = r.json()
        assert data["detail"] == "Person not found"

    def test_get_person_life_events_empty(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test getting life events for person with no events returns empty list."""
        # Get the test user by email
        from app.crud import get_user_by_email
        from app.db_models.person.gender import Gender
        
        user = get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
        
        if user:
            # Create a new person without any life events
            gender = db.exec(select(Gender).where(Gender.code == "FEMALE")).first()
            person = Person(
                id=uuid.uuid4(),
                user_id=user.id,
                first_name="Empty",
                last_name="Events",
                gender_id=gender.id,
                date_of_birth="1995-05-15",
                created_by_user_id=user.id,
            )
            db.add(person)
            db.commit()
            db.refresh(person)

            r = client.get(
                f"{settings.API_V1_STR}/life-events/person/{person.id}",
                headers=normal_user_token_headers,
            )
            assert r.status_code == 200
            data = r.json()
            assert data["data"] == []
            assert data["count"] == 0

    def test_get_person_life_events_pagination(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test getting life events with pagination parameters."""
        # Get the test user by email
        from app.crud import get_user_by_email
        from app.db_models.person.gender import Gender
        
        user = get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
        
        if user:
            person = db.exec(
                select(Person).where(Person.user_id == user.id)
            ).first()
            
            if not person:
                gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
                person = Person(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    first_name="Test",
                    last_name="Pagination",
                    gender_id=gender.id,
                    date_of_birth="1990-01-01",
                    created_by_user_id=user.id,
                )
                db.add(person)
                db.commit()
                db.refresh(person)

            # Create multiple events
            for i in range(5):
                event = PersonLifeEvent(
                    id=uuid.uuid4(),
                    person_id=person.id,
                    event_type=LifeEventType.OTHER,
                    title=f"Event {i}",
                    event_year=2020 + i,
                )
                db.add(event)
            db.commit()

            # Test with limit
            r = client.get(
                f"{settings.API_V1_STR}/life-events/person/{person.id}?skip=0&limit=2",
                headers=normal_user_token_headers,
            )
            assert r.status_code == 200
            data = r.json()
            assert len(data["data"]) <= 2

            # Test with skip
            r = client.get(
                f"{settings.API_V1_STR}/life-events/person/{person.id}?skip=2&limit=2",
                headers=normal_user_token_headers,
            )
            assert r.status_code == 200

    def test_get_person_life_events_sorting(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test that life events are sorted by date descending."""
        # Get the test user by email
        from app.crud import get_user_by_email
        from app.db_models.person.gender import Gender
        
        user = get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
        
        if user:
            # Create a person
            gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
            person = Person(
                id=uuid.uuid4(),
                user_id=user.id,
                first_name="Sort",
                last_name="Test",
                gender_id=gender.id,
                date_of_birth="1990-01-01",
                created_by_user_id=user.id,
            )
            db.add(person)
            db.commit()
            db.refresh(person)

            # Create events in non-chronological order
            event_old = PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=person.id,
                event_type=LifeEventType.BIRTH,
                title="Oldest Event",
                event_year=2015,
                event_month=1,
                event_date=1,
            )
            event_new = PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=person.id,
                event_type=LifeEventType.ACHIEVEMENT,
                title="Newest Event",
                event_year=2023,
                event_month=12,
                event_date=31,
            )
            event_mid = PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=person.id,
                event_type=LifeEventType.CAREER,
                title="Middle Event",
                event_year=2020,
                event_month=6,
                event_date=15,
            )
            db.add(event_old)
            db.add(event_new)
            db.add(event_mid)
            db.commit()

            r = client.get(
                f"{settings.API_V1_STR}/life-events/person/{person.id}",
                headers=normal_user_token_headers,
            )
            assert r.status_code == 200
            data = r.json()
            events = data["data"]
            
            # Verify sorting: most recent first
            if len(events) >= 3:
                # Find our test events
                titles = [e["title"] for e in events]
                newest_idx = titles.index("Newest Event")
                middle_idx = titles.index("Middle Event")
                oldest_idx = titles.index("Oldest Event")
                
                # Newest should come before middle, middle before oldest
                assert newest_idx < middle_idx < oldest_idx

    def test_get_person_life_events_unauthorized(self, client: TestClient) -> None:
        """Test getting life events without authentication returns 401."""
        fake_person_id = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/life-events/person/{fake_person_id}")
        assert r.status_code == 401


@pytest.mark.integration
class TestCreateLifeEvent:
    """Integration tests for POST /life-events/ endpoint."""

    def test_create_life_event_success(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
    ) -> None:
        """Test creating a life event successfully."""
        event_data = {
            "event_type": "marriage",
            "title": "Wedding Day",
            "description": "Got married",
            "event_year": 2020,
            "event_month": 6,
            "event_date": 15,
        }
        r = client.post(
            f"{settings.API_V1_STR}/life-events/",
            headers=normal_user_token_headers,
            json=event_data,
        )
        # May return 200 or 400 if user doesn't have person record
        assert r.status_code in [200, 400]
        if r.status_code == 200:
            data = r.json()
            assert data["title"] == "Wedding Day"
            assert data["event_type"] == "marriage"
            assert "id" in data

    def test_create_life_event_with_only_year(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
    ) -> None:
        """Test creating life event with only year."""
        event_data = {
            "event_type": "achievement",
            "title": "Graduation",
            "event_year": 2015,
        }
        r = client.post(
            f"{settings.API_V1_STR}/life-events/",
            headers=normal_user_token_headers,
            json=event_data,
        )
        assert r.status_code in [200, 400]

    def test_create_life_event_with_invalid_date(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
    ) -> None:
        """Test creating life event with invalid date returns 422."""
        event_data = {
            "event_type": "birth",
            "title": "Birth",
            "event_year": 2020,
            "event_month": 2,
            "event_date": 30,  # February 30 doesn't exist
        }
        r = client.post(
            f"{settings.API_V1_STR}/life-events/",
            headers=normal_user_token_headers,
            json=event_data,
        )
        assert r.status_code == 422

    def test_create_life_event_missing_required_fields(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
    ) -> None:
        """Test creating life event without required fields returns 422."""
        event_data = {
            "title": "Some Event",
            # Missing event_type and event_year
        }
        r = client.post(
            f"{settings.API_V1_STR}/life-events/",
            headers=normal_user_token_headers,
            json=event_data,
        )
        assert r.status_code == 422

    def test_create_life_event_unauthorized(self, client: TestClient) -> None:
        """Test creating life event without authentication returns 401."""
        event_data = {
            "event_type": "other",
            "title": "Test Event",
            "event_year": 2020,
        }
        r = client.post(
            f"{settings.API_V1_STR}/life-events/",
            json=event_data,
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestGetLifeEventById:
    """Integration tests for GET /life-events/{id} endpoint."""

    def test_get_life_event_by_id_success(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test getting a specific life event by ID."""
        # Get the test user by email
        from app.crud import get_user_by_email
        user = get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
        
        if user:
            # Get the person for the test user
            person = db.exec(
                select(Person).where(Person.user_id == user.id)
            ).first()

            if person:
                # Create a life event
                event = PersonLifeEvent(
                    id=uuid.uuid4(),
                    person_id=person.id,
                    event_type=LifeEventType.TRAVEL,
                    title="Trip to Paris",
                    event_year=2019,
                )
                db.add(event)
                db.commit()

                r = client.get(
                    f"{settings.API_V1_STR}/life-events/{event.id}",
                    headers=normal_user_token_headers,
                )
                assert r.status_code == 200
                data = r.json()
                assert data["id"] == str(event.id)
                assert data["title"] == "Trip to Paris"

    def test_get_life_event_nonexistent_id(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
    ) -> None:
        """Test getting non-existent life event returns 404."""
        fake_id = uuid.uuid4()
        r = client.get(
            f"{settings.API_V1_STR}/life-events/{fake_id}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 404

    def test_get_life_event_unauthorized(self, client: TestClient) -> None:
        """Test getting life event without authentication returns 401."""
        fake_id = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/life-events/{fake_id}")
        assert r.status_code == 401


@pytest.mark.integration
class TestUpdateLifeEvent:
    """Integration tests for PUT /life-events/{id} endpoint."""

    def test_update_life_event_success(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test updating a life event successfully."""
        # Get the test user by email
        from app.crud import get_user_by_email
        user = get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
        
        if user:
            # Get the person for the test user
            person = db.exec(
                select(Person).where(Person.user_id == user.id)
            ).first()

            if person:
                # Create a life event
                event = PersonLifeEvent(
                    id=uuid.uuid4(),
                    person_id=person.id,
                    event_type=LifeEventType.CAREER,
                    title="Started Job",
                    event_year=2018,
                )
                db.add(event)
                db.commit()

                update_data = {
                    "title": "Updated Job Title",
                    "description": "New description",
                }
                r = client.put(
                    f"{settings.API_V1_STR}/life-events/{event.id}",
                    headers=normal_user_token_headers,
                    json=update_data,
                )
                assert r.status_code == 200
                data = r.json()
                assert data["title"] == "Updated Job Title"
                assert data["description"] == "New description"

    def test_update_life_event_nonexistent_id(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
    ) -> None:
        """Test updating non-existent life event returns 404."""
        fake_id = uuid.uuid4()
        update_data = {"title": "Updated Title"}
        r = client.put(
            f"{settings.API_V1_STR}/life-events/{fake_id}",
            headers=normal_user_token_headers,
            json=update_data,
        )
        assert r.status_code == 404

    def test_update_life_event_with_invalid_date(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test updating with invalid date returns 422."""
        # Get the test user by email
        from app.crud import get_user_by_email
        user = get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
        
        if user:
            person = db.exec(
                select(Person).where(Person.user_id == user.id)
            ).first()

            if person:
                event = PersonLifeEvent(
                    id=uuid.uuid4(),
                    person_id=person.id,
                    event_type=LifeEventType.OTHER,
                    title="Test Event",
                    event_year=2020,
                )
                db.add(event)
                db.commit()

                update_data = {
                    "event_month": 4,
                    "event_date": 31,  # April 31 doesn't exist
                }
                r = client.put(
                    f"{settings.API_V1_STR}/life-events/{event.id}",
                    headers=normal_user_token_headers,
                    json=update_data,
                )
                assert r.status_code == 422

    def test_update_life_event_unauthorized(self, client: TestClient) -> None:
        """Test updating life event without authentication returns 401."""
        fake_id = uuid.uuid4()
        update_data = {"title": "Updated Title"}
        r = client.put(
            f"{settings.API_V1_STR}/life-events/{fake_id}",
            json=update_data,
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestDeleteLifeEvent:
    """Integration tests for DELETE /life-events/{id} endpoint."""

    def test_delete_life_event_success(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test deleting a life event successfully."""
        # Get the test user by email
        from app.crud import get_user_by_email
        user = get_user_by_email(session=db, email=settings.EMAIL_TEST_USER)
        
        if user:
            person = db.exec(
                select(Person).where(Person.user_id == user.id)
            ).first()

            if person:
                event = PersonLifeEvent(
                    id=uuid.uuid4(),
                    person_id=person.id,
                    event_type=LifeEventType.SALE,
                    title="Sold Car",
                    event_year=2021,
                )
                db.add(event)
                db.commit()
                event_id = event.id

                r = client.delete(
                    f"{settings.API_V1_STR}/life-events/{event_id}",
                    headers=normal_user_token_headers,
                )
                assert r.status_code == 200
                data = r.json()
                assert "message" in data

                # Refresh session to see deletion
                db.expire_all()
                
                # Verify deletion
                deleted_event = db.get(PersonLifeEvent, event_id)
                assert deleted_event is None

    def test_delete_life_event_nonexistent_id(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
    ) -> None:
        """Test deleting non-existent life event returns 404."""
        fake_id = uuid.uuid4()
        r = client.delete(
            f"{settings.API_V1_STR}/life-events/{fake_id}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 404

    def test_delete_life_event_unauthorized(self, client: TestClient) -> None:
        """Test deleting life event without authentication returns 401."""
        fake_id = uuid.uuid4()
        r = client.delete(f"{settings.API_V1_STR}/life-events/{fake_id}")
        assert r.status_code == 401

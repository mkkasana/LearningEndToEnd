"""Property-based tests for person contributions API endpoint.

**Feature: contribution-stats**
"""

import uuid
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlmodel import Session

from app.core.config import settings as app_settings
from app.db_models.person.person import Person
from tests.utils.user import authentication_token_from_email


# Strategies for generating test data
uuid_strategy = st.uuids()
name_strategy = st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=("Cs",)))
date_strategy = st.dates(min_value=date(1900, 1, 1), max_value=date(2024, 12, 31))
bool_strategy = st.booleans()
address_strategy = st.text(min_size=0, max_size=200, alphabet=st.characters(blacklist_categories=("Cs",)))
view_count_strategy = st.integers(min_value=0, max_value=10000)


class TestContributionsAPIResponseCompleteness:
    """Property-based tests for contributions API response completeness.
    
    **Feature: contribution-stats, Property 14: Contributions API Response Completeness**
    **Validates: Requirements 5.2, 5.3, 5.4**
    """

    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    @given(
        first_name=name_strategy,
        last_name=name_strategy,
        date_of_birth=date_strategy,
        date_of_death=st.one_of(st.none(), date_strategy),
        is_active=bool_strategy,
        address=address_strategy,
        total_views=view_count_strategy,
    )
    def test_response_contains_all_required_fields(
        self,
        client: TestClient,
        db: Session,
        first_name: str,
        last_name: str,
        date_of_birth: date,
        date_of_death: date | None,
        is_active: bool,
        address: str,
        total_views: int,
    ) -> None:
        """Property 14: For any contribution returned by the API,
        the response should include all required fields:
        id, first_name, last_name, date_of_birth, date_of_death,
        is_active, address, total_views, created_at.
        """
        # Get authentication token
        token_headers = authentication_token_from_email(
            client=client, email=app_settings.EMAIL_TEST_USER, db=db
        )
        
        # Get the test user
        from app.crud import get_user_by_email
        user = get_user_by_email(session=db, email=app_settings.EMAIL_TEST_USER)
        assert user is not None
        
        # Create mock contribution data
        person_id = uuid.uuid4()
        created_at = datetime.utcnow()
        
        mock_contribution = {
            "id": person_id,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "date_of_death": date_of_death,
            "is_active": is_active,
            "address": address,
            "total_views": total_views,
            "created_at": created_at,
        }
        
        # Mock the PersonService.get_my_contributions method
        with patch("app.api.routes.person.person.PersonService") as mock_service_class:
            mock_service = MagicMock()
            mock_service.get_my_contributions.return_value = [mock_contribution]
            mock_service_class.return_value = mock_service
            
            # Make request to endpoint
            response = client.get(
                f"{app_settings.API_V1_STR}/person/my-contributions",
                headers=token_headers,
            )
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            
            contribution = data[0]
            
            # Verify all required fields are present
            assert "id" in contribution, "Response must include 'id' field"
            assert "first_name" in contribution, "Response must include 'first_name' field"
            assert "last_name" in contribution, "Response must include 'last_name' field"
            assert "date_of_birth" in contribution, "Response must include 'date_of_birth' field"
            assert "date_of_death" in contribution, "Response must include 'date_of_death' field"
            assert "is_active" in contribution, "Response must include 'is_active' field"
            assert "address" in contribution, "Response must include 'address' field"
            assert "total_views" in contribution, "Response must include 'total_views' field"
            assert "created_at" in contribution, "Response must include 'created_at' field"
            
            # Verify field values match
            assert contribution["first_name"] == first_name
            assert contribution["last_name"] == last_name
            assert contribution["is_active"] == is_active
            assert contribution["address"] == address
            assert contribution["total_views"] == total_views

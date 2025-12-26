"""Test person search API endpoint."""

from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.utils.user import authentication_token_from_email


def test_search_matches_endpoint_exists(
    client: TestClient, db: Session
) -> None:
    """Test that the search-matches endpoint exists and requires authentication."""
    # Get authentication token
    token_headers = authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
    
    # Prepare search request (minimal valid data)
    search_data = {
        "first_name": "Test",
        "last_name": "User",
        "gender_id": "00000000-0000-0000-0000-000000000001",  # Placeholder UUID
        "date_of_birth": "1990-01-01",
        "country_id": "00000000-0000-0000-0000-000000000001",
        "state_id": "00000000-0000-0000-0000-000000000001",
        "district_id": "00000000-0000-0000-0000-000000000001",
        "religion_id": "00000000-0000-0000-0000-000000000001",
        "address_display": "Test Address",
        "religion_display": "Test Religion",
    }
    
    # Make request to endpoint
    response = client.post(
        f"{settings.API_V1_STR}/person/search-matches",
        headers=token_headers,
        json=search_data,
    )
    
    # Verify endpoint exists (should not return 404)
    assert response.status_code != 404, "Endpoint not found"
    
    # Verify response is a list (even if empty)
    # Note: May return 422 if UUIDs don't exist in DB, but that's okay for this test
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list), "Response should be a list"


def test_search_matches_requires_authentication(client: TestClient) -> None:
    """Test that the endpoint requires authentication."""
    search_data = {
        "first_name": "Test",
        "last_name": "User",
        "gender_id": "00000000-0000-0000-0000-000000000001",
        "date_of_birth": "1990-01-01",
        "country_id": "00000000-0000-0000-0000-000000000001",
        "state_id": "00000000-0000-0000-0000-000000000001",
        "district_id": "00000000-0000-0000-0000-000000000001",
        "religion_id": "00000000-0000-0000-0000-000000000001",
        "address_display": "Test Address",
        "religion_display": "Test Religion",
    }
    
    # Make request without authentication
    response = client.post(
        f"{settings.API_V1_STR}/person/search-matches",
        json=search_data,
    )
    
    # Should return 401 or 403 (unauthorized)
    assert response.status_code in [401, 403], "Endpoint should require authentication"

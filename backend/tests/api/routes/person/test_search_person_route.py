"""Tests for Person Search API route (/person/search).

Tests cover:
- Successful search requests (Requirement 5.1)
- Validation error handling (Requirement 5.2)
- Internal error handling (Requirement 5.3)
- Authentication requirements (Requirement 5.4)
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.schemas.person.person_search import PersonSearchResponse, PersonSearchResult


# =============================================================================
# Test Data Helpers
# =============================================================================


def create_valid_search_request() -> dict:
    """Create a valid search request with all required fields."""
    return {
        "country_id": str(uuid.uuid4()),
        "state_id": str(uuid.uuid4()),
        "district_id": str(uuid.uuid4()),
        "sub_district_id": str(uuid.uuid4()),
        "religion_id": str(uuid.uuid4()),
        "religion_category_id": str(uuid.uuid4()),
        "skip": 0,
        "limit": 20,
    }


# =============================================================================
# Authentication Tests
# =============================================================================


@pytest.mark.integration
class TestSearchPersonAuthentication:
    """Tests for authentication requirements.
    
    Validates: Requirement 5.4
    """

    def test_search_requires_authentication(
        self,
        client: TestClient,
    ) -> None:
        """Test that search endpoint requires authentication."""
        search_data = create_valid_search_request()

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            json=search_data,
        )

        assert response.status_code == 401


# =============================================================================
# Successful Search Tests
# =============================================================================


@pytest.mark.integration
class TestSearchPersonSuccess:
    """Tests for successful search operations.
    
    Validates: Requirement 5.1
    """

    def test_search_success_empty_results(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test successful search with no matching results."""
        search_data = create_valid_search_request()

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert "results" in content
        assert "total" in content
        assert "skip" in content
        assert "limit" in content
        assert isinstance(content["results"], list)
        assert content["total"] == 0
        assert content["skip"] == 0
        assert content["limit"] == 20

    def test_search_with_optional_filters(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test search with optional filters included."""
        search_data = create_valid_search_request()
        search_data["locality_id"] = str(uuid.uuid4())
        search_data["religion_sub_category_id"] = str(uuid.uuid4())
        search_data["gender_id"] = str(uuid.uuid4())
        search_data["birth_year_from"] = 1980
        search_data["birth_year_to"] = 2000
        search_data["first_name"] = "John"
        search_data["last_name"] = "Doe"

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert "results" in content
        assert "total" in content

    def test_search_with_pagination(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test search with custom pagination parameters."""
        search_data = create_valid_search_request()
        search_data["skip"] = 10
        search_data["limit"] = 50

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["skip"] == 10
        assert content["limit"] == 50

    @patch("app.api.routes.person.search_person.PersonSearchService")
    def test_search_returns_results(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test search returns results when matches are found."""
        # Setup mock
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        mock_response = PersonSearchResponse(
            results=[
                PersonSearchResult(
                    person_id=uuid.uuid4(),
                    first_name="John",
                    middle_name=None,
                    last_name="Doe",
                    date_of_birth="1990-01-15",
                    gender_id=uuid.uuid4(),
                    name_match_score=85.5,
                )
            ],
            total=1,
            skip=0,
            limit=20,
        )
        mock_service.search_persons.return_value = mock_response

        search_data = create_valid_search_request()
        search_data["first_name"] = "John"

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["total"] == 1
        assert len(content["results"]) == 1
        assert content["results"][0]["first_name"] == "John"
        assert content["results"][0]["last_name"] == "Doe"


# =============================================================================
# Validation Error Tests
# =============================================================================


@pytest.mark.integration
class TestSearchPersonValidation:
    """Tests for validation error handling.
    
    Validates: Requirement 5.2
    """

    def test_search_missing_required_field(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when required field is missing."""
        # Missing country_id
        search_data = {
            "state_id": str(uuid.uuid4()),
            "district_id": str(uuid.uuid4()),
            "sub_district_id": str(uuid.uuid4()),
            "religion_id": str(uuid.uuid4()),
            "religion_category_id": str(uuid.uuid4()),
        }

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 422

    def test_search_invalid_uuid_format(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when UUID format is invalid."""
        search_data = create_valid_search_request()
        search_data["country_id"] = "not-a-valid-uuid"

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 422

    def test_search_invalid_birth_year_range(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when birth_year_from > birth_year_to."""
        search_data = create_valid_search_request()
        search_data["birth_year_from"] = 2000
        search_data["birth_year_to"] = 1980

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 422

    def test_search_limit_exceeds_maximum(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when limit exceeds maximum (100)."""
        search_data = create_valid_search_request()
        search_data["limit"] = 200

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 422

    def test_search_negative_skip(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when skip is negative."""
        search_data = create_valid_search_request()
        search_data["skip"] = -1

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 422

    @patch("app.api.routes.person.search_person.PersonSearchService")
    def test_search_value_error_returns_400(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 400 error when service raises ValueError."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.search_persons.side_effect = ValueError("Invalid filter combination")

        search_data = create_valid_search_request()

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 400
        content = response.json()
        assert "Invalid filter combination" in content["detail"]


# =============================================================================
# Internal Error Tests
# =============================================================================


@pytest.mark.integration
class TestSearchPersonInternalError:
    """Tests for internal error handling.
    
    Validates: Requirement 5.3
    """

    @patch("app.api.routes.person.search_person.PersonSearchService")
    def test_search_unexpected_error_returns_500(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 500 error when unexpected exception occurs."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.search_persons.side_effect = Exception("Database connection failed")

        search_data = create_valid_search_request()

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 500
        content = response.json()
        assert "error occurred" in content["detail"].lower()

    @patch("app.api.routes.person.search_person.PersonSearchService")
    def test_search_runtime_error_returns_500(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 500 error when RuntimeError occurs."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.search_persons.side_effect = RuntimeError("Unexpected state")

        search_data = create_valid_search_request()

        response = client.post(
            f"{settings.API_V1_STR}/person/search",
            headers=superuser_token_headers,
            json=search_data,
        )

        assert response.status_code == 500
        content = response.json()
        assert "error occurred" in content["detail"].lower()

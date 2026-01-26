"""Tests for Relatives Network API route (/relatives-network/find).

Tests cover:
- Successful relatives requests (Requirement 7.1)
- Person not found error (Requirement 7.2)
- Internal error handling (Requirement 7.3)
- Authentication requirements (Requirement 7.4)
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.schemas.relatives_network import RelativeInfo, RelativesNetworkResponse


# =============================================================================
# Test Data Helpers
# =============================================================================


def create_valid_relatives_request() -> dict:
    """Create a valid relatives network request with required fields."""
    return {
        "person_id": str(uuid.uuid4()),
        "depth": 3,
        "depth_mode": "up_to",
        "living_only": True,
    }


# =============================================================================
# Authentication Tests
# =============================================================================


@pytest.mark.integration
class TestRelativesNetworkAuthentication:
    """Tests for authentication requirements.
    
    Validates: Requirement 7.4
    """

    def test_find_relatives_requires_authentication(
        self,
        client: TestClient,
    ) -> None:
        """Test that relatives network endpoint requires authentication."""
        request_data = create_valid_relatives_request()

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            json=request_data,
        )

        assert response.status_code == 401


# =============================================================================
# Successful Request Tests
# =============================================================================


@pytest.mark.integration
class TestRelativesNetworkSuccess:
    """Tests for successful relatives network operations.
    
    Validates: Requirement 7.1
    """

    @patch("app.api.routes.relatives_network.find_relatives.RelativesNetworkService")
    def test_find_relatives_success(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test successful relatives network request."""
        person_id = uuid.uuid4()
        relative_id = uuid.uuid4()
        gender_id = uuid.uuid4()
        
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        mock_response = RelativesNetworkResponse(
            person_id=person_id,
            total_count=1,
            depth=3,
            depth_mode="up_to",
            relatives=[
                RelativeInfo(
                    person_id=relative_id,
                    first_name="John",
                    last_name="Doe",
                    gender_id=gender_id,
                    birth_year=1990,
                    death_year=None,
                    district_name="Test District",
                    locality_name="Test Village",
                    depth=1,
                )
            ],
        )
        mock_service.find_relatives.return_value = mock_response

        request_data = {
            "person_id": str(person_id),
            "depth": 3,
            "depth_mode": "up_to",
            "living_only": True,
        }

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["person_id"] == str(person_id)
        assert content["total_count"] == 1
        assert content["depth"] == 3
        assert content["depth_mode"] == "up_to"
        assert len(content["relatives"]) == 1
        assert content["relatives"][0]["first_name"] == "John"

    @patch("app.api.routes.relatives_network.find_relatives.RelativesNetworkService")
    def test_find_relatives_no_results(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test relatives network with no matching results."""
        person_id = uuid.uuid4()
        
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        mock_response = RelativesNetworkResponse(
            person_id=person_id,
            total_count=0,
            depth=3,
            depth_mode="up_to",
            relatives=[],
        )
        mock_service.find_relatives.return_value = mock_response

        request_data = {
            "person_id": str(person_id),
            "depth": 3,
            "depth_mode": "up_to",
        }

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["total_count"] == 0
        assert content["relatives"] == []

    @patch("app.api.routes.relatives_network.find_relatives.RelativesNetworkService")
    def test_find_relatives_only_at_depth_mode(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test relatives network with 'only_at' depth mode."""
        person_id = uuid.uuid4()
        
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        mock_response = RelativesNetworkResponse(
            person_id=person_id,
            total_count=0,
            depth=2,
            depth_mode="only_at",
            relatives=[],
        )
        mock_service.find_relatives.return_value = mock_response

        request_data = {
            "person_id": str(person_id),
            "depth": 2,
            "depth_mode": "only_at",
        }

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["depth_mode"] == "only_at"

    @patch("app.api.routes.relatives_network.find_relatives.RelativesNetworkService")
    def test_find_relatives_with_filters(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test relatives network with optional filters."""
        person_id = uuid.uuid4()
        
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        mock_response = RelativesNetworkResponse(
            person_id=person_id,
            total_count=0,
            depth=3,
            depth_mode="up_to",
            relatives=[],
        )
        mock_service.find_relatives.return_value = mock_response

        request_data = {
            "person_id": str(person_id),
            "depth": 3,
            "depth_mode": "up_to",
            "living_only": False,
            "gender_id": str(uuid.uuid4()),
            "country_id": str(uuid.uuid4()),
            "state_id": str(uuid.uuid4()),
            "district_id": str(uuid.uuid4()),
            "sub_district_id": str(uuid.uuid4()),
            "locality_id": str(uuid.uuid4()),
        }

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 200
        mock_service.find_relatives.assert_called_once()


# =============================================================================
# Not Found Error Tests
# =============================================================================


@pytest.mark.integration
class TestRelativesNetworkNotFound:
    """Tests for person not found error handling.
    
    Validates: Requirement 7.2
    """

    @patch("app.api.routes.relatives_network.find_relatives.RelativesNetworkService")
    def test_find_relatives_person_not_found(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 404 error when person is not found."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.find_relatives.side_effect = HTTPException(
            status_code=404, detail="Person not found"
        )

        request_data = create_valid_relatives_request()

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 404
        content = response.json()
        assert "not found" in content["detail"].lower()


# =============================================================================
# Validation Error Tests
# =============================================================================


@pytest.mark.integration
class TestRelativesNetworkValidation:
    """Tests for request validation.
    
    Validates: Requirement 7.2
    """

    def test_find_relatives_missing_person_id(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when person_id is missing."""
        request_data = {
            "depth": 3,
            "depth_mode": "up_to",
        }

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 422

    def test_find_relatives_invalid_uuid_format(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when UUID format is invalid."""
        request_data = {
            "person_id": "not-a-valid-uuid",
            "depth": 3,
        }

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 422

    def test_find_relatives_invalid_depth_mode(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when depth_mode is invalid."""
        request_data = {
            "person_id": str(uuid.uuid4()),
            "depth": 3,
            "depth_mode": "invalid_mode",
        }

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 422

    def test_find_relatives_depth_below_minimum(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when depth is below minimum (1)."""
        request_data = {
            "person_id": str(uuid.uuid4()),
            "depth": 0,
            "depth_mode": "up_to",
        }

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 422


# =============================================================================
# Internal Error Tests
# =============================================================================


@pytest.mark.integration
class TestRelativesNetworkInternalError:
    """Tests for internal error handling.
    
    Validates: Requirement 7.3
    """

    @patch("app.api.routes.relatives_network.find_relatives.RelativesNetworkService")
    def test_find_relatives_unexpected_error_returns_500(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 500 error when unexpected exception occurs."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.find_relatives.side_effect = Exception("Database connection failed")

        request_data = create_valid_relatives_request()

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 500
        content = response.json()
        assert "error occurred" in content["detail"].lower()

    @patch("app.api.routes.relatives_network.find_relatives.RelativesNetworkService")
    def test_find_relatives_runtime_error_returns_500(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 500 error when RuntimeError occurs."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.find_relatives.side_effect = RuntimeError("Unexpected state")

        request_data = create_valid_relatives_request()

        response = client.post(
            f"{settings.API_V1_STR}/relatives-network/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 500
        content = response.json()
        assert "error occurred" in content["detail"].lower()

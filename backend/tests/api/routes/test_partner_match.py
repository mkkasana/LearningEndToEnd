"""Tests for Partner Match API route (/partner-match/find).

Tests cover:
- Successful match requests (Requirement 6.1)
- Seeker not found error (Requirement 6.2)
- Internal error handling (Requirement 6.3)
- Authentication requirements (Requirement 6.4)
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.schemas.partner_match import PartnerMatchResponse


# =============================================================================
# Test Data Helpers
# =============================================================================


def create_valid_match_request() -> dict:
    """Create a valid partner match request with required fields."""
    return {
        "seeker_person_id": str(uuid.uuid4()),
        "target_gender_code": "FEMALE",
        "max_depth": 5,
    }


# =============================================================================
# Authentication Tests
# =============================================================================


@pytest.mark.integration
class TestPartnerMatchAuthentication:
    """Tests for authentication requirements.
    
    Validates: Requirement 6.4
    """

    def test_find_matches_requires_authentication(
        self,
        client: TestClient,
    ) -> None:
        """Test that partner match endpoint requires authentication."""
        request_data = create_valid_match_request()

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            json=request_data,
        )

        assert response.status_code == 401


# =============================================================================
# Successful Match Tests
# =============================================================================


@pytest.mark.integration
class TestPartnerMatchSuccess:
    """Tests for successful match operations.
    
    Validates: Requirement 6.1
    """

    @patch("app.api.routes.partner_match.find_matches.PartnerMatchService")
    def test_find_matches_success(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test successful partner match request."""
        seeker_id = uuid.uuid4()
        match_id = uuid.uuid4()
        
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        mock_response = PartnerMatchResponse(
            seeker_id=seeker_id,
            total_matches=1,
            matches=[match_id],
            exploration_graph={},
        )
        mock_service.find_matches.return_value = mock_response

        request_data = {
            "seeker_person_id": str(seeker_id),
            "target_gender_code": "FEMALE",
            "max_depth": 5,
        }

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["seeker_id"] == str(seeker_id)
        assert content["total_matches"] == 1
        assert len(content["matches"]) == 1
        assert content["matches"][0] == str(match_id)

    @patch("app.api.routes.partner_match.find_matches.PartnerMatchService")
    def test_find_matches_no_results(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test partner match with no matching results."""
        seeker_id = uuid.uuid4()
        
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        mock_response = PartnerMatchResponse(
            seeker_id=seeker_id,
            total_matches=0,
            matches=[],
            exploration_graph={},
        )
        mock_service.find_matches.return_value = mock_response

        request_data = {
            "seeker_person_id": str(seeker_id),
            "target_gender_code": "MALE",
            "max_depth": 3,
        }

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["total_matches"] == 0
        assert content["matches"] == []

    @patch("app.api.routes.partner_match.find_matches.PartnerMatchService")
    def test_find_matches_with_filters(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test partner match with optional filters."""
        seeker_id = uuid.uuid4()
        
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        mock_response = PartnerMatchResponse(
            seeker_id=seeker_id,
            total_matches=0,
            matches=[],
            exploration_graph={},
        )
        mock_service.find_matches.return_value = mock_response

        request_data = {
            "seeker_person_id": str(seeker_id),
            "target_gender_code": "FEMALE",
            "birth_year_min": 1990,
            "birth_year_max": 2000,
            "include_religion_ids": [str(uuid.uuid4())],
            "include_category_ids": [str(uuid.uuid4())],
            "exclude_sub_category_ids": [str(uuid.uuid4())],
            "max_depth": 4,
            "prune_graph": False,
        }

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 200
        # Verify the service was called with the request
        mock_service.find_matches.assert_called_once()


# =============================================================================
# Not Found Error Tests
# =============================================================================


@pytest.mark.integration
class TestPartnerMatchNotFound:
    """Tests for seeker not found error handling.
    
    Validates: Requirement 6.2
    """

    @patch("app.api.routes.partner_match.find_matches.PartnerMatchService")
    def test_find_matches_seeker_not_found(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 404 error when seeker person is not found."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.find_matches.side_effect = HTTPException(
            status_code=404, detail="Seeker person not found"
        )

        request_data = create_valid_match_request()

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 404
        content = response.json()
        assert "seeker" in content["detail"].lower() or "not found" in content["detail"].lower()

    @patch("app.api.routes.partner_match.find_matches.PartnerMatchService")
    def test_find_matches_invalid_gender_code(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 400 error when gender code is invalid."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.find_matches.side_effect = HTTPException(
            status_code=400, detail="Invalid gender code. Use 'MALE' or 'FEMALE'"
        )

        request_data = create_valid_match_request()
        request_data["target_gender_code"] = "INVALID"

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 400
        content = response.json()
        assert "gender" in content["detail"].lower()


# =============================================================================
# Validation Error Tests
# =============================================================================


@pytest.mark.integration
class TestPartnerMatchValidation:
    """Tests for request validation.
    
    Validates: Requirement 6.2
    """

    def test_find_matches_missing_seeker_id(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when seeker_person_id is missing."""
        request_data = {
            "target_gender_code": "FEMALE",
            "max_depth": 5,
        }

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 422

    def test_find_matches_missing_gender_code(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when target_gender_code is missing."""
        request_data = {
            "seeker_person_id": str(uuid.uuid4()),
            "max_depth": 5,
        }

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 422

    def test_find_matches_invalid_uuid_format(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when UUID format is invalid."""
        request_data = {
            "seeker_person_id": "not-a-valid-uuid",
            "target_gender_code": "FEMALE",
        }

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 422

    def test_find_matches_invalid_birth_year_range(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 422 error when birth_year_min > birth_year_max."""
        request_data = create_valid_match_request()
        request_data["birth_year_min"] = 2000
        request_data["birth_year_max"] = 1990

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 422


# =============================================================================
# Internal Error Tests
# =============================================================================


@pytest.mark.integration
class TestPartnerMatchInternalError:
    """Tests for internal error handling.
    
    Validates: Requirement 6.3
    """

    @patch("app.api.routes.partner_match.find_matches.PartnerMatchService")
    def test_find_matches_unexpected_error_returns_500(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 500 error when unexpected exception occurs."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.find_matches.side_effect = Exception("Database connection failed")

        request_data = create_valid_match_request()

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 500
        content = response.json()
        assert "error occurred" in content["detail"].lower()

    @patch("app.api.routes.partner_match.find_matches.PartnerMatchService")
    def test_find_matches_runtime_error_returns_500(
        self,
        mock_service_class: MagicMock,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 500 error when RuntimeError occurs."""
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        mock_service.find_matches.side_effect = RuntimeError("Unexpected state")

        request_data = create_valid_match_request()

        response = client.post(
            f"{settings.API_V1_STR}/partner-match/find",
            headers=superuser_token_headers,
            json=request_data,
        )

        assert response.status_code == 500
        content = response.json()
        assert "error occurred" in content["detail"].lower()

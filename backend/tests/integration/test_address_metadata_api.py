"""Integration tests for Address Metadata API routes.

This module tests the Address Metadata API endpoints including:
- Country endpoints (Task 30.1)
- State endpoints (Task 30.2)
- District endpoints (Task 30.3)
- Sub-district and locality endpoints (Task 30.4)

Tests use seeded data from init_seed scripts and dynamically created test data.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.address.country import Country
from app.db_models.address.state import State
from app.db_models.address.district import District
from app.db_models.address.sub_district import SubDistrict
from app.db_models.address.locality import Locality
from tests.factories import UserFactory
from tests.utils.user import user_authentication_headers


# ============================================================================
# Helper Functions
# ============================================================================


def get_admin_auth_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Create an admin user and return auth headers."""
    user = UserFactory.create_admin(db, password="adminpassword123")
    headers = user_authentication_headers(
        client=client,
        email=user.email,
        password="adminpassword123",
    )
    return headers


def get_seeded_address_hierarchy(db: Session) -> dict[str, uuid.UUID | None]:
    """Get IDs from seeded address hierarchy."""
    country = db.exec(select(Country)).first()
    state = db.exec(select(State)).first() if country else None
    district = db.exec(select(District)).first() if state else None
    sub_district = db.exec(select(SubDistrict)).first() if district else None
    locality = db.exec(select(Locality)).first() if sub_district else None
    
    return {
        "country_id": country.id if country else None,
        "state_id": state.id if state else None,
        "district_id": district.id if district else None,
        "sub_district_id": sub_district.id if sub_district else None,
        "locality_id": locality.id if locality else None,
    }


# ============================================================================
# Integration Tests - Country Endpoints (Task 30.1)
# ============================================================================


@pytest.mark.integration
class TestCountryEndpoints:
    """Integration tests for country endpoints."""

    def test_get_countries_list(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/address/countries - list all countries."""
        r = client.get(f"{settings.API_V1_STR}/metadata/address/countries")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_country_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/address/countries/{country_id} - get country by ID."""
        country = db.exec(select(Country)).first()
        if not country:
            pytest.skip("No countries found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/countries/{country.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(country.id)
        assert data["name"] == country.name

    def test_get_country_by_id_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/address/countries/{country_id} - non-existent returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/countries/{non_existent_uuid}")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_states_by_country_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/address/country/{country_id}/states - get states by country."""
        country = db.exec(select(Country)).first()
        if not country:
            pytest.skip("No countries found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/country/{country.id}/states")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_states_by_country_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/address/country/{country_id}/states - non-existent country returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/country/{non_existent_uuid}/states")
        assert r.status_code == 404

    def test_get_country_invalid_uuid_format(self, client: TestClient) -> None:
        """Test GET /metadata/address/countries/{country_id} - invalid UUID format returns 422."""
        r = client.get(f"{settings.API_V1_STR}/metadata/address/countries/not-a-valid-uuid")
        assert r.status_code == 422


# ============================================================================
# Integration Tests - State Endpoints (Task 30.2)
# ============================================================================


@pytest.mark.integration
class TestStateEndpoints:
    """Integration tests for state endpoints."""

    def test_get_state_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/address/states/{state_id} - get state by ID."""
        state = db.exec(select(State)).first()
        if not state:
            pytest.skip("No states found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/states/{state.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(state.id)
        assert data["name"] == state.name

    def test_get_state_by_id_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/address/states/{state_id} - non-existent returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/states/{non_existent_uuid}")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_districts_by_state_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/address/state/{state_id}/districts - get districts by state."""
        state = db.exec(select(State)).first()
        if not state:
            pytest.skip("No states found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/state/{state.id}/districts")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_districts_by_state_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/address/state/{state_id}/districts - non-existent state returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/state/{non_existent_uuid}/districts")
        assert r.status_code == 404

    def test_get_state_invalid_uuid_format(self, client: TestClient) -> None:
        """Test GET /metadata/address/states/{state_id} - invalid UUID format returns 422."""
        r = client.get(f"{settings.API_V1_STR}/metadata/address/states/not-a-valid-uuid")
        assert r.status_code == 422


# ============================================================================
# Integration Tests - District Endpoints (Task 30.3)
# ============================================================================


@pytest.mark.integration
class TestDistrictEndpoints:
    """Integration tests for district endpoints."""

    def test_get_district_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/address/districts/{district_id} - get district by ID."""
        district = db.exec(select(District)).first()
        if not district:
            pytest.skip("No districts found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/districts/{district.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(district.id)
        assert data["name"] == district.name

    def test_get_district_by_id_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/address/districts/{district_id} - non-existent returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/districts/{non_existent_uuid}")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_sub_districts_by_district_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/address/district/{district_id}/sub-districts - get sub-districts."""
        district = db.exec(select(District)).first()
        if not district:
            pytest.skip("No districts found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/district/{district.id}/sub-districts")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_sub_districts_by_district_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/address/district/{district_id}/sub-districts - non-existent returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/district/{non_existent_uuid}/sub-districts")
        assert r.status_code == 404

    def test_get_district_invalid_uuid_format(self, client: TestClient) -> None:
        """Test GET /metadata/address/districts/{district_id} - invalid UUID format returns 422."""
        r = client.get(f"{settings.API_V1_STR}/metadata/address/districts/not-a-valid-uuid")
        assert r.status_code == 422


# ============================================================================
# Integration Tests - Sub-District and Locality Endpoints (Task 30.4)
# ============================================================================


@pytest.mark.integration
class TestSubDistrictEndpoints:
    """Integration tests for sub-district endpoints."""

    def test_get_sub_district_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/address/sub-districts/{sub_district_id} - get sub-district by ID."""
        sub_district = db.exec(select(SubDistrict)).first()
        if not sub_district:
            pytest.skip("No sub-districts found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-districts/{sub_district.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(sub_district.id)
        assert data["name"] == sub_district.name

    def test_get_sub_district_by_id_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/address/sub-districts/{sub_district_id} - non-existent returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-districts/{non_existent_uuid}")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_localities_by_sub_district_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/address/sub-district/{sub_district_id}/localities - get localities."""
        sub_district = db.exec(select(SubDistrict)).first()
        if not sub_district:
            pytest.skip("No sub-districts found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-district/{sub_district.id}/localities")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_localities_by_sub_district_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/address/sub-district/{sub_district_id}/localities - non-existent returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-district/{non_existent_uuid}/localities")
        assert r.status_code == 404

    def test_get_sub_district_invalid_uuid_format(self, client: TestClient) -> None:
        """Test GET /metadata/address/sub-districts/{sub_district_id} - invalid UUID format returns 422."""
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-districts/not-a-valid-uuid")
        assert r.status_code == 422


@pytest.mark.integration
class TestLocalityEndpoints:
    """Integration tests for locality endpoints."""

    def test_get_locality_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/address/localities/{locality_id} - get locality by ID."""
        locality = db.exec(select(Locality)).first()
        if not locality:
            pytest.skip("No localities found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/localities/{locality.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(locality.id)
        assert data["name"] == locality.name

    def test_get_locality_by_id_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/address/localities/{locality_id} - non-existent returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/localities/{non_existent_uuid}")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_locality_invalid_uuid_format(self, client: TestClient) -> None:
        """Test GET /metadata/address/localities/{locality_id} - invalid UUID format returns 422."""
        r = client.get(f"{settings.API_V1_STR}/metadata/address/localities/not-a-valid-uuid")
        assert r.status_code == 422


# ============================================================================
# Integration Tests - Address Hierarchy Validation
# ============================================================================


@pytest.mark.integration
class TestAddressHierarchyValidation:
    """Integration tests for address hierarchy validation."""

    def test_state_belongs_to_country(self, client: TestClient, db: Session) -> None:
        """Test that states returned for a country actually belong to that country."""
        country = db.exec(select(Country)).first()
        if not country:
            pytest.skip("No countries found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/country/{country.id}/states")
        assert r.status_code == 200
        states = r.json()
        
        # Verify each state belongs to the country
        for state in states:
            state_id = state.get("id") or state.get("stateId")
            if state_id:
                state_detail = client.get(
                    f"{settings.API_V1_STR}/metadata/address/states/{state_id}"
                )
                if state_detail.status_code == 200:
                    assert state_detail.json().get("country_id") == str(country.id)

    def test_district_belongs_to_state(self, client: TestClient, db: Session) -> None:
        """Test that districts returned for a state actually belong to that state."""
        state = db.exec(select(State)).first()
        if not state:
            pytest.skip("No states found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/state/{state.id}/districts")
        assert r.status_code == 200
        districts = r.json()
        
        # Verify each district belongs to the state
        for district in districts:
            district_id = district.get("id") or district.get("districtId")
            if district_id:
                district_detail = client.get(
                    f"{settings.API_V1_STR}/metadata/address/districts/{district_id}"
                )
                if district_detail.status_code == 200:
                    assert district_detail.json().get("state_id") == str(state.id)

    def test_sub_district_belongs_to_district(self, client: TestClient, db: Session) -> None:
        """Test that sub-districts returned for a district actually belong to that district."""
        district = db.exec(select(District)).first()
        if not district:
            pytest.skip("No districts found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/district/{district.id}/sub-districts")
        assert r.status_code == 200
        sub_districts = r.json()
        
        # Verify each sub-district belongs to the district
        for sub_district in sub_districts:
            sub_district_id = sub_district.get("id") or sub_district.get("subDistrictId")
            if sub_district_id:
                sub_district_detail = client.get(
                    f"{settings.API_V1_STR}/metadata/address/sub-districts/{sub_district_id}"
                )
                if sub_district_detail.status_code == 200:
                    assert sub_district_detail.json().get("district_id") == str(district.id)

    def test_locality_belongs_to_sub_district(self, client: TestClient, db: Session) -> None:
        """Test that localities returned for a sub-district actually belong to that sub-district."""
        sub_district = db.exec(select(SubDistrict)).first()
        if not sub_district:
            pytest.skip("No sub-districts found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-district/{sub_district.id}/localities")
        assert r.status_code == 200
        localities = r.json()
        
        # Verify each locality belongs to the sub-district
        for locality in localities:
            locality_id = locality.get("id") or locality.get("localityId")
            if locality_id:
                locality_detail = client.get(
                    f"{settings.API_V1_STR}/metadata/address/localities/{locality_id}"
                )
                if locality_detail.status_code == 200:
                    assert locality_detail.json().get("sub_district_id") == str(sub_district.id)


# ============================================================================
# Integration Tests - Non-Existent Address Hierarchy Returns 404
# ============================================================================


@pytest.mark.integration
class TestNonExistentAddressHierarchy:
    """Integration tests for non-existent address hierarchy returning 404.
    
    **Feature: backend-testing-coverage, Property 2: Non-Existent Resource Returns 404**
    **Validates: Requirements 11.11**
    """

    def test_non_existent_country_returns_404(self, client: TestClient) -> None:
        """Test that non-existent country returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/countries/{non_existent_uuid}")
        assert r.status_code == 404

    def test_non_existent_state_returns_404(self, client: TestClient) -> None:
        """Test that non-existent state returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/states/{non_existent_uuid}")
        assert r.status_code == 404

    def test_non_existent_district_returns_404(self, client: TestClient) -> None:
        """Test that non-existent district returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/districts/{non_existent_uuid}")
        assert r.status_code == 404

    def test_non_existent_sub_district_returns_404(self, client: TestClient) -> None:
        """Test that non-existent sub-district returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-districts/{non_existent_uuid}")
        assert r.status_code == 404

    def test_non_existent_locality_returns_404(self, client: TestClient) -> None:
        """Test that non-existent locality returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/localities/{non_existent_uuid}")
        assert r.status_code == 404

    def test_non_existent_country_for_states_returns_404(self, client: TestClient) -> None:
        """Test that getting states for non-existent country returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/country/{non_existent_uuid}/states")
        assert r.status_code == 404

    def test_non_existent_state_for_districts_returns_404(self, client: TestClient) -> None:
        """Test that getting districts for non-existent state returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/state/{non_existent_uuid}/districts")
        assert r.status_code == 404

    def test_non_existent_district_for_sub_districts_returns_404(self, client: TestClient) -> None:
        """Test that getting sub-districts for non-existent district returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/district/{non_existent_uuid}/sub-districts")
        assert r.status_code == 404

    def test_non_existent_sub_district_for_localities_returns_404(self, client: TestClient) -> None:
        """Test that getting localities for non-existent sub-district returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-district/{non_existent_uuid}/localities")
        assert r.status_code == 404

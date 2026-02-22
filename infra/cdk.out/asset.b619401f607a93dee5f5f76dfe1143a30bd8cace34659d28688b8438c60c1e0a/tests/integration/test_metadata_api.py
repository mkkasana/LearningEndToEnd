"""Integration tests for Metadata API routes.

This module tests the Metadata API endpoints including:
- Address metadata (Task 19.1)
- Religion metadata (Task 19.2)
- Person metadata (Task 19.3)

Tests use seeded data from init_seed scripts.

Requirements: 11.1-11.11
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
from app.db_models.religion.religion import Religion
from app.db_models.religion.religion_category import ReligionCategory
from app.db_models.religion.religion_sub_category import ReligionSubCategory
from app.db_models.person.gender import Gender
from app.db_models.person.profession import Profession


# ============================================================================
# Integration Tests - Address Metadata (Task 19.1)
# ============================================================================


@pytest.mark.integration
class TestGetCountries:
    """Integration tests for GET /metadata/address/countries endpoint.
    
    Requirements: 11.1
    """

    def test_get_countries_success(self, client: TestClient, db: Session) -> None:
        """Test getting list of countries."""
        r = client.get(f"{settings.API_V1_STR}/metadata/address/countries")
        assert r.status_code == 200
        data = r.json()
        
        # Should return a list
        assert isinstance(data, list)
        
        # If there are countries, verify structure (may have different field names)
        if len(data) > 0:
            country = data[0]
            # Check for either 'id' or 'countryId' field
            assert "id" in country or "countryId" in country
            assert "name" in country or "countryName" in country

    def test_get_country_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test getting a specific country by ID."""
        # Get first country from database
        country = db.exec(select(Country)).first()
        if not country:
            pytest.skip("No countries found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/countries/{country.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(country.id)
        assert data["name"] == country.name

    def test_get_country_by_id_not_found(self, client: TestClient) -> None:
        """Test getting non-existent country returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/countries/{non_existent_uuid}")
        assert r.status_code == 404


@pytest.mark.integration
class TestGetStatesByCountry:
    """Integration tests for GET /metadata/address/country/{country_id}/states endpoint.
    
    Requirements: 11.2
    """

    def test_get_states_by_country_success(self, client: TestClient, db: Session) -> None:
        """Test getting states for a specific country."""
        # Get first country from database
        country = db.exec(select(Country)).first()
        if not country:
            pytest.skip("No countries found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/country/{country.id}/states")
        assert r.status_code == 200
        data = r.json()
        
        # Should return a list
        assert isinstance(data, list)
        
        # If there are states, verify structure (may have different field names)
        if len(data) > 0:
            state = data[0]
            # Check for either 'id' or 'stateId' field
            assert "id" in state or "stateId" in state
            assert "name" in state or "stateName" in state

    def test_get_states_by_country_not_found(self, client: TestClient) -> None:
        """Test getting states for non-existent country returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/country/{non_existent_uuid}/states")
        assert r.status_code == 404

    def test_get_state_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test getting a specific state by ID."""
        state = db.exec(select(State)).first()
        if not state:
            pytest.skip("No states found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/states/{state.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(state.id)
        assert data["name"] == state.name

    def test_get_state_by_id_not_found(self, client: TestClient) -> None:
        """Test getting non-existent state returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/states/{non_existent_uuid}")
        assert r.status_code == 404


@pytest.mark.integration
class TestGetDistrictsByState:
    """Integration tests for GET /metadata/address/state/{state_id}/districts endpoint.
    
    Requirements: 11.3
    """

    def test_get_districts_by_state_success(self, client: TestClient, db: Session) -> None:
        """Test getting districts for a specific state."""
        state = db.exec(select(State)).first()
        if not state:
            pytest.skip("No states found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/state/{state.id}/districts")
        assert r.status_code == 200
        data = r.json()
        
        # Should return a list
        assert isinstance(data, list)

    def test_get_districts_by_state_not_found(self, client: TestClient) -> None:
        """Test getting districts for non-existent state returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/state/{non_existent_uuid}/districts")
        assert r.status_code == 404

    def test_get_district_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test getting a specific district by ID."""
        district = db.exec(select(District)).first()
        if not district:
            pytest.skip("No districts found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/districts/{district.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(district.id)
        assert data["name"] == district.name

    def test_get_district_by_id_not_found(self, client: TestClient) -> None:
        """Test getting non-existent district returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/districts/{non_existent_uuid}")
        assert r.status_code == 404


@pytest.mark.integration
class TestGetSubDistrictsByDistrict:
    """Integration tests for GET /metadata/address/district/{district_id}/sub-districts endpoint.
    
    Requirements: 11.4
    """

    def test_get_sub_districts_by_district_success(self, client: TestClient, db: Session) -> None:
        """Test getting sub-districts for a specific district."""
        district = db.exec(select(District)).first()
        if not district:
            pytest.skip("No districts found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/district/{district.id}/sub-districts")
        assert r.status_code == 200
        data = r.json()
        
        # Should return a list
        assert isinstance(data, list)

    def test_get_sub_districts_by_district_not_found(self, client: TestClient) -> None:
        """Test getting sub-districts for non-existent district returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/district/{non_existent_uuid}/sub-districts")
        assert r.status_code == 404

    def test_get_sub_district_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test getting a specific sub-district by ID."""
        sub_district = db.exec(select(SubDistrict)).first()
        if not sub_district:
            pytest.skip("No sub-districts found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-districts/{sub_district.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(sub_district.id)
        assert data["name"] == sub_district.name

    def test_get_sub_district_by_id_not_found(self, client: TestClient) -> None:
        """Test getting non-existent sub-district returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-districts/{non_existent_uuid}")
        assert r.status_code == 404


@pytest.mark.integration
class TestGetLocalitiesBySubDistrict:
    """Integration tests for GET /metadata/address/sub-district/{sub_district_id}/localities endpoint.
    
    Requirements: 11.5
    """

    def test_get_localities_by_sub_district_success(self, client: TestClient, db: Session) -> None:
        """Test getting localities for a specific sub-district."""
        sub_district = db.exec(select(SubDistrict)).first()
        if not sub_district:
            pytest.skip("No sub-districts found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-district/{sub_district.id}/localities")
        assert r.status_code == 200
        data = r.json()
        
        # Should return a list
        assert isinstance(data, list)

    def test_get_localities_by_sub_district_not_found(self, client: TestClient) -> None:
        """Test getting localities for non-existent sub-district returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-district/{non_existent_uuid}/localities")
        assert r.status_code == 404

    def test_get_locality_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test getting a specific locality by ID."""
        locality = db.exec(select(Locality)).first()
        if not locality:
            pytest.skip("No localities found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/address/localities/{locality.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(locality.id)
        assert data["name"] == locality.name

    def test_get_locality_by_id_not_found(self, client: TestClient) -> None:
        """Test getting non-existent locality returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/localities/{non_existent_uuid}")
        assert r.status_code == 404


# ============================================================================
# Integration Tests - Religion Metadata (Task 19.2)
# ============================================================================


@pytest.mark.integration
class TestGetReligions:
    """Integration tests for GET /metadata/religion/religions endpoint.
    
    Requirements: 11.6
    """

    def test_get_religions_success(self, client: TestClient, db: Session) -> None:
        """Test getting list of religions."""
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religions")
        assert r.status_code == 200
        data = r.json()
        
        # Should return a list
        assert isinstance(data, list)
        
        # If there are religions, verify structure (may have different field names)
        if len(data) > 0:
            religion = data[0]
            assert "id" in religion or "religionId" in religion
            assert "name" in religion or "religionName" in religion

    def test_get_religion_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test getting a specific religion by ID."""
        religion = db.exec(select(Religion)).first()
        if not religion:
            pytest.skip("No religions found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religions/{religion.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(religion.id)
        assert data["name"] == religion.name

    def test_get_religion_by_id_not_found(self, client: TestClient) -> None:
        """Test getting non-existent religion returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religions/{non_existent_uuid}")
        assert r.status_code == 404


@pytest.mark.integration
class TestGetReligionCategories:
    """Integration tests for GET /metadata/religion/religion/{religion_id}/categories endpoint.
    
    Requirements: 11.7
    """

    def test_get_categories_by_religion_success(self, client: TestClient, db: Session) -> None:
        """Test getting categories for a specific religion."""
        religion = db.exec(select(Religion)).first()
        if not religion:
            pytest.skip("No religions found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religion/{religion.id}/categories")
        assert r.status_code == 200
        data = r.json()
        
        # Should return a list
        assert isinstance(data, list)

    def test_get_categories_by_religion_not_found(self, client: TestClient) -> None:
        """Test getting categories for non-existent religion returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religion/{non_existent_uuid}/categories")
        assert r.status_code == 404

    def test_get_category_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test getting a specific category by ID."""
        category = db.exec(select(ReligionCategory)).first()
        if not category:
            pytest.skip("No religion categories found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/categories/{category.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(category.id)
        assert data["name"] == category.name

    def test_get_category_by_id_not_found(self, client: TestClient) -> None:
        """Test getting non-existent category returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/categories/{non_existent_uuid}")
        assert r.status_code == 404


@pytest.mark.integration
class TestGetReligionSubCategories:
    """Integration tests for GET /metadata/religion/category/{category_id}/sub-categories endpoint.
    
    Requirements: 11.8
    """

    def test_get_sub_categories_by_category_success(self, client: TestClient, db: Session) -> None:
        """Test getting sub-categories for a specific category."""
        category = db.exec(select(ReligionCategory)).first()
        if not category:
            pytest.skip("No religion categories found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/category/{category.id}/sub-categories")
        assert r.status_code == 200
        data = r.json()
        
        # Should return a list
        assert isinstance(data, list)

    def test_get_sub_categories_by_category_not_found(self, client: TestClient) -> None:
        """Test getting sub-categories for non-existent category returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/category/{non_existent_uuid}/sub-categories")
        assert r.status_code == 404

    def test_get_sub_category_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test getting a specific sub-category by ID."""
        sub_category = db.exec(select(ReligionSubCategory)).first()
        if not sub_category:
            pytest.skip("No religion sub-categories found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/sub-categories/{sub_category.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(sub_category.id)
        assert data["name"] == sub_category.name

    def test_get_sub_category_by_id_not_found(self, client: TestClient) -> None:
        """Test getting non-existent sub-category returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/sub-categories/{non_existent_uuid}")
        assert r.status_code == 404


# ============================================================================
# Integration Tests - Person Metadata (Task 19.3)
# ============================================================================


@pytest.mark.integration
class TestGetGenders:
    """Integration tests for GET /metadata/person/genders endpoint.
    
    Requirements: 11.9
    """

    def test_get_genders_success(self, client: TestClient) -> None:
        """Test getting list of genders."""
        r = client.get(f"{settings.API_V1_STR}/metadata/person/genders")
        assert r.status_code == 200
        data = r.json()
        
        # Should return a list
        assert isinstance(data, list)
        
        # Should have at least Male and Female
        assert len(data) >= 2
        
        # Verify structure (may have different field names)
        gender = data[0]
        assert "id" in gender or "genderId" in gender
        assert "name" in gender or "genderName" in gender

    def test_get_gender_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test getting a specific gender by ID."""
        gender = db.exec(select(Gender)).first()
        if not gender:
            pytest.skip("No genders found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/person/genders/{gender.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(gender.id)
        assert data["name"] == gender.name

    def test_get_gender_by_id_not_found(self, client: TestClient) -> None:
        """Test getting non-existent gender returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/person/genders/{non_existent_uuid}")
        assert r.status_code == 404


@pytest.mark.integration
class TestGetProfessions:
    """Integration tests for GET /metadata/person/professions endpoint.
    
    Requirements: 11.10
    """

    def test_get_professions_success(self, client: TestClient) -> None:
        """Test getting list of professions."""
        r = client.get(f"{settings.API_V1_STR}/metadata/person/professions")
        assert r.status_code == 200
        data = r.json()
        
        # Should return a list
        assert isinstance(data, list)

    def test_get_profession_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test getting a specific profession by ID."""
        profession = db.exec(select(Profession)).first()
        if not profession:
            pytest.skip("No professions found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/person/professions/{profession.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(profession.id)
        assert data["name"] == profession.name

    def test_get_profession_by_id_not_found(self, client: TestClient) -> None:
        """Test getting non-existent profession returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/person/professions/{non_existent_uuid}")
        assert r.status_code == 404


# ============================================================================
# Property-Based Tests - Non-Existent Parent Returns 404 (Task 19.4)
# ============================================================================


@pytest.mark.integration
class TestNonExistentParentReturns404Property:
    """Property-based tests for non-existent parent returning 404.
    
    **Feature: backend-testing-coverage, Property 2: Non-Existent Resource Returns 404**
    **Validates: Requirements 11.11**
    """

    def test_non_existent_country_returns_404_for_states(self, client: TestClient) -> None:
        """Property 2: For any non-existent country_id, getting states returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/country/{non_existent_uuid}/states")
        assert r.status_code == 404

    def test_non_existent_state_returns_404_for_districts(self, client: TestClient) -> None:
        """Property 2: For any non-existent state_id, getting districts returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/state/{non_existent_uuid}/districts")
        assert r.status_code == 404

    def test_non_existent_district_returns_404_for_sub_districts(self, client: TestClient) -> None:
        """Property 2: For any non-existent district_id, getting sub-districts returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/district/{non_existent_uuid}/sub-districts")
        assert r.status_code == 404

    def test_non_existent_sub_district_returns_404_for_localities(self, client: TestClient) -> None:
        """Property 2: For any non-existent sub_district_id, getting localities returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/address/sub-district/{non_existent_uuid}/localities")
        assert r.status_code == 404

    def test_non_existent_religion_returns_404_for_categories(self, client: TestClient) -> None:
        """Property 2: For any non-existent religion_id, getting categories returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religion/{non_existent_uuid}/categories")
        assert r.status_code == 404

    def test_non_existent_category_returns_404_for_sub_categories(self, client: TestClient) -> None:
        """Property 2: For any non-existent category_id, getting sub-categories returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/category/{non_existent_uuid}/sub-categories")
        assert r.status_code == 404

    def test_hierarchical_address_consistency(self, client: TestClient, db: Session) -> None:
        """Property: Address hierarchy should be consistent - children belong to their parents."""
        # Get a state and verify it belongs to a valid country
        state = db.exec(select(State)).first()
        if not state:
            pytest.skip("No states found in database")
        
        # Get the parent country
        r = client.get(f"{settings.API_V1_STR}/metadata/address/countries/{state.country_id}")
        assert r.status_code == 200
        
        # Get states for that country and verify our state is in the list
        r = client.get(f"{settings.API_V1_STR}/metadata/address/country/{state.country_id}/states")
        assert r.status_code == 200
        states = r.json()
        # Handle different field names (stateId vs id)
        state_ids = [s.get("id") or s.get("stateId") for s in states]
        assert str(state.id) in [str(sid) for sid in state_ids if sid]

    def test_hierarchical_religion_consistency(self, client: TestClient, db: Session) -> None:
        """Property: Religion hierarchy should be consistent - children belong to their parents."""
        # Get a category and verify it belongs to a valid religion
        category = db.exec(select(ReligionCategory)).first()
        if not category:
            pytest.skip("No religion categories found in database")
        
        # Get the parent religion
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religions/{category.religion_id}")
        assert r.status_code == 200
        
        # Get categories for that religion and verify our category is in the list
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religion/{category.religion_id}/categories")
        assert r.status_code == 200
        categories = r.json()
        # Handle different field names (categoryId vs id)
        category_ids = [c.get("id") or c.get("categoryId") for c in categories]
        assert str(category.id) in [str(cid) for cid in category_ids if cid]

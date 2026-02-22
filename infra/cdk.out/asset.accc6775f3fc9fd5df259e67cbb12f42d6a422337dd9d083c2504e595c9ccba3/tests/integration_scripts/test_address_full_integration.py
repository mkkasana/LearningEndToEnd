#!/usr/bin/env python3
"""
Comprehensive Integration Test for Address Metadata API

Tests all CRUD operations for all 5 address components:
- Countries
- States
- Districts
- Sub-Districts
- Localities

Usage:
    python3 backend/tests/integration_scripts/test_address_full_integration.py [port]
    
    Default port: 8000
"""

import sys
import uuid
from typing import Any

import requests

# Configuration
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
BASE_URL = f"http://localhost:{PORT}/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "changethis"

# Test counters
tests_passed = 0
tests_failed = 0


def print_header(text: str) -> None:
    """Print a formatted header."""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_test(text: str) -> None:
    """Print a test description."""
    print(f"→ {text}...", end=" ", flush=True)


def pass_test(message: str = "") -> None:
    """Mark test as passed."""
    global tests_passed
    tests_passed += 1
    suffix = f" ({message})" if message else ""
    print(f"✓{suffix}")


def fail_test(message: str) -> None:
    """Mark test as failed."""
    global tests_failed
    tests_failed += 1
    print(f"✗ FAILED: {message}")


def get_auth_token() -> str:
    """Get authentication token for superuser."""
    print_test("Getting authentication token")
    try:
        response = requests.post(
            f"{BASE_URL}/login/access-token",
            data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        token = response.json()["access_token"]
        pass_test()
        return token
    except Exception as e:
        fail_test(f"Failed to get token: {e}")
        sys.exit(1)


def test_countries_crud(headers: dict[str, str]) -> dict[str, Any]:
    """Test all CRUD operations for countries."""
    print_header("COUNTRIES - CRUD Operations")
    
    country_data = {
        "name": "Test Integration Country",
        "code": "TIC",
        "is_active": True,
    }
    
    # CREATE
    print_test("CREATE country")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/address/countries",
            json=country_data,
            headers=headers,
        )
        response.raise_for_status()
        country = response.json()
        assert "id" in country
        assert country["name"] == country_data["name"]
        assert country["code"] == country_data["code"].upper()
        pass_test(f"ID: {country['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}
    
    # READ - Get by ID
    print_test("READ country by ID")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/address/countries/{country['id']}"
        )
        response.raise_for_status()
        fetched = response.json()
        assert fetched["id"] == country["id"]
        assert fetched["name"] == country["name"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # READ - Get all countries
    print_test("READ all countries")
    try:
        response = requests.get(f"{BASE_URL}/metadata/address/countries")
        response.raise_for_status()
        countries = response.json()
        assert isinstance(countries, list)
        assert len(countries) > 0
        pass_test(f"{len(countries)} countries found")
    except Exception as e:
        fail_test(str(e))
    
    # UPDATE
    print_test("UPDATE country")
    try:
        update_data = {"name": "Updated Integration Country"}
        response = requests.patch(
            f"{BASE_URL}/metadata/address/countries/{country['id']}",
            json=update_data,
            headers=headers,
        )
        response.raise_for_status()
        updated = response.json()
        assert updated["name"] == update_data["name"]
        assert updated["code"] == country["code"]
        country = updated
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # Test duplicate code validation
    print_test("Validate duplicate code prevention")
    try:
        duplicate_data = {"name": "Duplicate Country", "code": country["code"], "is_active": True}
        response = requests.post(
            f"{BASE_URL}/metadata/address/countries",
            json=duplicate_data,
            headers=headers,
        )
        assert response.status_code == 400
        pass_test("Duplicate rejected")
    except Exception as e:
        fail_test(str(e))
    
    # Test 404 handling
    print_test("Validate 404 for non-existent country")
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{BASE_URL}/metadata/address/countries/{fake_id}")
        assert response.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    return country


def test_states_crud(headers: dict[str, str], country: dict[str, Any]) -> dict[str, Any]:
    """Test all CRUD operations for states."""
    print_header("STATES - CRUD Operations")
    
    state_data = {
        "name": "Test Integration State",
        "code": "TIS",
        "country_id": country["id"],
        "is_active": True,
    }
    
    # CREATE
    print_test("CREATE state")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/address/states",
            json=state_data,
            headers=headers,
        )
        response.raise_for_status()
        state = response.json()
        assert "id" in state
        assert state["name"] == state_data["name"]
        assert state["country_id"] == country["id"]
        pass_test(f"ID: {state['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}
    
    # READ - Get by ID
    print_test("READ state by ID")
    try:
        response = requests.get(f"{BASE_URL}/metadata/address/states/{state['id']}")
        response.raise_for_status()
        fetched = response.json()
        assert fetched["id"] == state["id"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # READ - Get states by country
    print_test("READ states by country")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/address/country/{country['id']}/states"
        )
        response.raise_for_status()
        states = response.json()
        assert isinstance(states, list)
        # List endpoints return camelCase format (stateId, stateName)
        assert any(s["stateId"] == state["id"] for s in states)
        pass_test(f"{len(states)} states found")
    except Exception as e:
        fail_test(str(e))
    
    # UPDATE
    print_test("UPDATE state")
    try:
        update_data = {"name": "Updated Integration State"}
        response = requests.patch(
            f"{BASE_URL}/metadata/address/states/{state['id']}",
            json=update_data,
            headers=headers,
        )
        response.raise_for_status()
        updated = response.json()
        assert updated["name"] == update_data["name"]
        state = updated
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # Test invalid country_id
    print_test("Validate invalid country_id rejection")
    try:
        invalid_data = {
            "name": "Invalid State",
            "code": "INV",
            "country_id": "00000000-0000-0000-0000-000000000000",
            "is_active": True,
        }
        response = requests.post(
            f"{BASE_URL}/metadata/address/states",
            json=invalid_data,
            headers=headers,
        )
        assert response.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    return state


def test_districts_crud(headers: dict[str, str], state: dict[str, Any]) -> dict[str, Any]:
    """Test all CRUD operations for districts."""
    print_header("DISTRICTS - CRUD Operations")
    
    district_data = {
        "name": "Test Integration District",
        "code": "TID",
        "state_id": state["id"],
        "is_active": True,
    }
    
    # CREATE
    print_test("CREATE district")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/address/districts",
            json=district_data,
            headers=headers,
        )
        response.raise_for_status()
        district = response.json()
        assert "id" in district
        assert district["name"] == district_data["name"]
        assert district["state_id"] == state["id"]
        pass_test(f"ID: {district['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}
    
    # READ - Get by ID
    print_test("READ district by ID")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/address/districts/{district['id']}"
        )
        response.raise_for_status()
        fetched = response.json()
        assert fetched["id"] == district["id"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # READ - Get districts by state
    print_test("READ districts by state")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/address/state/{state['id']}/districts"
        )
        response.raise_for_status()
        districts = response.json()
        assert isinstance(districts, list)
        # List endpoints return camelCase format (districtId, districtName)
        assert any(d["districtId"] == district["id"] for d in districts)
        pass_test(f"{len(districts)} districts found")
    except Exception as e:
        fail_test(str(e))
    
    # UPDATE
    print_test("UPDATE district")
    try:
        update_data = {"name": "Updated Integration District"}
        response = requests.patch(
            f"{BASE_URL}/metadata/address/districts/{district['id']}",
            json=update_data,
            headers=headers,
        )
        response.raise_for_status()
        updated = response.json()
        assert updated["name"] == update_data["name"]
        district = updated
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    return district


def test_sub_districts_crud(
    headers: dict[str, str], district: dict[str, Any]
) -> dict[str, Any]:
    """Test all CRUD operations for sub-districts."""
    print_header("SUB-DISTRICTS - CRUD Operations")
    
    sub_district_data = {
        "name": "Test Integration Sub-District",
        "code": "TISD",
        "district_id": district["id"],
        "is_active": True,
    }
    
    # CREATE
    print_test("CREATE sub-district")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/address/sub-districts",
            json=sub_district_data,
            headers=headers,
        )
        response.raise_for_status()
        sub_district = response.json()
        assert "id" in sub_district
        assert sub_district["name"] == sub_district_data["name"]
        assert sub_district["district_id"] == district["id"]
        pass_test(f"ID: {sub_district['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}
    
    # READ - Get by ID
    print_test("READ sub-district by ID")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/address/sub-districts/{sub_district['id']}"
        )
        response.raise_for_status()
        fetched = response.json()
        assert fetched["id"] == sub_district["id"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # READ - Get sub-districts by district
    print_test("READ sub-districts by district")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/address/district/{district['id']}/sub-districts"
        )
        response.raise_for_status()
        sub_districts = response.json()
        assert isinstance(sub_districts, list)
        # List endpoints return camelCase format (tehsilId, tehsilName)
        assert any(sd["tehsilId"] == sub_district["id"] for sd in sub_districts)
        pass_test(f"{len(sub_districts)} sub-districts found")
    except Exception as e:
        fail_test(str(e))
    
    # UPDATE
    print_test("UPDATE sub-district")
    try:
        update_data = {"name": "Updated Integration Sub-District"}
        response = requests.patch(
            f"{BASE_URL}/metadata/address/sub-districts/{sub_district['id']}",
            json=update_data,
            headers=headers,
        )
        response.raise_for_status()
        updated = response.json()
        assert updated["name"] == update_data["name"]
        sub_district = updated
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    return sub_district


def test_localities_crud(
    headers: dict[str, str], sub_district: dict[str, Any]
) -> dict[str, Any]:
    """Test all CRUD operations for localities."""
    print_header("LOCALITIES - CRUD Operations")
    
    locality_data = {
        "name": "Test Integration Locality",
        "code": "TIL",
        "sub_district_id": sub_district["id"],
        "is_active": True,
    }
    
    # CREATE
    print_test("CREATE locality")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/address/localities",
            json=locality_data,
            headers=headers,
        )
        response.raise_for_status()
        locality = response.json()
        assert "id" in locality
        assert locality["name"] == locality_data["name"]
        assert locality["sub_district_id"] == sub_district["id"]
        pass_test(f"ID: {locality['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}
    
    # READ - Get by ID
    print_test("READ locality by ID")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/address/localities/{locality['id']}"
        )
        response.raise_for_status()
        fetched = response.json()
        assert fetched["id"] == locality["id"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # READ - Get localities by sub-district
    print_test("READ localities by sub-district")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/address/sub-district/{sub_district['id']}/localities"
        )
        response.raise_for_status()
        localities = response.json()
        assert isinstance(localities, list)
        # List endpoints return camelCase format (localityId, localityName)
        assert any(l["localityId"] == locality["id"] for l in localities)
        pass_test(f"{len(localities)} localities found")
    except Exception as e:
        fail_test(str(e))
    
    # UPDATE
    print_test("UPDATE locality")
    try:
        update_data = {"name": "Updated Integration Locality"}
        response = requests.patch(
            f"{BASE_URL}/metadata/address/localities/{locality['id']}",
            json=update_data,
            headers=headers,
        )
        response.raise_for_status()
        updated = response.json()
        assert updated["name"] == update_data["name"]
        locality = updated
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    return locality


def test_delete_operations(
    headers: dict[str, str],
    country: dict[str, Any],
    state: dict[str, Any],
    district: dict[str, Any],
    sub_district: dict[str, Any],
    locality: dict[str, Any],
) -> None:
    """Test DELETE operations for all components."""
    print_header("DELETE Operations")
    
    # Delete in reverse hierarchical order
    print_test("DELETE locality")
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/address/localities/{locality['id']}",
            headers=headers,
        )
        response.raise_for_status()
        assert response.json()["message"] == "Locality deleted successfully"
        
        # Verify deletion
        verify = requests.get(
            f"{BASE_URL}/metadata/address/localities/{locality['id']}"
        )
        assert verify.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("DELETE sub-district")
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/address/sub-districts/{sub_district['id']}",
            headers=headers,
        )
        response.raise_for_status()
        assert response.json()["message"] == "Sub-district deleted successfully"
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("DELETE district")
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/address/districts/{district['id']}",
            headers=headers,
        )
        response.raise_for_status()
        assert response.json()["message"] == "District deleted successfully"
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("DELETE state")
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/address/states/{state['id']}",
            headers=headers,
        )
        response.raise_for_status()
        assert response.json()["message"] == "State deleted successfully"
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("DELETE country")
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/address/countries/{country['id']}",
            headers=headers,
        )
        response.raise_for_status()
        assert response.json()["message"] == "Country deleted successfully"
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # Test error handling
    print_test("DELETE non-existent resource (404)")
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.delete(
            f"{BASE_URL}/metadata/address/countries/{fake_id}",
            headers=headers,
        )
        assert response.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("DELETE without authentication (401)")
    try:
        # Create a temporary country to test auth
        temp_country = requests.post(
            f"{BASE_URL}/metadata/address/countries",
            json={"name": "Temp Country", "code": "TMP", "is_active": True},
            headers=headers,
        ).json()
        
        # Try to delete without auth
        response = requests.delete(
            f"{BASE_URL}/metadata/address/countries/{temp_country['id']}"
        )
        assert response.status_code == 401
        
        # Clean up
        requests.delete(
            f"{BASE_URL}/metadata/address/countries/{temp_country['id']}",
            headers=headers,
        )
        pass_test()
    except Exception as e:
        fail_test(str(e))


def test_authentication() -> None:
    """Test authentication requirements."""
    print_header("AUTHENTICATION Tests")
    
    print_test("POST without auth returns 401")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/address/countries",
            json={"name": "Test", "code": "TST", "is_active": True},
        )
        assert response.status_code == 401
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("PATCH without auth returns 401")
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.patch(
            f"{BASE_URL}/metadata/address/countries/{fake_id}",
            json={"name": "Test"},
        )
        assert response.status_code == 401
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("DELETE without auth returns 401")
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.delete(
            f"{BASE_URL}/metadata/address/countries/{fake_id}"
        )
        assert response.status_code == 401
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("GET endpoints are public (no auth required)")
    try:
        response = requests.get(f"{BASE_URL}/metadata/address/countries")
        assert response.status_code == 200
        pass_test()
    except Exception as e:
        fail_test(str(e))


def main() -> None:
    """Run all integration tests."""
    print_header(f"Address Metadata API - Full Integration Test Suite")
    print(f"Base URL: {BASE_URL}")
    print(f"Admin: {ADMIN_EMAIL}")
    
    # Get authentication
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test authentication requirements
    test_authentication()
    
    # Test CRUD for each component
    country = test_countries_crud(headers)
    if not country:
        print("\n❌ Country tests failed. Cannot continue with dependent tests.")
        sys.exit(1)
    
    state = test_states_crud(headers, country)
    if not state:
        print("\n❌ State tests failed. Cannot continue with dependent tests.")
        sys.exit(1)
    
    district = test_districts_crud(headers, state)
    if not district:
        print("\n❌ District tests failed. Cannot continue with dependent tests.")
        sys.exit(1)
    
    sub_district = test_sub_districts_crud(headers, district)
    if not sub_district:
        print("\n❌ Sub-district tests failed. Cannot continue with dependent tests.")
        sys.exit(1)
    
    locality = test_localities_crud(headers, sub_district)
    if not locality:
        print("\n❌ Locality tests failed. Cannot continue with dependent tests.")
        sys.exit(1)
    
    # Test delete operations
    test_delete_operations(headers, country, state, district, sub_district, locality)
    
    # Print summary
    print_header("TEST SUMMARY")
    total_tests = tests_passed + tests_failed
    print(f"Total Tests: {total_tests}")
    print(f"✓ Passed: {tests_passed}")
    print(f"✗ Failed: {tests_failed}")
    print(f"Success Rate: {(tests_passed/total_tests*100):.1f}%")
    
    if tests_failed == 0:
        print("\n" + "=" * 70)
        print("  🎉 ALL TESTS PASSED! 🎉")
        print("=" * 70)
        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print(f"  ⚠️  {tests_failed} TEST(S) FAILED")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)

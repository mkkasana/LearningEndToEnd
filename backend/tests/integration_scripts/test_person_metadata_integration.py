#!/usr/bin/env python3
"""
Comprehensive Integration Test for Person API

Tests all CRUD operations for:
- Professions (metadata)
- Genders (metadata)
- Person profiles
- Person addresses
- Person professions
- Person relationships

Usage:
    python3 backend/tests/integration_scripts/test_person_metadata_integration.py [port]
"""

import sys
import uuid

import requests

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
BASE_URL = f"http://localhost:{PORT}/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "changethis"

tests_passed = 0
tests_failed = 0


def print_header(text: str) -> None:
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}\n")


def print_test(text: str) -> None:
    print(f"→ {text}...", end=" ", flush=True)


def pass_test(message: str = "") -> None:
    global tests_passed
    tests_passed += 1
    suffix = f" ({message})" if message else ""
    print(f"✓{suffix}")


def fail_test(message: str) -> None:
    global tests_failed
    tests_failed += 1
    print(f"✗ FAILED: {message}")


def get_auth_token() -> str:
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


def test_professions(headers: dict[str, str]) -> None:
    print_header("PROFESSIONS - CRUD Operations")

    # CREATE
    print_test("CREATE profession")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/person/professions",
            json={
                "name": "Test Engineer",
                "description": "Testing professional",
                "weight": 50,
                "is_active": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        profession = response.json()
        assert "id" in profession
        pass_test(f"ID: {profession['id']}")
    except Exception as e:
        fail_test(str(e))
        return

    # READ
    print_test("READ profession by ID")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/person/professions/{profession['id']}"
        )
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # UPDATE
    print_test("UPDATE profession")
    try:
        response = requests.patch(
            f"{BASE_URL}/metadata/person/professions/{profession['id']}",
            json={"name": "Senior Test Engineer"},
            headers=headers,
        )
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # DELETE
    print_test("DELETE profession")
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/person/professions/{profession['id']}",
            headers=headers,
        )
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))


def test_genders(headers: dict[str, str]) -> None:
    print_header("GENDERS - CRUD Operations")

    # CREATE
    print_test("CREATE gender")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/person/genders",
            json={
                "name": "Test Gender",
                "code": "TG",
                "description": "Test gender option",
                "is_active": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        gender = response.json()
        assert "id" in gender
        pass_test(f"ID: {gender['id']}")
    except Exception as e:
        fail_test(str(e))
        return

    # READ
    print_test("READ gender by ID")
    try:
        response = requests.get(f"{BASE_URL}/metadata/person/genders/{gender['id']}")
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # READ ALL
    print_test("READ all genders")
    try:
        response = requests.get(f"{BASE_URL}/metadata/person/genders")
        response.raise_for_status()
        genders = response.json()
        assert isinstance(genders, list)
        pass_test(f"Found {len(genders)} genders")
    except Exception as e:
        fail_test(str(e))

    # UPDATE
    print_test("UPDATE gender")
    try:
        response = requests.patch(
            f"{BASE_URL}/metadata/person/genders/{gender['id']}",
            json={"name": "Updated Test Gender"},
            headers=headers,
        )
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # DELETE
    print_test("DELETE gender")
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/person/genders/{gender['id']}", headers=headers
        )
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # VERIFY DELETE
    print_test("VERIFY deletion (404)")
    try:
        response = requests.get(f"{BASE_URL}/metadata/person/genders/{gender['id']}")
        assert response.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))


def test_validations(headers: dict[str, str]) -> None:
    print_header("VALIDATION Tests")

    # Duplicate code
    print_test("CREATE gender with duplicate code (should fail)")
    try:
        requests.post(
            f"{BASE_URL}/metadata/person/genders",
            json={"name": "Test1", "code": "DUP", "is_active": True},
            headers=headers,
        )
        response = requests.post(
            f"{BASE_URL}/metadata/person/genders",
            json={"name": "Test2", "code": "DUP", "is_active": True},
            headers=headers,
        )
        assert response.status_code == 400
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # No auth
    print_test("CREATE without auth (should fail)")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/person/genders",
            json={"name": "Test", "code": "T", "is_active": True},
        )
        assert response.status_code == 401
        pass_test()
    except Exception as e:
        fail_test(str(e))


def test_person_profile(headers: dict[str, str]) -> None:
    print_header("PERSON PROFILE - CRUD Operations")

    # Get gender for person creation
    print_test("GET gender for person")
    try:
        response = requests.get(f"{BASE_URL}/metadata/person/genders")
        response.raise_for_status()
        genders = response.json()
        assert len(genders) > 0
        gender_id = genders[0]["genderId"]
        pass_test(f"Using gender: {gender_id}")
    except Exception as e:
        fail_test(str(e))
        return

    # Get current user
    print_test("GET current user")
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        response.raise_for_status()
        user = response.json()
        user_id = user["id"]
        pass_test(f"User ID: {user_id}")
    except Exception as e:
        fail_test(str(e))
        return

    # Delete existing person if any
    print_test("DELETE existing person (if any)")
    try:
        response = requests.delete(f"{BASE_URL}/person/me", headers=headers)
        if response.status_code in [200, 404]:
            pass_test()
        else:
            fail_test(f"Unexpected status: {response.status_code}")
    except Exception as e:
        fail_test(str(e))

    # CREATE person profile
    print_test("CREATE person profile")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me",
            json={
                "user_id": user_id,
                "first_name": "Test",
                "middle_name": "Integration",
                "last_name": "User",
                "gender_id": gender_id,
                "date_of_birth": "1990-01-01",
            },
            headers=headers,
        )
        response.raise_for_status()
        person = response.json()
        assert person["first_name"] == "Test"
        pass_test()
    except Exception as e:
        fail_test(str(e))
        return

    # READ person profile
    print_test("READ person profile")
    try:
        response = requests.get(f"{BASE_URL}/person/me", headers=headers)
        response.raise_for_status()
        person = response.json()
        assert person["first_name"] == "Test"
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # UPDATE person profile
    print_test("UPDATE person profile")
    try:
        response = requests.patch(
            f"{BASE_URL}/person/me",
            json={"middle_name": "Updated"},
            headers=headers,
        )
        response.raise_for_status()
        person = response.json()
        assert person["middle_name"] == "Updated"
        pass_test()
    except Exception as e:
        fail_test(str(e))


def test_person_addresses(headers: dict[str, str]) -> None:
    print_header("PERSON ADDRESSES - CRUD Operations")

    # Get country for address
    print_test("GET country for address")
    try:
        response = requests.get(f"{BASE_URL}/metadata/address/countries")
        response.raise_for_status()
        countries = response.json()
        assert len(countries) > 0
        country_id = countries[0]["countryId"]
        pass_test(f"Using country: {country_id}")
    except Exception as e:
        fail_test(str(e))
        return

    # CREATE address
    print_test("CREATE address")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/addresses",
            json={
                "country_id": country_id,
                "address_line": "123 Test Street",
                "start_date": "2024-01-01",
                "is_current": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        address = response.json()
        assert address["address_line"] == "123 Test Street"
        assert address["is_current"] is True
        address_id = address["id"]
        pass_test(f"ID: {address_id}")
    except Exception as e:
        fail_test(str(e))
        return

    # READ all addresses
    print_test("READ all addresses")
    try:
        response = requests.get(f"{BASE_URL}/person/me/addresses", headers=headers)
        response.raise_for_status()
        addresses = response.json()
        assert len(addresses) == 1
        pass_test(f"Found {len(addresses)} address")
    except Exception as e:
        fail_test(str(e))

    # READ address by ID
    print_test("READ address by ID")
    try:
        response = requests.get(
            f"{BASE_URL}/person/me/addresses/{address_id}", headers=headers
        )
        response.raise_for_status()
        address = response.json()
        assert address["id"] == address_id
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # UPDATE address
    print_test("UPDATE address")
    try:
        response = requests.patch(
            f"{BASE_URL}/person/me/addresses/{address_id}",
            json={"address_line": "456 Updated Street"},
            headers=headers,
        )
        response.raise_for_status()
        address = response.json()
        assert address["address_line"] == "456 Updated Street"
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # CREATE second address (should clear is_current from first)
    print_test("CREATE second address (auto-clear is_current)")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/addresses",
            json={
                "country_id": country_id,
                "address_line": "789 New Street",
                "start_date": "2024-06-01",
                "is_current": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        address2 = response.json()
        assert address2["is_current"] is True
        address2_id = address2["id"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
        return

    # Verify first address is no longer current
    print_test("VERIFY first address is_current cleared")
    try:
        response = requests.get(
            f"{BASE_URL}/person/me/addresses/{address_id}", headers=headers
        )
        response.raise_for_status()
        address = response.json()
        assert address["is_current"] is False
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # DELETE addresses
    print_test("DELETE first address")
    try:
        response = requests.delete(
            f"{BASE_URL}/person/me/addresses/{address_id}", headers=headers
        )
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))

    print_test("DELETE second address")
    try:
        response = requests.delete(
            f"{BASE_URL}/person/me/addresses/{address2_id}", headers=headers
        )
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # VERIFY empty
    print_test("VERIFY addresses deleted")
    try:
        response = requests.get(f"{BASE_URL}/person/me/addresses", headers=headers)
        response.raise_for_status()
        addresses = response.json()
        assert len(addresses) == 0
        pass_test()
    except Exception as e:
        fail_test(str(e))


def test_person_professions(headers: dict[str, str]) -> None:
    print_header("PERSON PROFESSIONS - CRUD Operations")

    # Get profession metadata
    print_test("GET profession metadata")
    try:
        response = requests.get(f"{BASE_URL}/metadata/person/professions")
        response.raise_for_status()
        professions = response.json()
        if not professions:
            # Create one
            response = requests.post(
                f"{BASE_URL}/metadata/person/professions",
                json={"name": "Test Engineer", "weight": 100, "is_active": True},
                headers=headers,
            )
            response.raise_for_status()
            professions = [response.json()]
        profession_id = professions[0]["professionId"]
        pass_test(f"Using profession: {profession_id}")
    except Exception as e:
        fail_test(str(e))
        return

    # CREATE profession association
    print_test("CREATE profession association")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/professions",
            json={
                "profession_id": profession_id,
                "start_date": "2024-01-01",
                "is_current": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        prof_assoc = response.json()
        assert prof_assoc["is_current"] is True
        prof_assoc_id = prof_assoc["id"]
        pass_test(f"ID: {prof_assoc_id}")
    except Exception as e:
        fail_test(str(e))
        return

    # READ all professions
    print_test("READ all professions")
    try:
        response = requests.get(f"{BASE_URL}/person/me/professions", headers=headers)
        response.raise_for_status()
        prof_assocs = response.json()
        assert len(prof_assocs) == 1
        pass_test(f"Found {len(prof_assocs)} profession")
    except Exception as e:
        fail_test(str(e))

    # READ profession by ID
    print_test("READ profession by ID")
    try:
        response = requests.get(
            f"{BASE_URL}/person/me/professions/{prof_assoc_id}", headers=headers
        )
        response.raise_for_status()
        prof_assoc = response.json()
        assert prof_assoc["id"] == prof_assoc_id
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # UPDATE profession
    print_test("UPDATE profession")
    try:
        response = requests.patch(
            f"{BASE_URL}/person/me/professions/{prof_assoc_id}",
            json={"end_date": "2024-12-31"},
            headers=headers,
        )
        response.raise_for_status()
        prof_assoc = response.json()
        assert prof_assoc["end_date"] == "2024-12-31"
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # CREATE second profession (should clear is_current from first)
    print_test("CREATE second profession (auto-clear is_current)")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/professions",
            json={
                "profession_id": profession_id,
                "start_date": "2025-01-01",
                "is_current": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        prof_assoc2 = response.json()
        assert prof_assoc2["is_current"] is True
        prof_assoc2_id = prof_assoc2["id"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
        return

    # Verify first profession is no longer current
    print_test("VERIFY first profession is_current cleared")
    try:
        response = requests.get(
            f"{BASE_URL}/person/me/professions/{prof_assoc_id}", headers=headers
        )
        response.raise_for_status()
        prof_assoc = response.json()
        assert prof_assoc["is_current"] is False
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # DELETE professions
    print_test("DELETE first profession")
    try:
        response = requests.delete(
            f"{BASE_URL}/person/me/professions/{prof_assoc_id}", headers=headers
        )
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))

    print_test("DELETE second profession")
    try:
        response = requests.delete(
            f"{BASE_URL}/person/me/professions/{prof_assoc2_id}", headers=headers
        )
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # VERIFY empty
    print_test("VERIFY professions deleted")
    try:
        response = requests.get(f"{BASE_URL}/person/me/professions", headers=headers)
        response.raise_for_status()
        prof_assocs = response.json()
        assert len(prof_assocs) == 0
        pass_test()
    except Exception as e:
        fail_test(str(e))


def test_person_relationships(headers: dict[str, str]) -> None:
    print_header("PERSON RELATIONSHIPS - CRUD Operations")

    # Get current user ID for related person
    print_test("GET current user for related person")
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        response.raise_for_status()
        user = response.json()
        related_person_id = user["id"]
        pass_test(f"Using person: {related_person_id}")
    except Exception as e:
        fail_test(str(e))
        return

    # CREATE relationship
    print_test("CREATE relationship")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/relationships",
            json={
                "related_person_id": related_person_id,
                "relationship_type": "rel-6a0ede824d107",  # SPOUSE
                "start_date": "2020-01-01",
                "is_active": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        relationship = response.json()
        assert relationship["is_active"] is True
        relationship_id = relationship["id"]
        pass_test(f"ID: {relationship_id}")
    except Exception as e:
        fail_test(str(e))
        return

    # READ all relationships
    print_test("READ all relationships")
    try:
        response = requests.get(f"{BASE_URL}/person/me/relationships", headers=headers)
        response.raise_for_status()
        relationships = response.json()
        assert len(relationships) == 1
        pass_test(f"Found {len(relationships)} relationship")
    except Exception as e:
        fail_test(str(e))

    # READ relationship by ID
    print_test("READ relationship by ID")
    try:
        response = requests.get(
            f"{BASE_URL}/person/me/relationships/{relationship_id}", headers=headers
        )
        response.raise_for_status()
        relationship = response.json()
        assert relationship["id"] == relationship_id
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # UPDATE relationship
    print_test("UPDATE relationship")
    try:
        response = requests.patch(
            f"{BASE_URL}/person/me/relationships/{relationship_id}",
            json={"end_date": "2024-12-31", "is_active": False},
            headers=headers,
        )
        response.raise_for_status()
        relationship = response.json()
        assert relationship["end_date"] == "2024-12-31"
        assert relationship["is_active"] is False
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # DELETE relationship
    print_test("DELETE relationship")
    try:
        response = requests.delete(
            f"{BASE_URL}/person/me/relationships/{relationship_id}", headers=headers
        )
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # VERIFY empty
    print_test("VERIFY relationships deleted")
    try:
        response = requests.get(f"{BASE_URL}/person/me/relationships", headers=headers)
        response.raise_for_status()
        relationships = response.json()
        assert len(relationships) == 0
        pass_test()
    except Exception as e:
        fail_test(str(e))


def main() -> None:
    print_header("PERSON API - INTEGRATION TEST")
    print(f"Testing against: {BASE_URL}")

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    test_professions(headers)
    test_genders(headers)
    test_validations(headers)
    test_person_profile(headers)
    test_person_addresses(headers)
    test_person_professions(headers)
    test_person_relationships(headers)

    print_header("TEST SUMMARY")
    total_tests = tests_passed + tests_failed
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {tests_passed} ✓")
    print(f"Failed: {tests_failed} ✗")

    if tests_failed > 0:
        print("\n❌ Some tests failed!")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()

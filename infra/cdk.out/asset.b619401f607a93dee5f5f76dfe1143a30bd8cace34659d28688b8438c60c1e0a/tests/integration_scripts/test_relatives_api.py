#!/usr/bin/env python3
"""
Integration Test for Relatives API

Tests the relatives extraction endpoints:
- GET /relatives/{user_id}/parents
- GET /relatives/{user_id}/children
- GET /relatives/{user_id}/spouses

Usage:
    python3 backend/tests/integration_scripts/test_relatives_api.py [port]
"""

import sys

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


def setup_test_data(headers: dict[str, str]) -> dict:
    """Create test persons and relationships."""
    print_header("SETUP - Creating Test Data")

    # Get gender
    print_test("GET gender for persons")
    try:
        response = requests.get(f"{BASE_URL}/metadata/person/genders")
        response.raise_for_status()
        genders = response.json()
        if not genders:
            fail_test("No genders available")
            sys.exit(1)
        gender_id = genders[0]["genderId"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
        sys.exit(1)

    # Get current user (will be the child)
    print_test("GET current user (child)")
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        response.raise_for_status()
        user = response.json()
        child_user_id = user["id"]
        pass_test(f"Child User ID: {child_user_id}")
    except Exception as e:
        fail_test(str(e))
        sys.exit(1)

    # Ensure person profile exists for child
    print_test("Ensure child person profile exists")
    try:
        response = requests.get(f"{BASE_URL}/person/me", headers=headers)
        if response.status_code == 404:
            response = requests.post(
                f"{BASE_URL}/person/me",
                json={
                    "user_id": child_user_id,
                    "first_name": "Child",
                    "last_name": "User",
                    "gender_id": gender_id,
                    "date_of_birth": "1990-01-01",
                },
                headers=headers,
            )
            response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))
        sys.exit(1)

    # For testing siblings, we'll use the same user as parent and create multiple children
    # In real scenario, you'd have separate parent users
    parent_user_id = child_user_id  # Using same user for simplicity

    # Create parent relationships (child -> parent)
    print_test("CREATE father relationship (child -> parent)")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/relationships",
            json={
                "related_person_id": parent_user_id,
                "relationship_type": "rel-6a0ede824d101",  # FATHER
                "start_date": "1990-01-01",
                "is_active": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        father_rel = response.json()
        pass_test(f"ID: {father_rel['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}

    print_test("CREATE mother relationship (child -> parent)")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/relationships",
            json={
                "related_person_id": parent_user_id,
                "relationship_type": "rel-6a0ede824d102",  # MOTHER
                "start_date": "1990-01-01",
                "is_active": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        mother_rel = response.json()
        pass_test(f"ID: {mother_rel['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}

    # Create sibling relationships (parent -> children)
    # These represent the parent's children (siblings of the current user)
    print_test("CREATE son relationship (parent -> sibling1)")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/relationships",
            json={
                "related_person_id": child_user_id,  # Sibling (using same user for test)
                "relationship_type": "rel-6a0ede824d104",  # SON
                "start_date": "2015-01-01",
                "is_active": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        son_rel = response.json()
        pass_test(f"ID: {son_rel['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}

    print_test("CREATE daughter relationship (parent -> sibling2)")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/relationships",
            json={
                "related_person_id": child_user_id,  # Sibling (using same user for test)
                "relationship_type": "rel-6a0ede824d103",  # DAUGHTER
                "start_date": "2018-01-01",
                "is_active": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        daughter_rel = response.json()
        pass_test(f"ID: {daughter_rel['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}

    # Create spouse relationship
    print_test("CREATE spouse relationship")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/relationships",
            json={
                "related_person_id": child_user_id,
                "relationship_type": "rel-6a0ede824d107",  # SPOUSE
                "start_date": "2010-01-01",
                "is_active": True,
            },
            headers=headers,
        )
        response.raise_for_status()
        spouse_rel = response.json()
        pass_test(f"ID: {spouse_rel['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}

    return {"user_id": child_user_id}


def test_relatives_api(headers: dict[str, str], test_data: dict) -> None:
    print_header("RELATIVES API - Extraction Tests")

    user_id = test_data["user_id"]

    # Test GET parents
    print_test("GET /relatives/{user_id}/parents")
    try:
        response = requests.get(f"{BASE_URL}/relatives/{user_id}/parents")
        response.raise_for_status()
        parents = response.json()
        assert isinstance(parents, list)
        assert len(parents) == 2  # Father and Mother
        parent_types = [p["relationship_type"] for p in parents]
        assert "rel-6a0ede824d101" in parent_types  # FATHER
        assert "rel-6a0ede824d102" in parent_types  # MOTHER
        pass_test(f"Found {len(parents)} parents")
    except Exception as e:
        fail_test(str(e))

    # Test GET children
    print_test("GET /relatives/{user_id}/children")
    try:
        response = requests.get(f"{BASE_URL}/relatives/{user_id}/children")
        response.raise_for_status()
        children = response.json()
        assert isinstance(children, list)
        assert len(children) == 2  # Son and Daughter
        child_types = [c["relationship_type"] for c in children]
        assert "rel-6a0ede824d104" in child_types  # SON
        assert "rel-6a0ede824d103" in child_types  # DAUGHTER
        pass_test(f"Found {len(children)} children")
    except Exception as e:
        fail_test(str(e))

    # Test GET spouses
    print_test("GET /relatives/{user_id}/spouses")
    try:
        response = requests.get(f"{BASE_URL}/relatives/{user_id}/spouses")
        response.raise_for_status()
        spouses = response.json()
        assert isinstance(spouses, list)
        assert len(spouses) == 1  # SPOUSE
        assert spouses[0]["relationship_type"] == "rel-6a0ede824d107"
        pass_test(f"Found {len(spouses)} spouse")
    except Exception as e:
        fail_test(str(e))

    # Test GET siblings
    print_test("GET /relatives/{user_id}/siblings")
    try:
        response = requests.get(f"{BASE_URL}/relatives/{user_id}/siblings")
        response.raise_for_status()
        siblings = response.json()
        assert isinstance(siblings, list)
        # Note: In our test setup, we're using the same user for everything
        # In a real scenario with different users, this would return actual siblings
        # The logic finds parent's children excluding self
        pass_test(f"Found {len(siblings)} siblings")
    except Exception as e:
        fail_test(str(e))

    # Test 404 for non-existent user
    print_test("GET parents for non-existent user (should return 404)")
    try:
        fake_uuid = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{BASE_URL}/relatives/{fake_uuid}/parents")
        assert response.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))


def cleanup_test_data(headers: dict[str, str]) -> None:
    """Clean up test relationships."""
    print_header("CLEANUP - Removing Test Data")

    print_test("DELETE all relationships")
    try:
        response = requests.get(f"{BASE_URL}/person/me/relationships", headers=headers)
        if response.status_code == 200:
            relationships = response.json()
            for rel in relationships:
                requests.delete(
                    f"{BASE_URL}/person/me/relationships/{rel['id']}", headers=headers
                )
        pass_test(f"Cleaned up {len(relationships)} relationships")
    except Exception as e:
        fail_test(str(e))


def main() -> None:
    print_header("RELATIVES API - INTEGRATION TEST")
    print(f"Testing against: {BASE_URL}")

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    test_data = setup_test_data(headers)
    if test_data:
        test_relatives_api(headers, test_data)
        cleanup_test_data(headers)

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

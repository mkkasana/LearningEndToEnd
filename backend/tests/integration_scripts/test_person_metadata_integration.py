#!/usr/bin/env python3
"""
Comprehensive Integration Test for Person Metadata API

Tests all CRUD operations for:
- Professions
- Genders

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


def main() -> None:
    print_header("PERSON METADATA API - INTEGRATION TEST")
    print(f"Testing against: {BASE_URL}")

    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    test_professions(headers)
    test_genders(headers)
    test_validations(headers)

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

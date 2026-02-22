#!/usr/bin/env python3
"""
Integration Test for Person Metadata CRUD API

Tests all CRUD operations for person metadata (profile image, bio, etc.)

Usage:
    python3 backend/tests/integration_scripts/test_person_metadata_crud.py [port]
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


def setup_person_profile(headers: dict[str, str]) -> None:
    """Ensure person profile exists for testing."""
    print_test("Setting up person profile")
    try:
        # Get gender
        response = requests.get(f"{BASE_URL}/metadata/person/genders")
        response.raise_for_status()
        genders = response.json()
        if not genders:
            fail_test("No genders available")
            sys.exit(1)
        gender_id = genders[0]["genderId"]

        # Get current user
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        response.raise_for_status()
        user = response.json()
        user_id = user["id"]

        # Check if person exists
        response = requests.get(f"{BASE_URL}/person/me", headers=headers)
        if response.status_code == 404:
            # Create person
            response = requests.post(
                f"{BASE_URL}/person/me",
                json={
                    "user_id": user_id,
                    "first_name": "Test",
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


def test_metadata_crud(headers: dict[str, str]) -> None:
    print_header("PERSON METADATA - CRUD Operations")

    # Clean up any existing metadata
    print_test("Cleanup existing metadata")
    try:
        response = requests.delete(f"{BASE_URL}/person/me/metadata", headers=headers)
        if response.status_code in [200, 404]:
            pass_test()
        else:
            fail_test(f"Unexpected status: {response.status_code}")
    except Exception as e:
        fail_test(str(e))

    # CREATE metadata
    print_test("CREATE person metadata")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/metadata",
            json={
                "profile_image_url": "https://example.com/profile.jpg",
                "bio": "This is my test biography",
            },
            headers=headers,
        )
        response.raise_for_status()
        metadata = response.json()
        assert "id" in metadata
        assert metadata["profile_image_url"] == "https://example.com/profile.jpg"
        assert metadata["bio"] == "This is my test biography"
        assert "person_id" in metadata
        assert "created_at" in metadata
        assert "updated_at" in metadata
        pass_test(f"ID: {metadata['id']}")
    except Exception as e:
        fail_test(str(e))
        return

    # READ metadata
    print_test("READ person metadata")
    try:
        response = requests.get(f"{BASE_URL}/person/me/metadata", headers=headers)
        response.raise_for_status()
        metadata = response.json()
        assert metadata["profile_image_url"] == "https://example.com/profile.jpg"
        assert metadata["bio"] == "This is my test biography"
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # UPDATE metadata - profile image only
    print_test("UPDATE profile image")
    try:
        response = requests.patch(
            f"{BASE_URL}/person/me/metadata",
            json={"profile_image_url": "https://example.com/new-profile.jpg"},
            headers=headers,
        )
        response.raise_for_status()
        metadata = response.json()
        assert metadata["profile_image_url"] == "https://example.com/new-profile.jpg"
        assert metadata["bio"] == "This is my test biography"  # Should remain unchanged
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # UPDATE metadata - bio only
    print_test("UPDATE bio")
    try:
        response = requests.patch(
            f"{BASE_URL}/person/me/metadata",
            json={"bio": "Updated biography with more details"},
            headers=headers,
        )
        response.raise_for_status()
        metadata = response.json()
        assert metadata["profile_image_url"] == "https://example.com/new-profile.jpg"
        assert metadata["bio"] == "Updated biography with more details"
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # UPDATE metadata - both fields
    print_test("UPDATE both fields")
    try:
        response = requests.patch(
            f"{BASE_URL}/person/me/metadata",
            json={
                "profile_image_url": "https://example.com/final-profile.jpg",
                "bio": "Final biography version",
            },
            headers=headers,
        )
        response.raise_for_status()
        metadata = response.json()
        assert metadata["profile_image_url"] == "https://example.com/final-profile.jpg"
        assert metadata["bio"] == "Final biography version"
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # UPDATE metadata - clear bio
    print_test("UPDATE to clear bio (set to null)")
    try:
        response = requests.patch(
            f"{BASE_URL}/person/me/metadata",
            json={"bio": None},
            headers=headers,
        )
        response.raise_for_status()
        metadata = response.json()
        assert metadata["bio"] is None
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # DELETE metadata
    print_test("DELETE person metadata")
    try:
        response = requests.delete(f"{BASE_URL}/person/me/metadata", headers=headers)
        response.raise_for_status()
        result = response.json()
        assert "message" in result
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # VERIFY deletion (404)
    print_test("VERIFY deletion (should return 404)")
    try:
        response = requests.get(f"{BASE_URL}/person/me/metadata", headers=headers)
        assert response.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))


def test_validations(headers: dict[str, str]) -> None:
    print_header("VALIDATION Tests")

    # Ensure no metadata exists
    requests.delete(f"{BASE_URL}/person/me/metadata", headers=headers)

    # CREATE duplicate metadata (should fail)
    print_test("CREATE duplicate metadata (should fail)")
    try:
        # Create first
        response = requests.post(
            f"{BASE_URL}/person/me/metadata",
            json={"profile_image_url": "https://example.com/test.jpg"},
            headers=headers,
        )
        response.raise_for_status()

        # Try to create second (should fail)
        response = requests.post(
            f"{BASE_URL}/person/me/metadata",
            json={"profile_image_url": "https://example.com/test2.jpg"},
            headers=headers,
        )
        assert response.status_code == 400
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # UPDATE non-existent metadata (should fail)
    print_test("UPDATE after deletion (should fail)")
    try:
        # Delete metadata
        requests.delete(f"{BASE_URL}/person/me/metadata", headers=headers)

        # Try to update
        response = requests.patch(
            f"{BASE_URL}/person/me/metadata",
            json={"bio": "Test"},
            headers=headers,
        )
        assert response.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))

    # No auth
    print_test("CREATE without auth (should fail)")
    try:
        response = requests.post(
            f"{BASE_URL}/person/me/metadata",
            json={"profile_image_url": "https://example.com/test.jpg"},
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

    setup_person_profile(headers)
    test_metadata_crud(headers)
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

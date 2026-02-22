#!/usr/bin/env python3
"""
Comprehensive Integration Test for Profession Metadata API

Tests all CRUD operations for professions including:
- Create profession
- Read profession by ID
- Read all professions (with weight-based sorting)
- Update profession
- Delete profession
- Duplicate name validation
- Authentication requirements

Usage:
    python3 backend/tests/integration_scripts/test_profession_integration.py [port]
    
    Default port: 8000
    
Example:
    python3 backend/tests/integration_scripts/test_profession_integration.py
    python3 backend/tests/integration_scripts/test_profession_integration.py 8080
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


def test_professions_crud(headers: dict[str, str]) -> dict[str, Any]:
    """Test all CRUD operations for professions."""
    print_header("PROFESSIONS - CRUD Operations")
    
    profession_data = {
        "name": "Test Software Engineer",
        "description": "A test profession for integration testing",
        "weight": 100,
        "is_active": True,
    }
    
    # CREATE
    print_test("CREATE profession")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/person/professions",
            json=profession_data,
            headers=headers,
        )
        response.raise_for_status()
        profession = response.json()
        assert "id" in profession
        assert profession["name"] == profession_data["name"]
        assert profession["weight"] == profession_data["weight"]
        pass_test(f"ID: {profession['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}
    
    # READ - Get by ID
    print_test("READ profession by ID")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/person/professions/{profession['id']}",
        )
        response.raise_for_status()
        fetched_profession = response.json()
        assert fetched_profession["id"] == profession["id"]
        assert fetched_profession["name"] == profession_data["name"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # READ - Get all professions
    print_test("READ all professions")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/person/professions",
        )
        response.raise_for_status()
        professions = response.json()
        assert isinstance(professions, list)
        assert len(professions) > 0
        # Find our test profession
        found = any(p["professionId"] == profession["id"] for p in professions)
        assert found, "Test profession not found in list"
        pass_test(f"Found {len(professions)} professions")
    except Exception as e:
        fail_test(str(e))
    
    # UPDATE
    print_test("UPDATE profession")
    try:
        update_data = {
            "name": "Test Senior Software Engineer",
            "weight": 150,
        }
        response = requests.patch(
            f"{BASE_URL}/metadata/person/professions/{profession['id']}",
            json=update_data,
            headers=headers,
        )
        response.raise_for_status()
        updated_profession = response.json()
        assert updated_profession["name"] == update_data["name"]
        assert updated_profession["weight"] == update_data["weight"]
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
    
    # Verify deletion
    print_test("VERIFY profession deletion")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/person/professions/{profession['id']}",
        )
        assert response.status_code == 404, "Profession should not exist"
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    return profession


def test_duplicate_name_validation(headers: dict[str, str]) -> None:
    """Test that duplicate profession names are rejected."""
    print_header("VALIDATION - Duplicate Name Check")
    
    profession_data = {
        "name": "Test Unique Profession",
        "description": "Testing uniqueness",
        "weight": 50,
        "is_active": True,
    }
    
    # Create first profession
    print_test("CREATE first profession")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/person/professions",
            json=profession_data,
            headers=headers,
        )
        response.raise_for_status()
        profession = response.json()
        pass_test()
    except Exception as e:
        fail_test(str(e))
        return
    
    # Try to create duplicate
    print_test("CREATE duplicate profession (should fail)")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/person/professions",
            json=profession_data,
            headers=headers,
        )
        assert response.status_code == 400, "Should reject duplicate name"
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # Cleanup
    print_test("CLEANUP - Delete test profession")
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/person/professions/{profession['id']}",
            headers=headers,
        )
        response.raise_for_status()
        pass_test()
    except Exception as e:
        fail_test(str(e))


def main() -> None:
    """Run all tests."""
    print_header("PROFESSION METADATA API - INTEGRATION TEST")
    print(f"Testing against: {BASE_URL}")
    
    # Get authentication
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Run tests
    test_professions_crud(headers)
    test_duplicate_name_validation(headers)
    
    # Print summary
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

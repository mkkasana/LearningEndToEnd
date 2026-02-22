#!/usr/bin/env python3
"""
Comprehensive Integration Test for Religion Metadata API

Tests all CRUD operations for all 3 religion components:
- Religions
- Religion Categories
- Religion Sub-Categories

Usage:
    python3 backend/tests/integration_scripts/test_religion_full_integration.py [port]
    
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


def test_religions_crud(headers: dict[str, str]) -> dict[str, Any]:
    """Test all CRUD operations for religions."""
    print_header("RELIGIONS - CRUD Operations")
    
    religion_data = {
        "name": "Test Integration Religion",
        "code": "TIR",
        "description": "A test religion for integration testing",
        "is_active": True,
    }
    
    # CREATE
    print_test("CREATE religion")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/religion/religions",
            json=religion_data,
            headers=headers,
        )
        response.raise_for_status()
        religion = response.json()
        assert "id" in religion
        assert religion["name"] == religion_data["name"]
        assert religion["code"] == religion_data["code"].upper()
        assert religion["description"] == religion_data["description"]
        pass_test(f"ID: {religion['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}
    
    # READ - Get by ID
    print_test("READ religion by ID")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/religion/religions/{religion['id']}"
        )
        response.raise_for_status()
        fetched = response.json()
        assert fetched["id"] == religion["id"]
        assert fetched["name"] == religion["name"]
        assert fetched["description"] == religion["description"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # READ - Get all religions
    print_test("READ all religions")
    try:
        response = requests.get(f"{BASE_URL}/metadata/religion/religions")
        response.raise_for_status()
        religions = response.json()
        assert isinstance(religions, list)
        # List endpoints return camelCase format (religionId, religionName)
        assert any(r["religionId"] == religion["id"] for r in religions)
        pass_test(f"{len(religions)} religions found")
    except Exception as e:
        fail_test(str(e))
    
    # UPDATE
    print_test("UPDATE religion")
    try:
        update_data = {
            "name": "Updated Integration Religion",
            "description": "Updated description"
        }
        response = requests.patch(
            f"{BASE_URL}/metadata/religion/religions/{religion['id']}",
            json=update_data,
            headers=headers,
        )
        response.raise_for_status()
        updated = response.json()
        assert updated["name"] == update_data["name"]
        assert updated["description"] == update_data["description"]
        assert updated["code"] == religion["code"]
        religion = updated
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # Test duplicate code validation
    print_test("Validate duplicate code prevention")
    try:
        duplicate_data = {
            "name": "Duplicate Religion",
            "code": religion["code"],
            "is_active": True
        }
        response = requests.post(
            f"{BASE_URL}/metadata/religion/religions",
            json=duplicate_data,
            headers=headers,
        )
        assert response.status_code == 400
        pass_test("Duplicate rejected")
    except Exception as e:
        fail_test(str(e))
    
    # Test 404 handling
    print_test("Validate 404 for non-existent religion")
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.get(f"{BASE_URL}/metadata/religion/religions/{fake_id}")
        assert response.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    return religion


def test_categories_crud(headers: dict[str, str], religion: dict[str, Any]) -> dict[str, Any]:
    """Test all CRUD operations for religion categories."""
    print_header("RELIGION CATEGORIES - CRUD Operations")
    
    category_data = {
        "name": "Test Integration Category",
        "code": "TIC",
        "religion_id": religion["id"],
        "description": "A test category (e.g., Caste, Sect, Denomination)",
        "is_active": True,
    }
    
    # CREATE
    print_test("CREATE category")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/religion/categories",
            json=category_data,
            headers=headers,
        )
        response.raise_for_status()
        category = response.json()
        assert "id" in category
        assert category["name"] == category_data["name"]
        assert category["religion_id"] == religion["id"]
        assert category["description"] == category_data["description"]
        pass_test(f"ID: {category['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}
    
    # READ - Get by ID
    print_test("READ category by ID")
    try:
        response = requests.get(f"{BASE_URL}/metadata/religion/categories/{category['id']}")
        response.raise_for_status()
        fetched = response.json()
        assert fetched["id"] == category["id"]
        assert fetched["description"] == category["description"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # READ - Get categories by religion
    print_test("READ categories by religion")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/religion/religion/{religion['id']}/categories"
        )
        response.raise_for_status()
        categories = response.json()
        assert isinstance(categories, list)
        # List endpoints return camelCase format (categoryId, categoryName)
        assert any(c["categoryId"] == category["id"] for c in categories)
        pass_test(f"{len(categories)} categories found")
    except Exception as e:
        fail_test(str(e))
    
    # UPDATE
    print_test("UPDATE category")
    try:
        update_data = {
            "name": "Updated Integration Category",
            "description": "Updated category description"
        }
        response = requests.patch(
            f"{BASE_URL}/metadata/religion/categories/{category['id']}",
            json=update_data,
            headers=headers,
        )
        response.raise_for_status()
        updated = response.json()
        assert updated["name"] == update_data["name"]
        assert updated["description"] == update_data["description"]
        category = updated
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # Test invalid religion_id
    print_test("Validate invalid religion_id rejection")
    try:
        invalid_data = {
            "name": "Invalid Category",
            "code": "INV",
            "religion_id": "00000000-0000-0000-0000-000000000000",
            "is_active": True,
        }
        response = requests.post(
            f"{BASE_URL}/metadata/religion/categories",
            json=invalid_data,
            headers=headers,
        )
        assert response.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    return category


def test_sub_categories_crud(
    headers: dict[str, str], category: dict[str, Any]
) -> dict[str, Any]:
    """Test all CRUD operations for religion sub-categories."""
    print_header("RELIGION SUB-CATEGORIES - CRUD Operations")
    
    sub_category_data = {
        "name": "Test Integration Sub-Category",
        "code": "TISC",
        "category_id": category["id"],
        "description": "A test sub-category (e.g., Sub-caste, Sub-sect)",
        "is_active": True,
    }
    
    # CREATE
    print_test("CREATE sub-category")
    try:
        response = requests.post(
            f"{BASE_URL}/metadata/religion/sub-categories",
            json=sub_category_data,
            headers=headers,
        )
        response.raise_for_status()
        sub_category = response.json()
        assert "id" in sub_category
        assert sub_category["name"] == sub_category_data["name"]
        assert sub_category["category_id"] == category["id"]
        assert sub_category["description"] == sub_category_data["description"]
        pass_test(f"ID: {sub_category['id']}")
    except Exception as e:
        fail_test(str(e))
        return {}
    
    # READ - Get by ID
    print_test("READ sub-category by ID")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/religion/sub-categories/{sub_category['id']}"
        )
        response.raise_for_status()
        fetched = response.json()
        assert fetched["id"] == sub_category["id"]
        assert fetched["description"] == sub_category["description"]
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # READ - Get sub-categories by category
    print_test("READ sub-categories by category")
    try:
        response = requests.get(
            f"{BASE_URL}/metadata/religion/category/{category['id']}/sub-categories"
        )
        response.raise_for_status()
        sub_categories = response.json()
        assert isinstance(sub_categories, list)
        # List endpoints return camelCase format (subCategoryId, subCategoryName)
        assert any(sc["subCategoryId"] == sub_category["id"] for sc in sub_categories)
        pass_test(f"{len(sub_categories)} sub-categories found")
    except Exception as e:
        fail_test(str(e))
    
    # UPDATE
    print_test("UPDATE sub-category")
    try:
        update_data = {
            "name": "Updated Integration Sub-Category",
            "description": "Updated sub-category description"
        }
        response = requests.patch(
            f"{BASE_URL}/metadata/religion/sub-categories/{sub_category['id']}",
            json=update_data,
            headers=headers,
        )
        response.raise_for_status()
        updated = response.json()
        assert updated["name"] == update_data["name"]
        assert updated["description"] == update_data["description"]
        sub_category = updated
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # Test invalid category_id
    print_test("Validate invalid category_id rejection")
    try:
        invalid_data = {
            "name": "Invalid Sub-Category",
            "code": "INV",
            "category_id": "00000000-0000-0000-0000-000000000000",
            "is_active": True,
        }
        response = requests.post(
            f"{BASE_URL}/metadata/religion/sub-categories",
            json=invalid_data,
            headers=headers,
        )
        assert response.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    return sub_category


def test_delete_operations(
    headers: dict[str, str],
    religion: dict[str, Any],
    category: dict[str, Any],
    sub_category: dict[str, Any],
) -> None:
    """Test DELETE operations for all components."""
    print_header("DELETE Operations")
    
    # Delete in reverse hierarchical order
    print_test("DELETE sub-category")
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/religion/sub-categories/{sub_category['id']}",
            headers=headers,
        )
        response.raise_for_status()
        assert response.json()["message"] == "Sub-category deleted successfully"
        
        # Verify deletion
        verify = requests.get(
            f"{BASE_URL}/metadata/religion/sub-categories/{sub_category['id']}"
        )
        assert verify.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("DELETE category")
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/religion/categories/{category['id']}",
            headers=headers,
        )
        response.raise_for_status()
        assert response.json()["message"] == "Category deleted successfully"
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("DELETE religion")
    try:
        response = requests.delete(
            f"{BASE_URL}/metadata/religion/religions/{religion['id']}",
            headers=headers,
        )
        response.raise_for_status()
        assert response.json()["message"] == "Religion deleted successfully"
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    # Test error handling
    print_test("DELETE non-existent resource (404)")
    try:
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = requests.delete(
            f"{BASE_URL}/metadata/religion/religions/{fake_id}",
            headers=headers,
        )
        assert response.status_code == 404
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("DELETE without authentication (401)")
    try:
        # Create a temporary religion to test auth
        temp_religion = requests.post(
            f"{BASE_URL}/metadata/religion/religions",
            json={"name": "Temp Religion", "code": "TMP", "is_active": True},
            headers=headers,
        ).json()
        
        # Try to delete without auth
        response = requests.delete(
            f"{BASE_URL}/metadata/religion/religions/{temp_religion['id']}"
        )
        assert response.status_code == 401
        
        # Clean up
        requests.delete(
            f"{BASE_URL}/metadata/religion/religions/{temp_religion['id']}",
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
            f"{BASE_URL}/metadata/religion/religions",
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
            f"{BASE_URL}/metadata/religion/religions/{fake_id}",
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
            f"{BASE_URL}/metadata/religion/religions/{fake_id}"
        )
        assert response.status_code == 401
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("GET endpoints are public (no auth required)")
    try:
        response = requests.get(f"{BASE_URL}/metadata/religion/religions")
        assert response.status_code == 200
        pass_test()
    except Exception as e:
        fail_test(str(e))


def test_description_field() -> None:
    """Test that description field works correctly."""
    print_header("DESCRIPTION Field Tests")
    
    # Get auth token
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    print_test("CREATE religion with description")
    try:
        religion_data = {
            "name": "Test Religion with Description",
            "code": "TRWD",
            "description": "This is a detailed description of the religion",
            "is_active": True,
        }
        response = requests.post(
            f"{BASE_URL}/metadata/religion/religions",
            json=religion_data,
            headers=headers,
        )
        response.raise_for_status()
        religion = response.json()
        assert religion["description"] == religion_data["description"]
        
        # Clean up
        requests.delete(
            f"{BASE_URL}/metadata/religion/religions/{religion['id']}",
            headers=headers,
        )
        pass_test()
    except Exception as e:
        fail_test(str(e))
    
    print_test("CREATE religion without description (optional)")
    try:
        religion_data = {
            "name": "Test Religion No Description",
            "code": "TRND",
            "is_active": True,
        }
        response = requests.post(
            f"{BASE_URL}/metadata/religion/religions",
            json=religion_data,
            headers=headers,
        )
        response.raise_for_status()
        religion = response.json()
        assert religion["description"] is None
        
        # Clean up
        requests.delete(
            f"{BASE_URL}/metadata/religion/religions/{religion['id']}",
            headers=headers,
        )
        pass_test()
    except Exception as e:
        fail_test(str(e))


def main() -> None:
    """Run all integration tests."""
    print_header(f"Religion Metadata API - Full Integration Test Suite")
    print(f"Base URL: {BASE_URL}")
    print(f"Admin: {ADMIN_EMAIL}")
    
    # Get authentication
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test authentication requirements
    test_authentication()
    
    # Test description field
    test_description_field()
    
    # Test CRUD for each component
    religion = test_religions_crud(headers)
    if not religion:
        print("\n❌ Religion tests failed. Cannot continue with dependent tests.")
        sys.exit(1)
    
    category = test_categories_crud(headers, religion)
    if not category:
        print("\n❌ Category tests failed. Cannot continue with dependent tests.")
        sys.exit(1)
    
    sub_category = test_sub_categories_crud(headers, category)
    if not sub_category:
        print("\n❌ Sub-category tests failed. Cannot continue with dependent tests.")
        sys.exit(1)
    
    # Test delete operations
    test_delete_operations(headers, religion, category, sub_category)
    
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

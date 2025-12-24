#!/usr/bin/env python3
"""Integration test script for PersonReligion CRUD operations."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import requests
from requests.auth import HTTPBasicAuth

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
import time
TEST_USER_EMAIL = f"test_religion_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "TestPassword123!"


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def print_response(response: requests.Response, description: str):
    """Print response details."""
    print(f"{description}")
    print(f"Status: {response.status_code}")
    if response.text:
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response: {response.text}")
    print()


def get_access_token(email: str, password: str) -> str:
    """Get access token for user."""
    response = requests.post(
        f"{BASE_URL}/login/access-token",
        data={"username": email, "password": password},
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    raise Exception(f"Failed to login: {response.text}")


def create_test_user() -> dict:
    """Create a test user with person record."""
    print_section("Creating Test User")
    
    user_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "first_name": "Religion",
        "middle_name": "Test",
        "last_name": "User",
        "gender": "male",
        "date_of_birth": "1990-01-01",
    }
    
    response = requests.post(f"{BASE_URL}/users/signup", json=user_data)
    print_response(response, "User Creation")
    
    if response.status_code == 200:
        return response.json()
    return None


def get_religion_metadata(token: str) -> dict:
    """Get religion metadata to use in tests."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get religions
    response = requests.get(f"{BASE_URL}/metadata/religion/religions", headers=headers)
    religions = response.json() if response.status_code == 200 else []
    
    if not religions:
        print("⚠️  No religions found in metadata")
        return {}
    
    religion = religions[0]
    religion_id = religion["religionId"]
    
    # Get categories for this religion
    response = requests.get(
        f"{BASE_URL}/metadata/religion/religions/{religion_id}/categories",
        headers=headers
    )
    categories = response.json() if response.status_code == 200 else []
    
    category_id = categories[0]["categoryId"] if categories else None
    
    # Get sub-categories if category exists
    sub_category_id = None
    if category_id:
        response = requests.get(
            f"{BASE_URL}/metadata/religion/categories/{category_id}/sub-categories",
            headers=headers
        )
        sub_categories = response.json() if response.status_code == 200 else []
        sub_category_id = sub_categories[0]["subCategoryId"] if sub_categories else None
    
    return {
        "religion_id": religion_id,
        "religion_name": religion["religionName"],
        "category_id": category_id,
        "sub_category_id": sub_category_id,
    }


def test_create_religion(token: str, metadata: dict):
    """Test creating person religion."""
    print_section("Test 1: Create Person Religion")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    religion_data = {
        "religion_id": metadata["religion_id"],
        "religion_category_id": metadata.get("category_id"),
        "religion_sub_category_id": metadata.get("sub_category_id"),
    }
    
    response = requests.post(
        f"{BASE_URL}/person-religion/",
        json=religion_data,
        headers=headers
    )
    print_response(response, "✓ Create Religion")
    
    assert response.status_code == 201, "Failed to create religion"
    data = response.json()
    assert data["religion_id"] == metadata["religion_id"]
    print(f"✓ Religion created successfully with ID: {data['id']}")
    return data


def test_create_duplicate_religion(token: str, metadata: dict):
    """Test creating duplicate religion (should fail)."""
    print_section("Test 2: Create Duplicate Religion (Should Fail)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    religion_data = {
        "religion_id": metadata["religion_id"],
    }
    
    response = requests.post(
        f"{BASE_URL}/person-religion/",
        json=religion_data,
        headers=headers
    )
    print_response(response, "✗ Duplicate Creation Attempt")
    
    assert response.status_code == 400, "Should fail with 400"
    print("✓ Correctly rejected duplicate religion")


def test_get_my_religion(token: str):
    """Test getting current user's religion."""
    print_section("Test 3: Get My Religion")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/person-religion/me",
        headers=headers
    )
    print_response(response, "✓ Get My Religion")
    
    assert response.status_code == 200, "Failed to get religion"
    data = response.json()
    assert "religion_id" in data
    print(f"✓ Retrieved religion: {data['religion_id']}")
    return data


def test_update_religion(token: str, metadata: dict):
    """Test updating person religion."""
    print_section("Test 4: Update Person Religion")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Update to different category if available
    update_data = {}
    if metadata.get("category_id"):
        update_data["religion_category_id"] = metadata["category_id"]
    
    if not update_data:
        update_data["religion_id"] = metadata["religion_id"]
    
    response = requests.put(
        f"{BASE_URL}/person-religion/me",
        json=update_data,
        headers=headers
    )
    print_response(response, "✓ Update Religion")
    
    assert response.status_code == 200, "Failed to update religion"
    data = response.json()
    print("✓ Religion updated successfully")
    return data


def test_profile_completion(token: str):
    """Test profile completion status includes religion."""
    print_section("Test 5: Profile Completion Status")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/profile/completion-status",
        headers=headers
    )
    print_response(response, "✓ Profile Completion Status")
    
    assert response.status_code == 200, "Failed to get profile status"
    data = response.json()
    assert data["has_religion"] is True, "Religion should be marked as complete"
    print(f"✓ Profile completion: {data}")


def test_delete_religion(token: str):
    """Test deleting person religion."""
    print_section("Test 6: Delete Person Religion")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(
        f"{BASE_URL}/person-religion/me",
        headers=headers
    )
    print_response(response, "✓ Delete Religion")
    
    assert response.status_code == 204, "Failed to delete religion"
    print("✓ Religion deleted successfully")


def test_get_after_delete(token: str):
    """Test getting religion after deletion (should fail)."""
    print_section("Test 7: Get Religion After Deletion (Should Fail)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/person-religion/me",
        headers=headers
    )
    print_response(response, "✗ Get After Delete")
    
    assert response.status_code == 404, "Should return 404"
    print("✓ Correctly returned 404 for deleted religion")


def test_profile_completion_after_delete(token: str):
    """Test profile completion after religion deletion."""
    print_section("Test 8: Profile Completion After Religion Deletion")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/profile/completion-status",
        headers=headers
    )
    print_response(response, "✓ Profile Status After Delete")
    
    assert response.status_code == 200
    data = response.json()
    assert data["has_religion"] is False, "Religion should be marked as incomplete"
    assert "religion" in data["missing_fields"]
    print(f"✓ Profile correctly shows religion as incomplete")


def cleanup_test_user(token: str):
    """Delete test user."""
    print_section("Cleanup")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(
        f"{BASE_URL}/users/me",
        headers=headers
    )
    print_response(response, "✓ Delete Test User")
    print("✓ Cleanup completed")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  PersonReligion CRUD Integration Tests")
    print("=" * 60)
    
    try:
        # Create test user
        user = create_test_user()
        if not user:
            print("❌ Failed to create test user")
            return
        
        # Login
        token = get_access_token(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        print(f"✓ Logged in successfully")
        
        # Get religion metadata
        metadata = get_religion_metadata(token)
        if not metadata:
            print("❌ No religion metadata available")
            cleanup_test_user(token)
            return
        
        print(f"\n✓ Using religion: {metadata['religion_name']}")
        
        # Run tests
        test_create_religion(token, metadata)
        test_create_duplicate_religion(token, metadata)
        test_get_my_religion(token)
        test_update_religion(token, metadata)
        test_profile_completion(token)
        test_delete_religion(token)
        test_get_after_delete(token)
        test_profile_completion_after_delete(token)
        
        # Cleanup
        cleanup_test_user(token)
        
        print_section("✅ All Tests Passed!")
        
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

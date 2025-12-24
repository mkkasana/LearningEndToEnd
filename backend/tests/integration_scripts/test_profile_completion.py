"""Integration test for Profile Completion API."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import uuid

import requests

# API base URL
BASE_URL = "http://localhost:8000/api/v1"


def test_profile_completion():
    """Test profile completion status endpoint."""
    
    print("\n" + "=" * 60)
    print("PROFILE COMPLETION INTEGRATION TEST")
    print("=" * 60)
    
    # Step 1: Create a test user via signup
    print("\n1. Creating test user via signup...")
    signup_data = {
        "first_name": "Profile",
        "middle_name": "Test",
        "last_name": "User",
        "gender": "MALE",
        "date_of_birth": "1990-01-01",
        "email": f"profile_{uuid.uuid4().hex[:8]}@example.com",
        "password": "testpassword123",
    }
    
    response = requests.post(f"{BASE_URL}/users/signup", json=signup_data)
    assert response.status_code == 200, f"Signup failed: {response.text}"
    user_data = response.json()
    print(f"   ✓ Created user: {user_data['email']}")
    
    # Step 2: Login to get access token
    print("\n2. Logging in...")
    login_data = {
        "username": signup_data["email"],
        "password": signup_data["password"],
    }
    
    response = requests.post(f"{BASE_URL}/login/access-token", data=login_data)
    assert response.status_code == 200, f"Login failed: {response.text}"
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"   ✓ Obtained access token")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 3: Check profile completion status (should have person but no address)
    print("\n3. Checking profile completion status...")
    response = requests.get(f"{BASE_URL}/profile/completion-status", headers=headers)
    assert response.status_code == 200, f"Get status failed: {response.text}"
    status = response.json()
    
    print(f"   Profile Status:")
    print(f"   - Is Complete: {status['is_complete']}")
    print(f"   - Has Person: {status['has_person']}")
    print(f"   - Has Address: {status['has_address']}")
    print(f"   - Missing Fields: {status['missing_fields']}")
    
    # Verify person exists (created during signup)
    assert status["has_person"] == True, "Person should exist after signup!"
    print(f"   ✓ Person record exists (created during signup)")
    
    # Verify address doesn't exist yet
    assert status["has_address"] == False, "Address should not exist yet!"
    print(f"   ✓ Address not yet added")
    
    # Verify profile is incomplete
    assert status["is_complete"] == False, "Profile should be incomplete!"
    assert "address" in status["missing_fields"], "Address should be in missing fields!"
    print(f"   ✓ Profile correctly marked as incomplete")
    
    # Step 4: Add an address
    print("\n4. Adding address...")
    
    # First, get a country (assuming India exists from seed data)
    response = requests.get(f"{BASE_URL}/metadata/address/countries")
    countries = response.json()
    india = next((c for c in countries if c["countryName"] == "India"), None)
    
    if not india:
        print("   ⚠ India not found in countries, skipping address test")
        print("\n" + "=" * 60)
        print("PARTIAL TEST PASSED! ✓")
        print("=" * 60)
        return
    
    address_data = {
        "country_id": india["countryId"],
        "address_line": "123 Test Street",
        "start_date": "2024-01-01",
        "is_current": True,
    }
    
    response = requests.post(
        f"{BASE_URL}/person/me/addresses",
        json=address_data,
        headers=headers,
    )
    assert response.status_code == 200, f"Add address failed: {response.text}"
    print(f"   ✓ Address added successfully")
    
    # Step 5: Check profile completion status again (should be complete now)
    print("\n5. Checking profile completion status after adding address...")
    response = requests.get(f"{BASE_URL}/profile/completion-status", headers=headers)
    assert response.status_code == 200, f"Get status failed: {response.text}"
    status = response.json()
    
    print(f"   Profile Status:")
    print(f"   - Is Complete: {status['is_complete']}")
    print(f"   - Has Person: {status['has_person']}")
    print(f"   - Has Address: {status['has_address']}")
    print(f"   - Missing Fields: {status['missing_fields']}")
    
    # Verify profile is now complete
    assert status["has_person"] == True, "Person should still exist!"
    assert status["has_address"] == True, "Address should now exist!"
    assert status["is_complete"] == True, "Profile should be complete!"
    assert len(status["missing_fields"]) == 0, "No fields should be missing!"
    print(f"   ✓ Profile is now complete!")
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✓")
    print("=" * 60)
    print("\nSummary:")
    print("  - User signup creates Person record automatically")
    print("  - Profile incomplete without address")
    print("  - Profile completion status API works correctly")
    print("  - Profile becomes complete after adding address")
    print("\n")


if __name__ == "__main__":
    try:
        test_profile_completion()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

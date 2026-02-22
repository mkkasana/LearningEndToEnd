"""Integration test for Posts API endpoints."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import uuid

import requests

# API base URL
BASE_URL = "http://localhost:8000/api/v1"


def test_posts_api():
    """Test Posts API CRUD operations end-to-end."""
    
    print("\n" + "=" * 60)
    print("POSTS API INTEGRATION TEST")
    print("=" * 60)
    
    # Step 1: Create a test user via signup
    print("\n1. Creating test user via signup API...")
    signup_data = {
        "first_name": "Test",
        "middle_name": "API",
        "last_name": "User",
        "gender": "MALE",
        "date_of_birth": "1990-01-01",
        "email": f"testapi_{uuid.uuid4().hex[:8]}@example.com",
        "password": "testpassword123",
    }
    
    response = requests.post(f"{BASE_URL}/users/signup", json=signup_data)
    assert response.status_code == 200, f"Signup failed: {response.text}"
    user_data = response.json()
    print(f"   ✓ Created user: {user_data['email']}")
    
    # Step 2: Login to get access token
    print("\n2. Logging in to get access token...")
    login_data = {
        "username": signup_data["email"],
        "password": signup_data["password"],
    }
    
    response = requests.post(
        f"{BASE_URL}/login/access-token",
        data=login_data,
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    token_data = response.json()
    access_token = token_data["access_token"]
    print(f"   ✓ Obtained access token")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 3: Create a post
    print("\n3. Creating a post via API...")
    post_data = {
        "title": "My First API Post",
        "content": "This is the content of my first post created via API!",
        "is_published": True,
    }
    
    response = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=headers)
    assert response.status_code == 200, f"Create post failed: {response.text}"
    created_post = response.json()
    post_id = created_post["id"]
    print(f"   ✓ Created post: '{created_post['title']}'")
    print(f"   - Post ID: {post_id}")
    print(f"   - Published: {created_post['is_published']}")
    
    # Step 4: Get the post by ID
    print("\n4. Getting post by ID...")
    response = requests.get(f"{BASE_URL}/posts/{post_id}")
    assert response.status_code == 200, f"Get post failed: {response.text}"
    retrieved_post = response.json()
    assert retrieved_post["id"] == post_id
    assert retrieved_post["title"] == post_data["title"]
    print(f"   ✓ Retrieved post: '{retrieved_post['title']}'")
    
    # Step 5: Update the post
    print("\n5. Updating the post...")
    update_data = {
        "title": "Updated API Post Title",
        "content": "This content has been updated via API!",
    }
    
    response = requests.patch(
        f"{BASE_URL}/posts/{post_id}", json=update_data, headers=headers
    )
    assert response.status_code == 200, f"Update post failed: {response.text}"
    updated_post = response.json()
    assert updated_post["title"] == update_data["title"]
    print(f"   ✓ Updated post title: '{updated_post['title']}'")
    print(f"   - New content: {updated_post['content']}")
    
    # Step 6: Create multiple posts
    print("\n6. Creating multiple posts...")
    posts_to_create = [
        {"title": "Second Post", "content": "Content 2", "is_published": True},
        {"title": "Third Post", "content": "Content 3", "is_published": True},
        {"title": "Draft Post", "content": "Draft content", "is_published": False},
    ]
    
    created_post_ids = [post_id]
    for post_data in posts_to_create:
        response = requests.post(f"{BASE_URL}/posts/", json=post_data, headers=headers)
        assert response.status_code == 200
        created_post_ids.append(response.json()["id"])
    
    print(f"   ✓ Created {len(posts_to_create)} additional posts")
    
    # Step 7: Get my posts
    print("\n7. Getting my posts...")
    response = requests.get(f"{BASE_URL}/posts/me", headers=headers)
    assert response.status_code == 200, f"Get my posts failed: {response.text}"
    my_posts = response.json()
    print(f"   ✓ Found {my_posts['count']} posts")
    for idx, post in enumerate(my_posts["data"], 1):
        print(f"   {idx}. {post['title']} (Published: {post['is_published']})")
    
    # Step 8: Get all published posts (public endpoint)
    print("\n8. Getting all published posts (public)...")
    response = requests.get(f"{BASE_URL}/posts/")
    assert response.status_code == 200, f"Get published posts failed: {response.text}"
    published_posts = response.json()
    print(f"   ✓ Found {published_posts['count']} published posts")
    
    # Verify draft post is not in public list
    draft_in_public = any(
        p["title"] == "Draft Post" for p in published_posts["data"]
    )
    assert not draft_in_public, "Draft post should not be in public list!"
    print(f"   ✓ Verified draft post is not publicly visible")
    
    # Step 9: Try to access draft post without auth (should fail)
    print("\n9. Testing draft post access without auth...")
    draft_post_id = created_post_ids[-1]  # Last one is the draft
    response = requests.get(f"{BASE_URL}/posts/{draft_post_id}")
    assert response.status_code == 404, "Draft post should not be accessible publicly!"
    print(f"   ✓ Draft post correctly hidden from public")
    
    # Step 10: Delete a post
    print("\n10. Deleting a post...")
    post_to_delete = created_post_ids[1]  # Delete second post
    response = requests.delete(
        f"{BASE_URL}/posts/{post_to_delete}", headers=headers
    )
    assert response.status_code == 200, f"Delete post failed: {response.text}"
    print(f"   ✓ Deleted post successfully")
    
    # Verify deletion
    response = requests.get(f"{BASE_URL}/posts/{post_to_delete}")
    assert response.status_code == 404, "Deleted post should return 404"
    print(f"   ✓ Verified post is deleted")
    
    # Step 11: Try to update another user's post (should fail)
    print("\n11. Testing authorization (update another user's post)...")
    # Create another user
    other_user_data = {
        "first_name": "Other",
        "last_name": "User",
        "gender": "FEMALE",
        "date_of_birth": "1995-05-05",
        "email": f"other_{uuid.uuid4().hex[:8]}@example.com",
        "password": "otherpassword123",
    }
    requests.post(f"{BASE_URL}/users/signup", json=other_user_data)
    
    # Login as other user
    other_login = {
        "username": other_user_data["email"],
        "password": other_user_data["password"],
    }
    response = requests.post(f"{BASE_URL}/login/access-token", data=other_login)
    other_token = response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}
    
    # Try to update first user's post
    response = requests.patch(
        f"{BASE_URL}/posts/{post_id}",
        json={"title": "Hacked!"},
        headers=other_headers,
    )
    assert response.status_code == 403, "Should not be able to update other user's post!"
    print(f"   ✓ Authorization check passed (403 Forbidden)")
    
    # Cleanup: Delete remaining posts
    print("\n12. Cleaning up...")
    for pid in created_post_ids:
        requests.delete(f"{BASE_URL}/posts/{pid}", headers=headers)
    print(f"   ✓ Cleaned up test data")
    
    print("\n" + "=" * 60)
    print("ALL API TESTS PASSED! ✓")
    print("=" * 60)
    print("\nSummary:")
    print("  - User signup and login")
    print("  - Create post with authentication")
    print("  - Read post (public and authenticated)")
    print("  - Update post (owner only)")
    print("  - List posts (my posts and public posts)")
    print("  - Draft posts hidden from public")
    print("  - Delete post")
    print("  - Authorization checks (403 for non-owners)")
    print("\n")


if __name__ == "__main__":
    try:
        test_posts_api()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

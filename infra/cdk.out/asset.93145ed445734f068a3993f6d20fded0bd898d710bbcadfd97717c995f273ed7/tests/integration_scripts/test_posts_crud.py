"""Integration test for Posts CRUD operations."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import uuid

from sqlmodel import Session, select

from app.core.db import engine
from app.core.security import get_password_hash
from app.db_models.post import Post
from app.db_models.user import User


def test_posts_crud():
    """Test complete CRUD operations for posts."""
    
    print("\n" + "=" * 60)
    print("POSTS CRUD INTEGRATION TEST")
    print("=" * 60)
    
    with Session(engine) as session:
        # Step 1: Create a test user
        print("\n1. Creating test user...")
        test_user = User(
            id=uuid.uuid4(),
            email=f"testuser_{uuid.uuid4().hex[:8]}@example.com",
            hashed_password=get_password_hash("testpassword123"),
            full_name="Test User",
            is_active=True,
            is_superuser=False,
        )
        session.add(test_user)
        session.commit()
        session.refresh(test_user)
        print(f"   ✓ Created user: {test_user.email} (ID: {test_user.id})")
        
        # Step 2: Create a post
        print("\n2. Creating a post...")
        post = Post(
            id=uuid.uuid4(),
            user_id=test_user.id,
            title="My First Post",
            content="This is the content of my first post. It's a great post!",
            is_published=True,
        )
        session.add(post)
        session.commit()
        session.refresh(post)
        print(f"   ✓ Created post: '{post.title}' (ID: {post.id})")
        print(f"   - Content: {post.content[:50]}...")
        print(f"   - Published: {post.is_published}")
        print(f"   - Created at: {post.created_at}")
        
        # Step 3: Read the post
        print("\n3. Reading the post...")
        retrieved_post = session.get(Post, post.id)
        assert retrieved_post is not None, "Post not found!"
        assert retrieved_post.title == "My First Post"
        assert retrieved_post.user_id == test_user.id
        print(f"   ✓ Retrieved post: '{retrieved_post.title}'")
        print(f"   - User ID matches: {retrieved_post.user_id == test_user.id}")
        
        # Step 4: Update the post
        print("\n4. Updating the post...")
        retrieved_post.title = "My Updated Post Title"
        retrieved_post.content = "This content has been updated!"
        retrieved_post.is_published = False
        session.add(retrieved_post)
        session.commit()
        session.refresh(retrieved_post)
        print(f"   ✓ Updated post title: '{retrieved_post.title}'")
        print(f"   - New content: {retrieved_post.content}")
        print(f"   - Published status: {retrieved_post.is_published}")
        
        # Step 5: Create multiple posts for the user
        print("\n5. Creating multiple posts...")
        posts_data = [
            {"title": "Second Post", "content": "Content of second post"},
            {"title": "Third Post", "content": "Content of third post"},
            {"title": "Fourth Post", "content": "Content of fourth post"},
        ]
        
        created_posts = []
        for post_data in posts_data:
            new_post = Post(
                id=uuid.uuid4(),
                user_id=test_user.id,
                title=post_data["title"],
                content=post_data["content"],
                is_published=True,
            )
            session.add(new_post)
            created_posts.append(new_post)
        
        session.commit()
        print(f"   ✓ Created {len(created_posts)} additional posts")
        
        # Step 6: Query all posts by user
        print("\n6. Querying all posts by user...")
        statement = select(Post).where(Post.user_id == test_user.id)
        user_posts = list(session.exec(statement).all())
        print(f"   ✓ Found {len(user_posts)} posts for user")
        for idx, p in enumerate(user_posts, 1):
            print(f"   {idx}. {p.title} (Published: {p.is_published})")
        
        # Step 7: Query only published posts
        print("\n7. Querying published posts...")
        statement = select(Post).where(
            Post.user_id == test_user.id, Post.is_published == True
        )
        published_posts = list(session.exec(statement).all())
        print(f"   ✓ Found {len(published_posts)} published posts")
        
        # Step 8: Delete a post
        print("\n8. Deleting a post...")
        post_to_delete = created_posts[0]
        post_id_to_delete = post_to_delete.id
        post_title_to_delete = post_to_delete.title
        session.delete(post_to_delete)
        session.commit()
        print(f"   ✓ Deleted post: '{post_title_to_delete}'")
        
        # Verify deletion
        deleted_post = session.get(Post, post_id_to_delete)
        assert deleted_post is None, "Post should be deleted!"
        print(f"   ✓ Verified post is deleted")
        
        # Step 9: Verify remaining posts
        print("\n9. Verifying remaining posts...")
        statement = select(Post).where(Post.user_id == test_user.id)
        remaining_posts = list(session.exec(statement).all())
        print(f"   ✓ {len(remaining_posts)} posts remain")
        
        # Step 10: Test cascade delete (delete user should delete all posts)
        print("\n10. Testing cascade delete...")
        print(f"   - Deleting user: {test_user.email}")
        session.delete(test_user)
        session.commit()
        
        # Verify all posts are deleted
        statement = select(Post).where(Post.user_id == test_user.id)
        orphaned_posts = list(session.exec(statement).all())
        assert len(orphaned_posts) == 0, "All posts should be deleted with user!"
        print(f"   ✓ All user posts deleted via cascade")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60)
        print("\nSummary:")
        print("  - Created user and posts")
        print("  - Read post successfully")
        print("  - Updated post fields")
        print("  - Queried posts by user and status")
        print("  - Deleted individual post")
        print("  - Verified cascade delete")
        print("\n")


if __name__ == "__main__":
    try:
        test_posts_crud()
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

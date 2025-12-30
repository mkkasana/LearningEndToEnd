"""Tests for cache management API endpoints."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.utils.cache import get_cache_manager


def test_delete_cache_key_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test deleting a specific cache key as superuser."""
    # Set up a cache entry
    cache_manager = get_cache_manager()
    cache_manager.set("test:key:123", "test_value", ttl_seconds=60)
    
    # Verify it exists
    assert cache_manager.get("test:key:123") == "test_value"
    
    # Delete via API
    response = client.delete(
        f"{settings.API_V1_STR}/utils/cache/test:key:123",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "deleted successfully" in data["message"]
    
    # Verify it's gone
    assert cache_manager.get("test:key:123") is None


def test_delete_cache_key_as_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test that normal users cannot delete cache keys."""
    response = client.delete(
        f"{settings.API_V1_STR}/utils/cache/test:key:123",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403


def test_delete_cache_pattern_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test deleting cache keys by pattern as superuser."""
    # Set up multiple cache entries
    cache_manager = get_cache_manager()
    cache_manager.set("discovery:user1", "value1", ttl_seconds=60)
    cache_manager.set("discovery:user2", "value2", ttl_seconds=60)
    cache_manager.set("other:key", "value3", ttl_seconds=60)
    
    # Verify they exist
    assert cache_manager.get("discovery:user1") == "value1"
    assert cache_manager.get("discovery:user2") == "value2"
    assert cache_manager.get("other:key") == "value3"
    
    # Delete discovery pattern via API
    response = client.delete(
        f"{settings.API_V1_STR}/utils/cache-pattern/discovery:",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "deleted successfully" in data["message"]
    
    # Verify discovery keys are gone but other key remains
    assert cache_manager.get("discovery:user1") is None
    assert cache_manager.get("discovery:user2") is None
    assert cache_manager.get("other:key") == "value3"


def test_clear_all_cache_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test clearing all cache as superuser."""
    # Set up multiple cache entries
    cache_manager = get_cache_manager()
    cache_manager.set("key1", "value1", ttl_seconds=60)
    cache_manager.set("key2", "value2", ttl_seconds=60)
    cache_manager.set("key3", "value3", ttl_seconds=60)
    
    # Verify they exist
    assert cache_manager.get("key1") == "value1"
    assert cache_manager.get("key2") == "value2"
    assert cache_manager.get("key3") == "value3"
    
    # Clear all via API
    response = client.post(
        f"{settings.API_V1_STR}/utils/cache/clear",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "All cache cleared successfully" in data["message"]
    
    # Verify all are gone
    assert cache_manager.get("key1") is None
    assert cache_manager.get("key2") is None
    assert cache_manager.get("key3") is None


def test_clear_all_cache_as_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test that normal users cannot clear all cache."""
    response = client.post(
        f"{settings.API_V1_STR}/utils/cache/clear",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403

"""Tests for caching utilities."""

import time
import uuid

import pytest

from app.utils.cache import CacheManager, cached, get_cache_manager, invalidate_discovery_cache


class TestCacheManager:
    """Test CacheManager functionality."""

    def test_set_and_get(self) -> None:
        """Test basic set and get operations."""
        cache = CacheManager()
        cache.set("test_key", "test_value", ttl_seconds=60)
        
        result = cache.get("test_key")
        assert result == "test_value"

    def test_get_nonexistent_key(self) -> None:
        """Test getting a key that doesn't exist."""
        cache = CacheManager()
        result = cache.get("nonexistent")
        assert result is None

    def test_ttl_expiration(self) -> None:
        """Test that cached values expire after TTL."""
        cache = CacheManager()
        cache.set("test_key", "test_value", ttl_seconds=1)
        
        # Should exist immediately
        result = cache.get("test_key")
        assert result == "test_value"
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        result = cache.get("test_key")
        assert result is None

    def test_delete(self) -> None:
        """Test deleting a cached value."""
        cache = CacheManager()
        cache.set("test_key", "test_value", ttl_seconds=60)
        
        # Verify it exists
        assert cache.get("test_key") == "test_value"
        
        # Delete it
        cache.delete("test_key")
        
        # Should be gone
        assert cache.get("test_key") is None

    def test_clear(self) -> None:
        """Test clearing all cached values."""
        cache = CacheManager()
        cache.set("key1", "value1", ttl_seconds=60)
        cache.set("key2", "value2", ttl_seconds=60)
        
        # Verify they exist
        assert cache.get("key1") == "value1"
        assert cache.get("key2") == "value2"
        
        # Clear all
        cache.clear()
        
        # Should all be gone
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_invalidate_pattern(self) -> None:
        """Test invalidating keys by pattern."""
        cache = CacheManager()
        cache.set("discovery:user1", "value1", ttl_seconds=60)
        cache.set("discovery:user2", "value2", ttl_seconds=60)
        cache.set("other:key", "value3", ttl_seconds=60)
        
        # Invalidate discovery keys
        cache.invalidate_pattern("discovery:")
        
        # Discovery keys should be gone
        assert cache.get("discovery:user1") is None
        assert cache.get("discovery:user2") is None
        
        # Other key should still exist
        assert cache.get("other:key") == "value3"


class TestCachedDecorator:
    """Test the @cached decorator."""

    def test_caches_function_result(self) -> None:
        """Test that function results are cached."""
        call_count = 0
        
        @cached(ttl_seconds=60, key_prefix="test")
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not increment
        
        # Different argument should execute function again
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2

    def test_cache_with_uuid_argument(self) -> None:
        """Test caching with UUID arguments."""
        call_count = 0
        test_uuid = uuid.uuid4()
        
        @cached(ttl_seconds=60, key_prefix="test")
        def function_with_uuid(user_id: uuid.UUID) -> str:
            nonlocal call_count
            call_count += 1
            return f"user_{user_id}"
        
        # First call
        result1 = function_with_uuid(test_uuid)
        assert result1 == f"user_{test_uuid}"
        assert call_count == 1
        
        # Second call with same UUID should use cache
        result2 = function_with_uuid(test_uuid)
        assert result2 == f"user_{test_uuid}"
        assert call_count == 1

    def test_cache_expiration(self) -> None:
        """Test that cached results expire after TTL."""
        call_count = 0
        
        @cached(ttl_seconds=1, key_prefix="test")
        def function_with_short_ttl(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = function_with_short_ttl(5)
        assert result1 == 10
        assert call_count == 1
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should execute function again
        result2 = function_with_short_ttl(5)
        assert result2 == 10
        assert call_count == 2


class TestInvalidateDiscoveryCache:
    """Test discovery cache invalidation."""

    def test_invalidates_user_cache(self) -> None:
        """Test that invalidate_discovery_cache removes the correct cache entry."""
        cache = get_cache_manager()
        user_id = uuid.uuid4()
        
        # Set a cache entry
        cache_key = f"discovery:discover_family_members:{str(user_id)}"
        cache.set(cache_key, ["result1", "result2"], ttl_seconds=60)
        
        # Verify it exists
        assert cache.get(cache_key) is not None
        
        # Invalidate
        invalidate_discovery_cache(user_id)
        
        # Should be gone
        assert cache.get(cache_key) is None

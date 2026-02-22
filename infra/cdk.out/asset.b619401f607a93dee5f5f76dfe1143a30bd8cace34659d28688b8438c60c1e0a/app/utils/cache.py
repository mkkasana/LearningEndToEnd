"""Caching utilities for the application."""

import functools
import logging
import time
import uuid
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Simple in-memory cache manager with TTL support.

    This is a lightweight caching solution that stores data in memory
    with time-to-live (TTL) expiration. Suitable for single-instance
    deployments or development environments.

    For production multi-instance deployments, consider using Redis
    or another distributed caching solution.
    """

    def __init__(self) -> None:
        """Initialize the cache manager."""
        self._cache: dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Any | None:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        if key not in self._cache:
            return None

        value, expiry = self._cache[key]

        # Check if expired
        if time.time() > expiry:
            # Remove expired entry
            del self._cache[key]
            logger.debug(f"Cache expired for key: {key}")
            return None

        logger.debug(f"Cache hit for key: {key}")
        return value

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """
        Set a value in the cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (default: 300 = 5 minutes)
        """
        expiry = time.time() + ttl_seconds
        self._cache[key] = (value, expiry)
        logger.debug(f"Cache set for key: {key}, TTL: {ttl_seconds}s")

    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.

        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted for key: {key}")

    def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()
        logger.debug("Cache cleared")

    def invalidate_pattern(self, pattern: str) -> None:
        """
        Invalidate all cache keys matching a pattern.

        Args:
            pattern: Pattern to match (simple string prefix matching)
        """
        keys_to_delete = [key for key in self._cache.keys() if key.startswith(pattern)]
        for key in keys_to_delete:
            del self._cache[key]

        if keys_to_delete:
            logger.debug(
                f"Invalidated {len(keys_to_delete)} cache entries matching pattern: {pattern}"
            )


# Global cache manager instance
_cache_manager = CacheManager()


def get_cache_manager() -> CacheManager:
    """
    Get the global cache manager instance.

    Returns:
        Global CacheManager instance
    """
    return _cache_manager


def cached(ttl_seconds: int = 300, key_prefix: str = "") -> Callable[..., Any]:
    """
    Decorator to cache function results with TTL.

    Args:
        ttl_seconds: Time to live in seconds (default: 300 = 5 minutes)
        key_prefix: Prefix for cache keys (default: empty string)

    Returns:
        Decorator function

    Example:
        @cached(ttl_seconds=300, key_prefix="discovery")
        def discover_family_members(user_id: uuid.UUID) -> list:
            # Expensive operation
            return results
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Build cache key from function name and arguments
            # Convert UUID arguments to strings for cache key
            cache_key_parts = [key_prefix, func.__name__]

            for arg in args:
                if isinstance(arg, uuid.UUID):
                    cache_key_parts.append(str(arg))
                elif isinstance(arg, (str, int, float, bool)):
                    cache_key_parts.append(str(arg))
                # Skip non-hashable types like Session

            for key, value in sorted(kwargs.items()):
                if isinstance(value, uuid.UUID):
                    cache_key_parts.append(f"{key}={str(value)}")
                elif isinstance(value, (str, int, float, bool)):
                    cache_key_parts.append(f"{key}={str(value)}")

            cache_key = ":".join(cache_key_parts)

            # Try to get from cache
            cache_manager = get_cache_manager()
            cached_value = cache_manager.get(cache_key)

            if cached_value is not None:
                logger.debug(f"Returning cached result for {func.__name__}")
                return cached_value

            # Call the function
            logger.debug(f"Cache miss for {func.__name__}, executing function")
            result = func(*args, **kwargs)

            # Store in cache
            cache_manager.set(cache_key, result, ttl_seconds)

            return result

        return wrapper

    return decorator


def invalidate_discovery_cache(user_id: uuid.UUID) -> None:
    """
    Invalidate discovery cache for a specific user.

    This should be called when relationships are created, updated, or deleted
    to ensure the discovery results are refreshed.

    Args:
        user_id: User ID whose discovery cache should be invalidated
    """
    cache_manager = get_cache_manager()
    cache_key_pattern = f"discovery:discover_family_members:{str(user_id)}"
    cache_manager.delete(cache_key_pattern)
    logger.info(f"Invalidated discovery cache for user: {user_id}")

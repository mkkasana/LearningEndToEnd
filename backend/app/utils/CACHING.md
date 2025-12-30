# Caching Implementation

## Overview

This application uses an in-memory caching system to improve performance for expensive operations like family member discovery. The caching system is implemented in `app/utils/cache.py`.

## Architecture

### CacheManager

The `CacheManager` class provides a simple in-memory cache with TTL (Time To Live) support:

- **Storage**: Python dictionary with (value, expiry_timestamp) tuples
- **TTL**: Configurable expiration time for each cached entry
- **Pattern Invalidation**: Support for invalidating multiple keys by prefix

### @cached Decorator

The `@cached` decorator makes it easy to cache function results:

```python
@cached(ttl_seconds=300, key_prefix="discovery")
def discover_family_members(user_id: uuid.UUID) -> list[PersonDiscoveryResult]:
    # Expensive operation
    return results
```

**Features:**
- Automatic cache key generation from function name and arguments
- Support for UUID, string, int, float, and bool arguments
- Configurable TTL per function
- Key prefix for organizing cache entries

## Usage

### Discovery Service Caching

The `PersonDiscoveryService.discover_family_members()` method is cached with:
- **TTL**: 1 minute (60 seconds)
- **Key Format**: `discovery:discover_family_members:{user_id}`
- **Cache Key Prefix**: `discovery`

### Cache Invalidation

Cache is automatically invalidated when relationships change:

1. **On Relationship Create**: `PersonRelationshipService.create_relationship()`
2. **On Relationship Update**: `PersonRelationshipService.update_relationship()`
3. **On Relationship Delete**: `PersonRelationshipService.delete_relationship()`

The `invalidate_discovery_cache(user_id)` function is called for both persons involved in the relationship to ensure their discovery results are refreshed.

## Implementation Details

### Cache Key Generation

Cache keys are built from:
1. Key prefix (e.g., "discovery")
2. Function name (e.g., "discover_family_members")
3. Function arguments (converted to strings)

Example: `discovery:discover_family_members:123e4567-e89b-12d3-a456-426614174000`

### Expiration

- Cached entries are checked for expiration on every `get()` call
- Expired entries are automatically removed from the cache
- Default TTL is 60 seconds (1 minute)

## Cache Management API

Superusers can manually manage the cache through API endpoints:

### Delete Specific Cache Key

```bash
DELETE /api/v1/utils/cache/{cache_key}
```

Example:
```bash
curl -X DELETE "http://localhost/api/v1/utils/cache/discovery:discover_family_members:123e4567-e89b-12d3-a456-426614174000" \
  -H "Authorization: Bearer {superuser_token}"
```

### Delete Cache Keys by Pattern

```bash
DELETE /api/v1/utils/cache-pattern/{pattern}
```

Example (clear all discovery caches):
```bash
curl -X DELETE "http://localhost/api/v1/utils/cache-pattern/discovery:" \
  -H "Authorization: Bearer {superuser_token}"
```

### Clear All Cache

```bash
POST /api/v1/utils/cache/clear
```

Example:
```bash
curl -X POST "http://localhost/api/v1/utils/cache/clear" \
  -H "Authorization: Bearer {superuser_token}"
```

**Note**: All cache management endpoints require superuser authentication.

### Thread Safety

**Note**: The current implementation is NOT thread-safe. For production use with multiple workers, consider:
- Using Redis or Memcached for distributed caching
- Adding thread locks to the CacheManager
- Using a process-safe caching solution

## Production Considerations

### Current Limitations

1. **Single Instance Only**: In-memory cache is not shared across multiple application instances
2. **No Persistence**: Cache is lost on application restart
3. **Memory Usage**: Large caches can consume significant memory

### Recommended Upgrades for Production

For production deployments with multiple instances, consider upgrading to:

1. **Redis**: Distributed caching with persistence
   ```python
   import redis
   from redis import Redis
   
   redis_client = Redis(host='localhost', port=6379, db=0)
   ```

2. **Memcached**: High-performance distributed memory caching
   ```python
   from pymemcache.client import base
   
   memcache_client = base.Client(('localhost', 11211))
   ```

3. **FastAPI-Cache**: FastAPI-specific caching library with Redis/Memcached support
   ```python
   from fastapi_cache import FastAPICache
   from fastapi_cache.backends.redis import RedisBackend
   ```

## Testing

Cache functionality is tested in `tests/utils/test_cache.py`:

- Basic set/get operations
- TTL expiration
- Cache invalidation
- Pattern-based invalidation
- Decorator functionality

Run tests:
```bash
pytest tests/utils/test_cache.py -v
```

## Monitoring

To monitor cache performance, check logs for:
- `Cache hit for key: {key}` - Successful cache retrieval
- `Cache miss for {function_name}, executing function` - Cache miss, function executed
- `Cache expired for key: {key}` - Entry expired and removed
- `Invalidated discovery cache for user: {user_id}` - Cache invalidated

## Configuration

To adjust cache TTL, modify the decorator:

```python
@cached(ttl_seconds=120, key_prefix="discovery")  # 2 minutes
def discover_family_members(user_id: uuid.UUID) -> list[PersonDiscoveryResult]:
    ...
```

To disable caching temporarily, remove the `@cached` decorator.

Current TTL: **60 seconds (1 minute)** for discovery cache.

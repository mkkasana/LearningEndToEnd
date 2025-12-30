from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

from app.api.deps import get_current_active_superuser
from app.schemas.common import Message
from app.utils import generate_test_email, send_email
from app.utils.cache import get_cache_manager

router = APIRouter(prefix="/utils", tags=["utils"])


@router.post(
    "/test-email/",
    dependencies=[Depends(get_current_active_superuser)],
    status_code=201,
)
def test_email(email_to: EmailStr) -> Message:
    """
    Test emails.
    """
    email_data = generate_test_email(email_to=email_to)
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Test email sent")


@router.get("/health-check/")
async def health_check() -> bool:
    return True


@router.delete(
    "/cache/{cache_key:path}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_cache_key(cache_key: str) -> Message:
    """
    Delete a specific cache key (superuser only).

    This endpoint allows superusers to manually invalidate cache entries.
    Useful for debugging or forcing cache refresh.

    Args:
        cache_key: The cache key to delete (e.g., "discovery:discover_family_members:user-id")

    Returns:
        Success message

    Example:
        DELETE /api/v1/utils/cache/discovery:discover_family_members:123e4567-e89b-12d3-a456-426614174000
    """
    cache_manager = get_cache_manager()
    cache_manager.delete(cache_key)
    return Message(message=f"Cache key '{cache_key}' deleted successfully")


@router.delete(
    "/cache-pattern/{pattern:path}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def delete_cache_pattern(pattern: str) -> Message:
    """
    Delete all cache keys matching a pattern (superuser only).

    This endpoint allows superusers to invalidate multiple cache entries at once
    by matching a prefix pattern.

    Args:
        pattern: The pattern to match (e.g., "discovery:" to clear all discovery caches)

    Returns:
        Success message

    Example:
        DELETE /api/v1/utils/cache-pattern/discovery:
    """
    cache_manager = get_cache_manager()
    cache_manager.invalidate_pattern(pattern)
    return Message(
        message=f"All cache keys matching pattern '{pattern}' deleted successfully"
    )


@router.post(
    "/cache/clear",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=Message,
)
def clear_all_cache() -> Message:
    """
    Clear all cache entries (superuser only).

    This endpoint clears the entire cache. Use with caution as it will
    invalidate all cached data across the application.

    Returns:
        Success message
    """
    cache_manager = get_cache_manager()
    cache_manager.clear()
    return Message(message="All cache cleared successfully")

"""Logging decorator for API routes."""

import asyncio
import functools
import inspect
import logging
import time
import uuid
from collections.abc import Callable
from typing import Any, TypeVar

from fastapi import Request, Response

from app.core.logging_config import mask_sensitive_data

F = TypeVar("F", bound=Callable[..., Any])


def log_route(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to log API route requests and responses.

    Automatically logs:
    - Request method, path, and query parameters
    - Request body (with sensitive data masked)
    - Response status code
    - Execution time
    - User information (if authenticated)
    - Request ID for tracing

    Usage:
        @router.get("/example")
        @log_route
        def example_endpoint(session: SessionDep, current_user: CurrentUser):
            return {"message": "Hello"}
    """
    logger = logging.getLogger(func.__module__)

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        return await _execute_with_logging_async(func, logger, args, kwargs)

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        return _execute_with_logging(func, logger, args, kwargs, is_async=False)

    # Return appropriate wrapper based on whether function is async
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


async def _execute_with_logging_async(
    func: Callable[..., Any],
    logger: logging.Logger,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Execute async function with logging."""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    # Extract request information
    request = _extract_request_from_args(args, kwargs)
    current_user = kwargs.get("current_user")

    # Log request
    user_info = ""
    if current_user:
        user_email = getattr(current_user, "email", "unknown")
        user_id = getattr(current_user, "id", "unknown")
        user_info = f" | User: {user_email} (ID: {user_id})"

    method = request.method if request else "UNKNOWN"
    path = request.url.path if request else func.__name__
    query_params = dict(request.query_params) if request else {}

    logger.info(
        f"[{request_id}] → {method} {path}{user_info} | "
        f"Query: {mask_sensitive_data(query_params)}"
    )

    # Log request body if present (for POST, PUT, PATCH)
    if method in ["POST", "PUT", "PATCH"]:
        body_data = _extract_body_from_kwargs(kwargs)
        if body_data:
            logger.debug(
                f"[{request_id}] Request body: {mask_sensitive_data(body_data)}"
            )

    try:
        # Execute the async function
        result = await func(*args, **kwargs)

        # Log response
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        status_code = _extract_status_code(result)

        logger.info(
            f"[{request_id}] ← {method} {path} | "
            f"Status: {status_code} | Time: {execution_time:.2f}ms"
        )

        # Log response body in debug mode (masked)
        if logger.isEnabledFor(logging.DEBUG):
            response_preview = _get_response_preview(result)
            if response_preview:
                logger.debug(
                    f"[{request_id}] Response: {mask_sensitive_data(response_preview)}"
                )

        return result

    except Exception as e:
        # Log error
        execution_time = (time.time() - start_time) * 1000
        logger.error(
            f"[{request_id}] ✗ {method} {path} | "
            f"Error: {type(e).__name__}: {str(e)} | Time: {execution_time:.2f}ms",
            exc_info=True,
        )
        raise


def _execute_with_logging(
    func: Callable[..., Any],
    logger: logging.Logger,
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    is_async: bool = False,
) -> Any:
    """Execute function with logging (handles both sync and async)."""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    # Extract request information
    request = _extract_request_from_args(args, kwargs)
    current_user = kwargs.get("current_user")

    # Log request
    user_info = ""
    if current_user:
        user_email = getattr(current_user, "email", "unknown")
        user_id = getattr(current_user, "id", "unknown")
        user_info = f" | User: {user_email} (ID: {user_id})"

    method = request.method if request else "UNKNOWN"
    path = request.url.path if request else func.__name__
    query_params = dict(request.query_params) if request else {}

    logger.info(
        f"[{request_id}] → {method} {path}{user_info} | "
        f"Query: {mask_sensitive_data(query_params)}"
    )

    # Log request body if present (for POST, PUT, PATCH)
    if method in ["POST", "PUT", "PATCH"]:
        body_data = _extract_body_from_kwargs(kwargs)
        if body_data:
            logger.debug(
                f"[{request_id}] Request body: {mask_sensitive_data(body_data)}"
            )

    try:
        # Execute the function
        result = func(*args, **kwargs)

        # Log response
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        status_code = _extract_status_code(result)

        logger.info(
            f"[{request_id}] ← {method} {path} | "
            f"Status: {status_code} | Time: {execution_time:.2f}ms"
        )

        # Log response body in debug mode (masked)
        if logger.isEnabledFor(logging.DEBUG):
            response_preview = _get_response_preview(result)
            if response_preview:
                logger.debug(
                    f"[{request_id}] Response: {mask_sensitive_data(response_preview)}"
                )

        return result

    except Exception as e:
        # Log error
        execution_time = (time.time() - start_time) * 1000
        logger.error(
            f"[{request_id}] ✗ {method} {path} | "
            f"Error: {type(e).__name__}: {str(e)} | Time: {execution_time:.2f}ms",
            exc_info=True,
        )
        raise


def _extract_request_from_args(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Any:
    """Extract Request object from function arguments."""
    # Check kwargs first
    if "request" in kwargs:
        return kwargs["request"]

    # Check args for Request instance
    for arg in args:
        if isinstance(arg, Request):
            return arg

    return None


def _extract_body_from_kwargs(kwargs: dict[str, Any]) -> dict[str, Any] | None:
    """Extract request body data from kwargs."""
    # Common parameter names for request bodies
    body_param_names = [
        "body",
        "data",
        "item_in",
        "user_in",
        "person_in",
        "address_in",
        "profession_in",
        "relationship_in",
        "post_in",
        "support_ticket_in",
        "form_data",
    ]

    for param_name in body_param_names:
        if param_name in kwargs:
            body = kwargs[param_name]
            if hasattr(body, "model_dump"):
                result: dict[str, Any] = body.model_dump()
                return result
            elif hasattr(body, "__dict__"):
                return dict(body.__dict__)
            elif isinstance(body, dict):
                return body

    return None


def _extract_status_code(result: Any) -> int:
    """Extract HTTP status code from response."""
    if isinstance(result, Response):
        return result.status_code
    # Default to 200 for successful responses
    return 200


def _get_response_preview(
    result: Any,
) -> dict[str, Any] | list[Any] | str | int | float | bool | None:
    """Get a preview of the response for logging."""
    if result is None:
        return None

    if isinstance(result, Response):
        return {"status_code": result.status_code}

    if hasattr(result, "model_dump"):
        preview: dict[str, Any] = result.model_dump()
        return preview

    if isinstance(result, dict):
        return dict(result)
    elif isinstance(result, (list, str, int, float, bool)):
        return result

    return {"type": str(type(result))}

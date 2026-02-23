"""Unit tests for person profile image API route registration.

Tests cover:
- All 6 profile image routes are registered
- Routes have correct HTTP methods
- /me routes come before /{person_id} routes

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import pytest

from app.api.routes.person.person import router


def _get_image_routes() -> list[tuple[str, set[str]]]:
    """Extract profile-image routes as (path, methods) tuples."""
    return [
        (r.path, r.methods)
        for r in router.routes
        if hasattr(r, "path") and "profile-image" in r.path
    ]


def _get_all_route_paths() -> list[str]:
    """Get all route paths in registration order."""
    return [r.path for r in router.routes if hasattr(r, "path")]


@pytest.mark.unit
class TestProfileImageRouteRegistration:
    """Tests for profile image route registration."""

    def test_six_profile_image_routes_registered(self) -> None:
        routes = _get_image_routes()
        assert len(routes) == 6

    def test_me_post_route_exists(self) -> None:
        routes = _get_image_routes()
        assert ("/me/profile-image", {"POST"}) in routes

    def test_me_get_route_exists(self) -> None:
        routes = _get_image_routes()
        assert ("/me/profile-image", {"GET"}) in routes

    def test_me_delete_route_exists(self) -> None:
        routes = _get_image_routes()
        assert ("/me/profile-image", {"DELETE"}) in routes

    def test_person_id_post_route_exists(self) -> None:
        routes = _get_image_routes()
        assert ("/{person_id}/profile-image", {"POST"}) in routes

    def test_person_id_get_route_exists(self) -> None:
        routes = _get_image_routes()
        assert ("/{person_id}/profile-image", {"GET"}) in routes

    def test_person_id_delete_route_exists(self) -> None:
        routes = _get_image_routes()
        assert ("/{person_id}/profile-image", {"DELETE"}) in routes

    def test_me_routes_before_person_id_routes(self) -> None:
        """FastAPI matches routes in order — /me must come before /{person_id}."""
        paths = _get_all_route_paths()
        me_indices = [i for i, p in enumerate(paths) if p == "/me/profile-image"]
        pid_indices = [i for i, p in enumerate(paths) if p == "/{person_id}/profile-image"]

        assert me_indices, "/me/profile-image routes not found"
        assert pid_indices, "/{person_id}/profile-image routes not found"
        assert max(me_indices) < min(pid_indices), (
            "/me/profile-image routes must come before /{person_id}/profile-image routes"
        )

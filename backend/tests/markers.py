"""Pytest marker definitions and documentation.

This module documents the custom pytest markers used in the test suite.
Markers are configured in pyproject.toml and can be used to selectively
run different categories of tests.

Usage:
    # Run only unit tests
    pytest -m unit

    # Run only integration tests
    pytest -m integration

    # Run all tests except slow ones
    pytest -m "not slow"

    # Run unit tests that are not slow
    pytest -m "unit and not slow"
"""

import pytest

# Marker decorators for convenience
unit = pytest.mark.unit
integration = pytest.mark.integration
slow = pytest.mark.slow


# Example usage in test files:
#
# @pytest.mark.unit
# def test_something_fast():
#     pass
#
# @pytest.mark.integration
# def test_api_endpoint():
#     pass
#
# @pytest.mark.slow
# @pytest.mark.integration
# def test_complex_workflow():
#     pass

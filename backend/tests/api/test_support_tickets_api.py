"""Property-based tests for Support Ticket API validation."""

import uuid

import pytest
from fastapi.testclient import TestClient
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlmodel import Session

from app.models import User
from app.schemas.support_ticket import IssueType


# Custom strategy for text without NUL bytes and surrogates (PostgreSQL doesn't allow them)
def text_without_nul(min_size: int = 0, max_size: int | None = None) -> st.SearchStrategy[str]:
    """Generate text without NUL bytes and surrogates which PostgreSQL/UTF-8 rejects."""
    return st.text(
        min_size=min_size,
        max_size=max_size,
        alphabet=st.characters(
            blacklist_categories=("Cs",),  # Surrogate characters
            blacklist_characters="\x00",  # NUL byte
        ),
    )


def get_auth_headers(client: TestClient, db: Session) -> tuple[dict[str, str], User]:
    """Create a test user and return auth headers."""
    from datetime import timedelta
    
    # Create test user
    test_user = User(
        email=f"test_{uuid.uuid4()}@example.com",
        hashed_password="test_password",
        is_active=True,
        is_superuser=False,
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)

    # Get token
    from app.core import security
    access_token = security.create_access_token(
        test_user.id, expires_delta=timedelta(minutes=30)
    )
    headers = {"Authorization": f"Bearer {access_token}"}
    
    return headers, test_user


class TestTitleLengthConstraint:
    """Tests for Property 4: Title length constraint.
    
    **Feature: issue-tracking, Property 4: Title length constraint**
    **Validates: Requirements 2.1, 1.5**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        title=text_without_nul(min_size=101, max_size=200),
        description=text_without_nul(min_size=1, max_size=100),
    )
    def test_title_exceeding_100_chars_returns_422(
        self,
        client: TestClient,
        db: Session,
        title: str,
        description: str,
    ) -> None:
        """Property 4: Titles exceeding 100 characters should return 422 validation error."""
        headers, test_user = get_auth_headers(client, db)

        # Create ticket with title > 100 chars
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": title,
            "description": description,
        }

        response = client.post("/api/v1/support-tickets/", json=ticket_data, headers=headers)

        # Should return 422 validation error
        assert response.status_code == 422, f"Expected 422 for title length {len(title)}, got {response.status_code}"

        # Cleanup
        db.delete(test_user)
        db.commit()


class TestDescriptionLengthConstraint:
    """Tests for Property 5: Description length constraint.
    
    **Feature: issue-tracking, Property 5: Description length constraint**
    **Validates: Requirements 2.2**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        title=text_without_nul(min_size=1, max_size=100),
        description=text_without_nul(min_size=2001, max_size=3000),
    )
    def test_description_exceeding_2000_chars_returns_422(
        self,
        client: TestClient,
        db: Session,
        title: str,
        description: str,
    ) -> None:
        """Property 5: Descriptions exceeding 2000 characters should return 422 validation error."""
        headers, test_user = get_auth_headers(client, db)

        # Create ticket with description > 2000 chars
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": title,
            "description": description,
        }

        response = client.post("/api/v1/support-tickets/", json=ticket_data, headers=headers)

        # Should return 422 validation error
        assert response.status_code == 422, f"Expected 422 for description length {len(description)}, got {response.status_code}"

        # Cleanup
        db.delete(test_user)
        db.commit()


class TestRequiredFieldValidation:
    """Tests for Property 6: Required field validation.
    
    **Feature: issue-tracking, Property 6: Required field validation**
    **Validates: Requirements 2.3, 2.4, 2.5**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        title=text_without_nul(min_size=1, max_size=100),
        description=text_without_nul(min_size=1, max_size=2000),
    )
    def test_missing_issue_type_returns_422(
        self,
        client: TestClient,
        db: Session,
        title: str,
        description: str,
    ) -> None:
        """Property 6: Missing issue_type should return 422 validation error."""
        headers, test_user = get_auth_headers(client, db)

        # Create ticket without issue_type
        ticket_data = {
            "title": title,
            "description": description,
        }

        response = client.post("/api/v1/support-tickets/", json=ticket_data, headers=headers)

        # Should return 422 validation error
        assert response.status_code == 422, f"Expected 422 for missing issue_type, got {response.status_code}"

        # Cleanup
        db.delete(test_user)
        db.commit()

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        description=text_without_nul(min_size=1, max_size=2000),
    )
    def test_missing_title_returns_422(
        self,
        client: TestClient,
        db: Session,
        description: str,
    ) -> None:
        """Property 6: Missing title should return 422 validation error."""
        headers, test_user = get_auth_headers(client, db)

        # Create ticket without title
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "description": description,
        }

        response = client.post("/api/v1/support-tickets/", json=ticket_data, headers=headers)

        # Should return 422 validation error
        assert response.status_code == 422, f"Expected 422 for missing title, got {response.status_code}"

        # Cleanup
        db.delete(test_user)
        db.commit()

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        title=text_without_nul(min_size=1, max_size=100),
    )
    def test_missing_description_returns_422(
        self,
        client: TestClient,
        db: Session,
        title: str,
    ) -> None:
        """Property 6: Missing description should return 422 validation error."""
        headers, test_user = get_auth_headers(client, db)

        # Create ticket without description
        ticket_data = {
            "issue_type": IssueType.BUG.value,
            "title": title,
        }

        response = client.post("/api/v1/support-tickets/", json=ticket_data, headers=headers)

        # Should return 422 validation error
        assert response.status_code == 422, f"Expected 422 for missing description, got {response.status_code}"

        # Cleanup
        db.delete(test_user)
        db.commit()

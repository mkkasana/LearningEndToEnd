"""Property-based tests for SupportTicketService."""

import uuid
from datetime import datetime, timezone

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from sqlmodel import Session

from app.db_models.support_ticket import SupportTicket
from app.models import User
from app.schemas.support_ticket import IssueStatus, IssueType
from app.services.support_ticket_service import SupportTicketService


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


class TestSupportTicketOwnershipValidation:
    """Tests for Property 1: SupportTicket ownership validation.
    
    **Feature: issue-tracking, Property 1: SupportTicket ownership validation**
    **Validates: Requirements 8.1, 8.2**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        issue_type=st.sampled_from([IssueType.BUG, IssueType.FEATURE_REQUEST]),
        title=text_without_nul(min_size=1, max_size=100),
        description=text_without_nul(min_size=1, max_size=2000),
    )
    def test_non_admin_can_only_access_own_tickets(
        self,
        db: Session,
        issue_type: IssueType,
        title: str,
        description: str,
    ) -> None:
        """Property 1: Non-admin users can only access their own tickets."""
        service = SupportTicketService(db)
        
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

        # Create another user who will be the "other" user
        other_user = User(
            email=f"other_{uuid.uuid4()}@example.com",
            hashed_password="other_password",
            is_active=True,
            is_superuser=False,
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        # Create a ticket owned by test_user
        ticket = SupportTicket(
            user_id=test_user.id,
            issue_type=issue_type.value,
            title=title,
            description=description,
            status=IssueStatus.OPEN.value,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        # Test that the owner can access their own ticket
        can_owner_access = service.can_user_access_support_ticket(
            ticket, test_user.id, is_superuser=False
        )
        assert can_owner_access is True, "Owner should be able to access their own ticket"

        # Test that another non-admin user cannot access the ticket
        can_other_access = service.can_user_access_support_ticket(
            ticket, other_user.id, is_superuser=False
        )
        assert can_other_access is False, "Non-admin user should not access other user's ticket"

        # Cleanup
        db.delete(ticket)
        db.delete(other_user)
        db.delete(test_user)
        db.commit()

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        issue_type=st.sampled_from([IssueType.BUG, IssueType.FEATURE_REQUEST]),
        title=text_without_nul(min_size=1, max_size=100),
        description=text_without_nul(min_size=1, max_size=2000),
    )
    def test_admin_can_access_all_tickets(
        self,
        db: Session,
        issue_type: IssueType,
        title: str,
        description: str,
    ) -> None:
        """Property 1: Admin users can access all tickets."""
        service = SupportTicketService(db)
        
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

        # Create admin user
        admin_user = User(
            email=f"admin_{uuid.uuid4()}@example.com",
            hashed_password="admin_password",
            is_active=True,
            is_superuser=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        # Create a ticket owned by test_user
        ticket = SupportTicket(
            user_id=test_user.id,
            issue_type=issue_type.value,
            title=title,
            description=description,
            status=IssueStatus.OPEN.value,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        # Test that admin can access any ticket
        can_admin_access = service.can_user_access_support_ticket(
            ticket, admin_user.id, is_superuser=True
        )
        assert can_admin_access is True, "Admin should be able to access any ticket"

        # Cleanup
        db.delete(ticket)
        db.delete(admin_user)
        db.delete(test_user)
        db.commit()


class TestStatusTransitions:
    """Tests for Property 2 and 3: Status transition validity and reversal.
    
    **Feature: issue-tracking, Property 2: Status transition validity**
    **Validates: Requirements 5.1, 5.3**
    
    **Feature: issue-tracking, Property 3: Status transition reversal**
    **Validates: Requirements 5.2, 5.3**
    """

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        issue_type=st.sampled_from([IssueType.BUG, IssueType.FEATURE_REQUEST]),
        title=text_without_nul(min_size=1, max_size=100),
        description=text_without_nul(min_size=1, max_size=2000),
    )
    def test_resolve_sets_resolved_fields(
        self,
        db: Session,
        issue_type: IssueType,
        title: str,
        description: str,
    ) -> None:
        """Property 2: Resolving a ticket sets resolved_at and resolved_by_user_id."""
        service = SupportTicketService(db)
        
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

        # Create admin user
        admin_user = User(
            email=f"admin_{uuid.uuid4()}@example.com",
            hashed_password="admin_password",
            is_active=True,
            is_superuser=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        # Create an open ticket
        ticket = SupportTicket(
            user_id=test_user.id,
            issue_type=issue_type.value,
            title=title,
            description=description,
            status=IssueStatus.OPEN.value,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        # Record the time before resolution
        before_resolve = datetime.now(timezone.utc)

        # Resolve the ticket
        resolved_ticket = service.resolve_support_ticket(ticket, admin_user.id)
        db.refresh(resolved_ticket)

        # Verify status changed to closed
        assert resolved_ticket.status == IssueStatus.CLOSED.value, "Status should be closed"

        # Verify resolved_at is set and not None
        assert resolved_ticket.resolved_at is not None, "resolved_at should be set"
        assert resolved_ticket.resolved_at >= before_resolve, "resolved_at should be recent"

        # Verify resolved_by_user_id is set
        assert (
            resolved_ticket.resolved_by_user_id == admin_user.id
        ), "resolved_by_user_id should be set to admin"

        # Cleanup
        db.delete(resolved_ticket)
        db.delete(admin_user)
        db.delete(test_user)
        db.commit()

    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    @given(
        issue_type=st.sampled_from([IssueType.BUG, IssueType.FEATURE_REQUEST]),
        title=text_without_nul(min_size=1, max_size=100),
        description=text_without_nul(min_size=1, max_size=2000),
    )
    def test_reopen_clears_resolved_fields(
        self,
        db: Session,
        issue_type: IssueType,
        title: str,
        description: str,
    ) -> None:
        """Property 3: Reopening a ticket clears resolved_at and resolved_by_user_id."""
        service = SupportTicketService(db)
        
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

        # Create admin user
        admin_user = User(
            email=f"admin_{uuid.uuid4()}@example.com",
            hashed_password="admin_password",
            is_active=True,
            is_superuser=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        # Create a closed ticket with resolved fields set
        ticket = SupportTicket(
            user_id=test_user.id,
            issue_type=issue_type.value,
            title=title,
            description=description,
            status=IssueStatus.CLOSED.value,
            resolved_at=datetime.now(timezone.utc),
            resolved_by_user_id=admin_user.id,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        # Reopen the ticket
        reopened_ticket = service.reopen_support_ticket(ticket)
        db.refresh(reopened_ticket)

        # Verify status changed to open
        assert reopened_ticket.status == IssueStatus.OPEN.value, "Status should be open"

        # Verify resolved_at is cleared (set to None)
        assert reopened_ticket.resolved_at is None, "resolved_at should be None"

        # Verify resolved_by_user_id is cleared (set to None)
        assert reopened_ticket.resolved_by_user_id is None, "resolved_by_user_id should be None"

        # Cleanup
        db.delete(reopened_ticket)
        db.delete(admin_user)
        db.delete(test_user)
        db.commit()

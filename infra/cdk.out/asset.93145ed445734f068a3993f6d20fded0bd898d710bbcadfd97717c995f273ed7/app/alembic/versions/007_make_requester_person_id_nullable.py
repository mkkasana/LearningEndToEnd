"""make requester_person_id nullable in person_attachment_request

Revision ID: 007_nullable_requester_person
Revises: 006_attachment_approval
Create Date: 2026-02-01

This migration makes requester_person_id nullable so it can be cleared
when the temporary person is deleted during approve/deny operations.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_nullable_requester_person'
down_revision = '006_attachment_approval'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make requester_person_id nullable
    op.alter_column(
        'person_attachment_request',
        'requester_person_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True
    )
    # Make requester_user_id nullable (needed for deny which deletes the user)
    op.alter_column(
        'person_attachment_request',
        'requester_user_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True
    )


def downgrade() -> None:
    # Make requester_user_id non-nullable again
    op.alter_column(
        'person_attachment_request',
        'requester_user_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False
    )
    # Make requester_person_id non-nullable again
    # Note: This will fail if there are NULL values in the column
    op.alter_column(
        'person_attachment_request',
        'requester_person_id',
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False
    )

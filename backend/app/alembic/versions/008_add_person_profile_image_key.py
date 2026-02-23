"""add profile_image_key to person table

Revision ID: 008_profile_image_key
Revises: 007_nullable_requester_person
Create Date: 2026-02-23

Adds a nullable profile_image_key column to the person table
to store the storage key (filename) of the person's profile image.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008_profile_image_key'
down_revision = '007_nullable_requester_person'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('person', sa.Column('profile_image_key', sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column('person', 'profile_image_key')

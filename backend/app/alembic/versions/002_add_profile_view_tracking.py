"""add profile_view_tracking table

Revision ID: 002_add_profile_view_tracking
Revises: 001_add_support_ticket
Create Date: 2025-12-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_profile_view_tracking'
down_revision = '001_add_support_ticket'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if table already exists (may have been created by SQLModel.metadata.create_all)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'profile_view_tracking' not in tables:
        # Create profile_view_tracking table
        op.create_table(
            'profile_view_tracking',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('viewed_person_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('viewer_person_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('view_count', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('is_aggregated', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
            
            # Foreign key constraints
            sa.ForeignKeyConstraint(['viewed_person_id'], ['person.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['viewer_person_id'], ['person.id'], ondelete='CASCADE'),
        )
    
    # Create indexes if they don't exist
    indexes = [idx['name'] for idx in inspector.get_indexes('profile_view_tracking')]
    
    if 'idx_profile_view_tracking_viewed_person' not in indexes:
        op.create_index(
            'idx_profile_view_tracking_viewed_person',
            'profile_view_tracking',
            ['viewed_person_id']
        )
    if 'idx_profile_view_tracking_viewer_person' not in indexes:
        op.create_index(
            'idx_profile_view_tracking_viewer_person',
            'profile_view_tracking',
            ['viewer_person_id']
        )
    if 'idx_profile_view_tracking_composite' not in indexes:
        op.create_index(
            'idx_profile_view_tracking_composite',
            'profile_view_tracking',
            ['viewed_person_id', 'viewer_person_id', 'is_aggregated']
        )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_profile_view_tracking_composite', table_name='profile_view_tracking')
    op.drop_index('idx_profile_view_tracking_viewer_person', table_name='profile_view_tracking')
    op.drop_index('idx_profile_view_tracking_viewed_person', table_name='profile_view_tracking')
    
    # Drop table
    op.drop_table('profile_view_tracking')

"""add support_ticket table

Revision ID: 001_add_support_ticket
Revises: 000_initial
Create Date: 2025-12-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_support_ticket'
down_revision = '000_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create support_ticket table
    op.create_table(
        'support_ticket',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('issue_type', sa.String(20), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='open'),
        sa.Column('resolved_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by_user_id'], ['user.id'], ondelete='SET NULL'),
        
        # Check constraints
        sa.CheckConstraint("issue_type IN ('bug', 'feature_request')", name='check_issue_type'),
        sa.CheckConstraint("status IN ('open', 'closed')", name='check_status'),
        sa.CheckConstraint("char_length(description) <= 2000", name='check_description_length'),
    )
    
    # Create indexes
    op.create_index('idx_support_ticket_user_id', 'support_ticket', ['user_id'])
    op.create_index('idx_support_ticket_status', 'support_ticket', ['status'])
    op.create_index('idx_support_ticket_created_at', 'support_ticket', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_support_ticket_type', 'support_ticket', ['issue_type'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_support_ticket_type', table_name='support_ticket')
    op.drop_index('idx_support_ticket_created_at', table_name='support_ticket')
    op.drop_index('idx_support_ticket_status', table_name='support_ticket')
    op.drop_index('idx_support_ticket_user_id', table_name='support_ticket')
    
    # Drop table
    op.drop_table('support_ticket')

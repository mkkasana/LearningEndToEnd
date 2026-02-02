"""add is_active to person and create person_attachment_request table

Revision ID: 006_attachment_approval
Revises: 005_add_person_marital_status
Create Date: 2026-02-01

This migration:
1. Adds 'is_active' boolean column to person table with default True
2. Creates 'person_attachment_request' table for tracking attachment requests
3. Creates indexes for efficient queries on the attachment request table

**Validates: Requirements 1.1, 2.1**
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_attachment_approval'
down_revision = '005_add_person_marital_status'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Get existing columns in person table
    existing_columns = [col['name'] for col in inspector.get_columns('person')]
    
    # Add is_active column to person table if it doesn't exist
    if 'is_active' not in existing_columns:
        op.add_column(
            'person',
            sa.Column(
                'is_active',
                sa.Boolean(),
                nullable=False,
                server_default='true'
            )
        )
    
    # Check if person_attachment_request table already exists
    existing_tables = inspector.get_table_names()
    
    if 'person_attachment_request' not in existing_tables:
        # Create person_attachment_request table
        op.create_table(
            'person_attachment_request',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('requester_user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('requester_person_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('target_person_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('approver_user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column('resolved_at', sa.DateTime(), nullable=True),
            sa.Column('resolved_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
            # Foreign key constraints
            sa.ForeignKeyConstraint(['requester_user_id'], ['user.id'], name='fk_attachment_request_requester_user'),
            sa.ForeignKeyConstraint(['requester_person_id'], ['person.id'], name='fk_attachment_request_requester_person'),
            sa.ForeignKeyConstraint(['target_person_id'], ['person.id'], name='fk_attachment_request_target_person'),
            sa.ForeignKeyConstraint(['approver_user_id'], ['user.id'], name='fk_attachment_request_approver_user'),
            sa.ForeignKeyConstraint(['resolved_by_user_id'], ['user.id'], name='fk_attachment_request_resolved_by_user'),
        )
        
        # Create indexes for efficient queries
        op.create_index(
            'idx_attachment_request_requester_user',
            'person_attachment_request',
            ['requester_user_id']
        )
        op.create_index(
            'idx_attachment_request_requester_person',
            'person_attachment_request',
            ['requester_person_id']
        )
        op.create_index(
            'idx_attachment_request_target_person',
            'person_attachment_request',
            ['target_person_id']
        )
        op.create_index(
            'idx_attachment_request_approver_user',
            'person_attachment_request',
            ['approver_user_id']
        )
        op.create_index(
            'idx_attachment_request_status',
            'person_attachment_request',
            ['status']
        )
        
        # Create check constraint for valid status values
        op.create_check_constraint(
            'check_attachment_request_status',
            'person_attachment_request',
            "status IN ('pending', 'approved', 'denied', 'cancelled')"
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Check if person_attachment_request table exists
    existing_tables = inspector.get_table_names()
    
    if 'person_attachment_request' in existing_tables:
        # Drop indexes
        op.drop_index('idx_attachment_request_requester_user', table_name='person_attachment_request')
        op.drop_index('idx_attachment_request_requester_person', table_name='person_attachment_request')
        op.drop_index('idx_attachment_request_target_person', table_name='person_attachment_request')
        op.drop_index('idx_attachment_request_approver_user', table_name='person_attachment_request')
        op.drop_index('idx_attachment_request_status', table_name='person_attachment_request')
        
        # Drop check constraint
        op.drop_constraint('check_attachment_request_status', 'person_attachment_request', type_='check')
        
        # Drop table
        op.drop_table('person_attachment_request')
    
    # Get existing columns in person table
    existing_columns = [col['name'] for col in inspector.get_columns('person')]
    
    # Drop is_active column if it exists
    if 'is_active' in existing_columns:
        op.drop_column('person', 'is_active')

"""add marital_status column to person table

Revision ID: 005_add_person_marital_status
Revises: 004_add_person_life_event
Create Date: 2026-01-24

This migration:
1. Adds a 'marital_status' column to the person table with default 'unknown'
2. Sets the column as NOT NULL
3. Updates existing records to 'unknown'

**Validates: Requirements 5.1, 5.2, 5.3**
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_add_person_marital_status'
down_revision = '004_add_person_life_event'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Get existing columns in person table
    existing_columns = [col['name'] for col in inspector.get_columns('person')]
    
    # Add marital_status column if it doesn't exist
    if 'marital_status' not in existing_columns:
        op.add_column(
            'person',
            sa.Column(
                'marital_status',
                sa.String(20),
                nullable=False,
                server_default='unknown'
            )
        )
    
    # Add check constraint for valid marital_status values
    existing_constraints = inspector.get_check_constraints('person')
    constraint_names = [c['name'] for c in existing_constraints]
    
    if 'check_marital_status' not in constraint_names:
        op.create_check_constraint(
            'check_marital_status',
            'person',
            "marital_status IN ('unknown', 'single', 'married', 'divorced', 'widowed', 'separated')"
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Get existing columns in person table
    existing_columns = [col['name'] for col in inspector.get_columns('person')]
    
    # Drop check constraint if it exists
    existing_constraints = inspector.get_check_constraints('person')
    constraint_names = [c['name'] for c in existing_constraints]
    
    if 'check_marital_status' in constraint_names:
        op.drop_constraint('check_marital_status', 'person', type_='check')
    
    # Drop marital_status column if it exists
    if 'marital_status' in existing_columns:
        op.drop_column('person', 'marital_status')

"""add user role column and migrate from is_superuser

Revision ID: 003_add_user_role
Revises: 002_add_profile_view_tracking
Create Date: 2026-01-03

This migration:
1. Adds a 'role' column to the user table with default 'user'
2. Migrates existing data: is_superuser=True → role='superuser'
3. Removes the 'is_superuser' column

**Validates: Requirements 6.1, 6.2, 6.3**
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_user_role'
down_revision = '002_add_profile_view_tracking'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Get existing columns in user table
    existing_columns = [col['name'] for col in inspector.get_columns('user')]
    
    # Step 1: Add 'role' column if it doesn't exist
    if 'role' not in existing_columns:
        op.add_column(
            'user',
            sa.Column(
                'role',
                sa.String(20),
                nullable=False,
                server_default='user'
            )
        )
        
        # Step 2: Migrate existing data from is_superuser to role
        # is_superuser=True → role='superuser'
        # is_superuser=False → role='user' (already default)
        if 'is_superuser' in existing_columns:
            op.execute(
                """
                UPDATE "user" 
                SET role = 'superuser' 
                WHERE is_superuser = true
                """
            )
    
    # Step 3: Drop is_superuser column if it exists
    if 'is_superuser' in existing_columns:
        op.drop_column('user', 'is_superuser')
    
    # Add check constraint for valid role values
    # First check if constraint already exists
    existing_constraints = inspector.get_check_constraints('user')
    constraint_names = [c['name'] for c in existing_constraints]
    
    if 'check_user_role' not in constraint_names:
        op.create_check_constraint(
            'check_user_role',
            'user',
            "role IN ('user', 'superuser', 'admin')"
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    # Get existing columns in user table
    existing_columns = [col['name'] for col in inspector.get_columns('user')]
    
    # Step 1: Add is_superuser column back if it doesn't exist
    if 'is_superuser' not in existing_columns:
        op.add_column(
            'user',
            sa.Column(
                'is_superuser',
                sa.Boolean(),
                nullable=False,
                server_default='false'
            )
        )
        
        # Step 2: Migrate data back from role to is_superuser
        # role='superuser' or role='admin' → is_superuser=True
        # role='user' → is_superuser=False (already default)
        if 'role' in existing_columns:
            op.execute(
                """
                UPDATE "user" 
                SET is_superuser = true 
                WHERE role IN ('superuser', 'admin')
                """
            )
    
    # Step 3: Drop check constraint if it exists
    existing_constraints = inspector.get_check_constraints('user')
    constraint_names = [c['name'] for c in existing_constraints]
    
    if 'check_user_role' in constraint_names:
        op.drop_constraint('check_user_role', 'user', type_='check')
    
    # Step 4: Drop role column if it exists
    if 'role' in existing_columns:
        op.drop_column('user', 'role')

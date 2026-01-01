"""add user role column and migrate from is_superuser

Revision ID: 003_add_user_role
Revises: 002_add_profile_view_tracking
Create Date: 2026-01-01

This migration:
1. Adds a 'role' column with default 'user' (if not already created by SQLModel)
2. Migrates existing data: is_superuser=True → role='superuser'
3. Removes the 'is_superuser' column

Requirements: 6.1, 6.2, 6.3

Note: If the database was created fresh with SQLModel.metadata.create_all(),
the role column will already exist as a PostgreSQL enum type. This migration
handles both cases: fresh installs and upgrades from existing databases.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_user_role'
down_revision = '002_add_profile_view_tracking'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check current column state
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('user')]
    
    has_is_superuser = 'is_superuser' in columns
    has_role = 'role' in columns
    
    # If role column already exists (created by SQLModel.metadata.create_all),
    # we just need to handle is_superuser migration if it exists
    if has_role:
        # Role column already exists (fresh install with SQLModel)
        # Just remove is_superuser if it exists
        if has_is_superuser:
            op.drop_column('user', 'is_superuser')
        return
    
    # Role column doesn't exist - this is an upgrade from an older schema
    # Create the userrole enum type first
    userrole_enum = postgresql.ENUM('user', 'superuser', 'admin', name='userrole', create_type=False)
    
    # Check if enum type exists
    result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'userrole'"))
    enum_exists = result.fetchone() is not None
    
    if not enum_exists:
        userrole_enum.create(conn)
    
    # Add role column with enum type
    op.add_column(
        'user',
        sa.Column(
            'role',
            userrole_enum,
            nullable=False,
            server_default='user'
        )
    )
    
    # Migrate existing data from is_superuser to role
    if has_is_superuser:
        # Update users where is_superuser=True to have role='superuser'
        op.execute(
            """
            UPDATE "user" 
            SET role = 'superuser' 
            WHERE is_superuser = true
            """
        )
        
        # Remove is_superuser column
        op.drop_column('user', 'is_superuser')


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('user')]
    
    has_role = 'role' in columns
    has_is_superuser = 'is_superuser' in columns
    
    if not has_role:
        return
    
    # Add is_superuser column back if it doesn't exist
    if not has_is_superuser:
        op.add_column(
            'user',
            sa.Column(
                'is_superuser',
                sa.Boolean(),
                nullable=False,
                server_default='false'
            )
        )
        
        # Migrate role data back to is_superuser
        # superuser and admin roles become is_superuser=True
        op.execute(
            """
            UPDATE "user" 
            SET is_superuser = true 
            WHERE role IN ('superuser', 'admin')
            """
        )
    
    # Note: We don't drop the role column or enum type in downgrade
    # as it may be used by the SQLModel schema

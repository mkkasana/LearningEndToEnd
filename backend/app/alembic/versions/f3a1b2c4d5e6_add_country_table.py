"""Add country table for metadata

Revision ID: f3a1b2c4d5e6
Revises: 1a31ce608336
Create Date: 2024-12-22 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'f3a1b2c4d5e6'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # Create country table
    op.create_table(
        'country',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('code')
    )
    
    # Create indexes
    op.create_index(op.f('ix_country_name'), 'country', ['name'], unique=True)
    op.create_index(op.f('ix_country_code'), 'country', ['code'], unique=True)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_country_code'), table_name='country')
    op.drop_index(op.f('ix_country_name'), table_name='country')
    
    # Drop table
    op.drop_table('country')

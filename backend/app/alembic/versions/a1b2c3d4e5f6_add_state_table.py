"""Add state table for metadata

Revision ID: a1b2c3d4e5f6
Revises: f3a1b2c4d5e6
Create Date: 2024-12-22 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'f3a1b2c4d5e6'
branch_labels = None
depends_on = None


def upgrade():
    # Create state table
    op.create_table(
        'state',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=True),
        sa.Column('country_id', UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['country_id'], ['country.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_state_name'), 'state', ['name'], unique=False)
    op.create_index(op.f('ix_state_country_id'), 'state', ['country_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_state_country_id'), table_name='state')
    op.drop_index(op.f('ix_state_name'), table_name='state')
    
    # Drop table
    op.drop_table('state')

"""Add district table for metadata

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2024-12-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Create district table
    op.create_table(
        'district',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=True),
        sa.Column('state_id', UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['state_id'], ['state.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_district_name'), 'district', ['name'], unique=False)
    op.create_index(op.f('ix_district_state_id'), 'district', ['state_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_district_state_id'), table_name='district')
    op.drop_index(op.f('ix_district_name'), table_name='district')
    
    # Drop table
    op.drop_table('district')

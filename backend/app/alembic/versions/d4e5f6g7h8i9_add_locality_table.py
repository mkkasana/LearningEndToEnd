"""Add locality table for metadata

Revision ID: d4e5f6g7h8i9
Revises: c3d4e5f6g7h8
Create Date: 2024-12-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'd4e5f6g7h8i9'
down_revision = 'c3d4e5f6g7h8'
branch_labels = None
depends_on = None


def upgrade():
    # Create locality table
    op.create_table(
        'locality',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=True),
        sa.Column('sub_district_id', UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['sub_district_id'], ['subdistrict.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_locality_name'), 'locality', ['name'], unique=False)
    op.create_index(op.f('ix_locality_sub_district_id'), 'locality', ['sub_district_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_locality_sub_district_id'), table_name='locality')
    op.drop_index(op.f('ix_locality_name'), table_name='locality')
    
    # Drop table
    op.drop_table('locality')

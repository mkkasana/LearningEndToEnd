"""Add sub_district table for metadata

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2024-12-23 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6g7h8'
down_revision = 'b2c3d4e5f6g7'
branch_labels = None
depends_on = None


def upgrade():
    # Create subdistrict table
    op.create_table(
        'subdistrict',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=True),
        sa.Column('district_id', UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['district_id'], ['district.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_subdistrict_name'), 'subdistrict', ['name'], unique=False)
    op.create_index(op.f('ix_subdistrict_district_id'), 'subdistrict', ['district_id'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_subdistrict_district_id'), table_name='subdistrict')
    op.drop_index(op.f('ix_subdistrict_name'), table_name='subdistrict')
    
    # Drop table
    op.drop_table('subdistrict')

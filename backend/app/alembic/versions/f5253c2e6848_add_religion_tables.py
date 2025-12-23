"""add_religion_tables

Revision ID: f5253c2e6848
Revises: e5f6g7h8i9j0
Create Date: 2024-12-23 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f5253c2e6848'
down_revision = 'e5f6g7h8i9j0'
branch_labels = None
depends_on = None


def upgrade():
    # Create religion table
    op.create_table('religion',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('code', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_religion_code'), 'religion', ['code'], unique=False)
    op.create_index(op.f('ix_religion_name'), 'religion', ['name'], unique=False)
    
    # Create religion_category table
    op.create_table('religion_category',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('code', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=True),
    sa.Column('religion_id', sa.UUID(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['religion_id'], ['religion.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_religion_category_name'), 'religion_category', ['name'], unique=False)
    op.create_index(op.f('ix_religion_category_religion_id'), 'religion_category', ['religion_id'], unique=False)
    
    # Create religion_sub_category table
    op.create_table('religion_sub_category',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('code', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=True),
    sa.Column('category_id', sa.UUID(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['religion_category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_religion_sub_category_category_id'), 'religion_sub_category', ['category_id'], unique=False)
    op.create_index(op.f('ix_religion_sub_category_name'), 'religion_sub_category', ['name'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_religion_sub_category_name'), table_name='religion_sub_category')
    op.drop_index(op.f('ix_religion_sub_category_category_id'), table_name='religion_sub_category')
    op.drop_table('religion_sub_category')
    op.drop_index(op.f('ix_religion_category_religion_id'), table_name='religion_category')
    op.drop_index(op.f('ix_religion_category_name'), table_name='religion_category')
    op.drop_table('religion_category')
    op.drop_index(op.f('ix_religion_name'), table_name='religion')
    op.drop_index(op.f('ix_religion_code'), table_name='religion')
    op.drop_table('religion')

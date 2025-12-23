"""Add profession table for person metadata

Revision ID: g6h7i8j9k0l1
Revises: f5253c2e6848
Create Date: 2024-12-23 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'g6h7i8j9k0l1'
down_revision = 'f5253c2e6848'
branch_labels = None
depends_on = None


def upgrade():
    # Create person_profession table
    op.create_table(
        'person_profession',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('weight', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_person_profession_name'), 'person_profession', ['name'], unique=True)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_person_profession_name'), table_name='person_profession')
    
    # Drop table
    op.drop_table('person_profession')

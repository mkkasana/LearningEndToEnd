"""Add gender table for person metadata

Revision ID: h7i8j9k0l1m2
Revises: g6h7i8j9k0l1
Create Date: 2024-12-23 12:00:00.000000

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "h7i8j9k0l1m2"
down_revision = "g6h7i8j9k0l1"
branch_labels = None
depends_on = None


def upgrade():
    # Create person_gender table
    op.create_table(
        "person_gender",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_person_gender_name"), "person_gender", ["name"], unique=True
    )
    op.create_index(
        op.f("ix_person_gender_code"), "person_gender", ["code"], unique=True
    )


def downgrade():
    # Drop indexes
    op.drop_index(op.f("ix_person_gender_code"), table_name="person_gender")
    op.drop_index(op.f("ix_person_gender_name"), table_name="person_gender")

    # Drop table
    op.drop_table("person_gender")

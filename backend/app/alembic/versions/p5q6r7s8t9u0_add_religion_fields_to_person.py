"""Add person_religion association table

Revision ID: p5q6r7s8t9u0
Revises: o4p5q6r7s8t9
Create Date: 2024-12-24 15:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "p5q6r7s8t9u0"
down_revision = "o4p5q6r7s8t9"
branch_labels = None
depends_on = None


def upgrade():
    # Create person_religion table
    op.create_table(
        "person_religion",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", UUID(as_uuid=True), nullable=False),
        sa.Column("religion_id", UUID(as_uuid=True), nullable=False),
        sa.Column("religion_category_id", UUID(as_uuid=True), nullable=True),
        sa.Column("religion_sub_category_id", UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["person_id"], ["person.user_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["religion_id"], ["religion.id"]),
        sa.ForeignKeyConstraint(["religion_category_id"], ["religion_category.id"]),
        sa.ForeignKeyConstraint(["religion_sub_category_id"], ["religion_sub_category.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create unique index on person_id (one religion per person)
    op.create_index(
        op.f("ix_person_religion_person_id"),
        "person_religion",
        ["person_id"],
        unique=True,
    )


def downgrade():
    # Drop index
    op.drop_index(op.f("ix_person_religion_person_id"), table_name="person_religion")

    # Drop table
    op.drop_table("person_religion")

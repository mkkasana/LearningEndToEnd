"""Add person_relationship table

Revision ID: m2n3o4p5q6r7
Revises: k0l1m2n3o4p5
Create Date: 2024-12-23 17:00:00.000000

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "m2n3o4p5q6r7"
down_revision = "k0l1m2n3o4p5"
branch_labels = None
depends_on = None


def upgrade():
    # Create person_relationship table
    op.create_table(
        "person_relationship",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", UUID(as_uuid=True), nullable=False),
        sa.Column("related_person_id", UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_type", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["person_id"], ["person.user_id"]),
        sa.ForeignKeyConstraint(["related_person_id"], ["person.user_id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_person_relationship_person_id"),
        "person_relationship",
        ["person_id"],
        unique=False,
    )


def downgrade():
    # Drop indexes
    op.drop_index(
        op.f("ix_person_relationship_person_id"), table_name="person_relationship"
    )

    # Drop table
    op.drop_table("person_relationship")

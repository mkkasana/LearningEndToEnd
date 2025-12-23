"""Add person_metadata table

Revision ID: n3o4p5q6r7s8
Revises: m2n3o4p5q6r7
Create Date: 2024-12-23 18:00:00.000000

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "n3o4p5q6r7s8"
down_revision = "m2n3o4p5q6r7"
branch_labels = None
depends_on = None


def upgrade():
    # Create person_metadata table
    op.create_table(
        "person_metadata",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", UUID(as_uuid=True), nullable=False),
        sa.Column("profile_image_url", sa.String(length=500), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["person_id"], ["person.user_id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_person_metadata_person_id"),
        "person_metadata",
        ["person_id"],
        unique=True,
    )


def downgrade():
    # Drop indexes
    op.drop_index(op.f("ix_person_metadata_person_id"), table_name="person_metadata")

    # Drop table
    op.drop_table("person_metadata")

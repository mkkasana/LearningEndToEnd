"""Add person_profession_association table

Revision ID: k0l1m2n3o4p5
Revises: j9k0l1m2n3o4
Create Date: 2024-12-23 15:00:00.000000

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "k0l1m2n3o4p5"
down_revision = "j9k0l1m2n3o4"
branch_labels = None
depends_on = None


def upgrade():
    # Create person_profession_association table
    op.create_table(
        "person_profession_association",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", UUID(as_uuid=True), nullable=False),
        sa.Column("profession_id", UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["person_id"], ["person.user_id"]),
        sa.ForeignKeyConstraint(["profession_id"], ["person_profession.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_person_profession_association_person_id"),
        "person_profession_association",
        ["person_id"],
        unique=False,
    )


def downgrade():
    # Drop indexes
    op.drop_index(
        op.f("ix_person_profession_association_person_id"),
        table_name="person_profession_association",
    )

    # Drop table
    op.drop_table("person_profession_association")

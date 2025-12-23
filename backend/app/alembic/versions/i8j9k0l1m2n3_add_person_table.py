"""Add person table

Revision ID: i8j9k0l1m2n3
Revises: h7i8j9k0l1m2
Create Date: 2024-12-23 13:00:00.000000

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "i8j9k0l1m2n3"
down_revision = "h7i8j9k0l1m2"
branch_labels = None
depends_on = None


def upgrade():
    # Create person table
    op.create_table(
        "person",
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("middle_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("gender_id", UUID(as_uuid=True), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("date_of_death", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["gender_id"],
            ["person_gender.id"],
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )

    # Create indexes
    op.create_index(op.f("ix_person_gender_id"), "person", ["gender_id"], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f("ix_person_gender_id"), table_name="person")

    # Drop table
    op.drop_table("person")

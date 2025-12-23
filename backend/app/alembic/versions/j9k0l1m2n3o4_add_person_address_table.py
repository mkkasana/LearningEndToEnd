"""Add person_address table

Revision ID: j9k0l1m2n3o4
Revises: i8j9k0l1m2n3
Create Date: 2024-12-23 14:00:00.000000

"""

import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "j9k0l1m2n3o4"
down_revision = "i8j9k0l1m2n3"
branch_labels = None
depends_on = None


def upgrade():
    # Create person_address table
    op.create_table(
        "person_address",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", UUID(as_uuid=True), nullable=False),
        sa.Column("country_id", UUID(as_uuid=True), nullable=False),
        sa.Column("state_id", UUID(as_uuid=True), nullable=True),
        sa.Column("district_id", UUID(as_uuid=True), nullable=True),
        sa.Column("sub_district_id", UUID(as_uuid=True), nullable=True),
        sa.Column("locality_id", UUID(as_uuid=True), nullable=True),
        sa.Column("address_line", sa.Text(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["person_id"], ["person.user_id"]),
        sa.ForeignKeyConstraint(["country_id"], ["address_country.id"]),
        sa.ForeignKeyConstraint(["state_id"], ["address_state.id"]),
        sa.ForeignKeyConstraint(["district_id"], ["address_district.id"]),
        sa.ForeignKeyConstraint(["sub_district_id"], ["address_sub_district.id"]),
        sa.ForeignKeyConstraint(["locality_id"], ["address_locality.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_person_address_person_id"), "person_address", ["person_id"], unique=False
    )


def downgrade():
    # Drop indexes
    op.drop_index(op.f("ix_person_address_person_id"), table_name="person_address")

    # Drop table
    op.drop_table("person_address")

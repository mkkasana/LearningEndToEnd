"""initial schema

Revision ID: 000_initial
Revises: 
Create Date: 2025-12-24

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '000_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use SQLModel to create all tables
    from sqlmodel import SQLModel
    from app.core.db import engine
    
    # Import all models to register them
    from app.db_models import user, item, post
    from app.db_models.person import person, gender
    from app.db_models.person import person_address, person_religion, person_relationship
    from app.db_models.person import person_metadata
    from app.db_models.address import country, state, district, sub_district, locality
    from app.db_models.religion import religion, religion_category, religion_sub_category
    
    # Create all tables
    SQLModel.metadata.create_all(engine)


def downgrade() -> None:
    pass

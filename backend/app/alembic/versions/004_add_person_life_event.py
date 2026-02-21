"""add person_life_event table

Revision ID: 004_add_person_life_event
Revises: 003_add_user_role
Create Date: 2026-01-04

This migration creates the person_life_event table for storing
significant life events for persons.

**Validates: Requirements 1.2, 2.4, 2.5, 2.6, 2.7, 2.9, 2.12**
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_person_life_event'
down_revision = '003_add_user_role'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'support_ticket' in inspector.get_table_names():
        return

    # Create person_life_event table
    op.create_table(
        'person_life_event',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('event_year', sa.Integer(), nullable=False),
        sa.Column('event_month', sa.Integer(), nullable=True),
        sa.Column('event_date', sa.Integer(), nullable=True),
        sa.Column('country_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('state_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('district_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sub_district_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('locality_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('address_details', sa.String(30), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        
        # Foreign key constraints
        sa.ForeignKeyConstraint(['person_id'], ['person.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['country_id'], ['address_country.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['state_id'], ['address_state.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['district_id'], ['address_district.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sub_district_id'], ['address_sub_district.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['locality_id'], ['address_locality.id'], ondelete='SET NULL'),
        
        # Check constraints
        sa.CheckConstraint(
            "event_type IN ('birth', 'marriage', 'death', 'purchase', 'sale', 'achievement', 'education', 'career', 'health', 'travel', 'other')",
            name='check_event_type'
        ),
        sa.CheckConstraint('event_month >= 1 AND event_month <= 12', name='check_event_month'),
        sa.CheckConstraint('event_date >= 1 AND event_date <= 31', name='check_event_date'),
    )
    
    # Create indexes
    op.create_index('idx_person_life_event_person_id', 'person_life_event', ['person_id'])
    op.create_index('idx_person_life_event_year', 'person_life_event', ['event_year'], postgresql_ops={'event_year': 'DESC'})


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_person_life_event_year', table_name='person_life_event')
    op.drop_index('idx_person_life_event_person_id', table_name='person_life_event')
    
    # Drop table
    op.drop_table('person_life_event')

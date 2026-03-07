"""initial schema - squashed from migrations 000-008

Revision ID: 000_initial
Revises:
Create Date: 2025-12-24

This is a squashed migration combining all development migrations (000-008)
into a single initial schema. Tables created:
- user, item, post
- address_country, address_state, address_district, address_sub_district, address_locality
- religion, religion_category, religion_sub_category
- person_gender, person, person_metadata, person_address, person_religion,
  person_relationship, person_profession, person_profession_association,
  person_life_event, person_attachment_request
- support_ticket, profile_view_tracking
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '000_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── user ──
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('role', sa.String(20), nullable=False, server_default='user'),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.CheckConstraint("role IN ('user', 'superuser', 'admin')", name='check_user_role'),
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True)

    # ── item ──
    op.create_table(
        'item',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['user.id'], ondelete='CASCADE'),
    )

    # ── post ──
    op.create_table(
        'post',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_published', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
    )
    op.create_index('ix_post_user_id', 'post', ['user_id'])

    # ── address hierarchy ──
    op.create_table(
        'address_country',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(3), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.create_index('ix_address_country_name', 'address_country', ['name'], unique=True)
    op.create_index('ix_address_country_code', 'address_country', ['code'], unique=True)

    op.create_table(
        'address_state',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(10), nullable=True),
        sa.Column('country_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['country_id'], ['address_country.id']),
    )
    op.create_index('ix_address_state_name', 'address_state', ['name'])
    op.create_index('ix_address_state_country_id', 'address_state', ['country_id'])

    op.create_table(
        'address_district',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(10), nullable=True),
        sa.Column('state_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['state_id'], ['address_state.id']),
    )
    op.create_index('ix_address_district_name', 'address_district', ['name'])
    op.create_index('ix_address_district_state_id', 'address_district', ['state_id'])

    op.create_table(
        'address_sub_district',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(10), nullable=True),
        sa.Column('district_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['district_id'], ['address_district.id']),
    )
    op.create_index('ix_address_sub_district_name', 'address_sub_district', ['name'])
    op.create_index('ix_address_sub_district_district_id', 'address_sub_district', ['district_id'])

    op.create_table(
        'address_locality',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(10), nullable=True),
        sa.Column('sub_district_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['sub_district_id'], ['address_sub_district.id']),
    )
    op.create_index('ix_address_locality_name', 'address_locality', ['name'])
    op.create_index('ix_address_locality_sub_district_id', 'address_locality', ['sub_district_id'])

    # ── religion hierarchy ──
    op.create_table(
        'religion',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.create_index('ix_religion_name', 'religion', ['name'], unique=True)
    op.create_index('ix_religion_code', 'religion', ['code'], unique=True)

    op.create_table(
        'religion_category',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(10), nullable=True),
        sa.Column('religion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['religion_id'], ['religion.id']),
    )
    op.create_index('ix_religion_category_name', 'religion_category', ['name'])
    op.create_index('ix_religion_category_religion_id', 'religion_category', ['religion_id'])

    op.create_table(
        'religion_sub_category',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(10), nullable=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['category_id'], ['religion_category.id']),
    )
    op.create_index('ix_religion_sub_category_name', 'religion_sub_category', ['name'])
    op.create_index('ix_religion_sub_category_category_id', 'religion_sub_category', ['category_id'])

    # ── person_gender ──
    op.create_table(
        'person_gender',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(10), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.create_index('ix_person_gender_name', 'person_gender', ['name'], unique=True)
    op.create_index('ix_person_gender_code', 'person_gender', ['code'], unique=True)

    # ── person ──
    op.create_table(
        'person',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_by_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('middle_name', sa.String(100), nullable=True),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('gender_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('date_of_death', sa.Date(), nullable=True),
        sa.Column('marital_status', sa.String(20), nullable=False, server_default='unknown'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('profile_image_key', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['gender_id'], ['person_gender.id']),
        sa.CheckConstraint(
            "marital_status IN ('unknown', 'single', 'married', 'divorced', 'widowed', 'separated')",
            name='check_marital_status',
        ),
    )
    op.create_index('ix_person_user_id', 'person', ['user_id'])
    op.create_index('ix_person_created_by_user_id', 'person', ['created_by_user_id'])

    # ── person_metadata ──
    op.create_table(
        'person_metadata',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('profile_image_url', sa.String(500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['person_id'], ['person.id']),
    )
    op.create_index('ix_person_metadata_person_id', 'person_metadata', ['person_id'])

    # ── person_address ──
    op.create_table(
        'person_address',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('country_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('state_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('district_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('sub_district_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('locality_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('address_line', sa.String(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['person_id'], ['person.id']),
        sa.ForeignKeyConstraint(['country_id'], ['address_country.id']),
        sa.ForeignKeyConstraint(['state_id'], ['address_state.id']),
        sa.ForeignKeyConstraint(['district_id'], ['address_district.id']),
        sa.ForeignKeyConstraint(['sub_district_id'], ['address_sub_district.id']),
        sa.ForeignKeyConstraint(['locality_id'], ['address_locality.id']),
    )
    op.create_index('ix_person_address_person_id', 'person_address', ['person_id'])

    # ── person_religion ──
    op.create_table(
        'person_religion',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('religion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('religion_category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('religion_sub_category_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['person_id'], ['person.id']),
        sa.ForeignKeyConstraint(['religion_id'], ['religion.id']),
        sa.ForeignKeyConstraint(['religion_category_id'], ['religion_category.id']),
        sa.ForeignKeyConstraint(['religion_sub_category_id'], ['religion_sub_category.id']),
    )
    op.create_index('ix_person_religion_person_id', 'person_religion', ['person_id'], unique=True)

    # ── person_relationship ──
    op.create_table(
        'person_relationship',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('related_person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('relationship_type', sa.String(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['person_id'], ['person.id']),
        sa.ForeignKeyConstraint(['related_person_id'], ['person.id']),
    )
    op.create_index('ix_person_relationship_person_id', 'person_relationship', ['person_id'])

    # ── person_profession (lookup table) ──
    op.create_table(
        'person_profession',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('weight', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.create_index('ix_person_profession_name', 'person_profession', ['name'], unique=True)

    # ── person_profession_association ──
    op.create_table(
        'person_profession_association',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('profession_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['person_id'], ['person.id']),
        sa.ForeignKeyConstraint(['profession_id'], ['person_profession.id']),
    )
    op.create_index('ix_person_profession_assoc_person_id', 'person_profession_association', ['person_id'])

    # ── person_life_event ──
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
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['person_id'], ['person.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['country_id'], ['address_country.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['state_id'], ['address_state.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['district_id'], ['address_district.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sub_district_id'], ['address_sub_district.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['locality_id'], ['address_locality.id'], ondelete='SET NULL'),
        sa.CheckConstraint(
            "event_type IN ('birth', 'marriage', 'death', 'purchase', 'sale', 'achievement', 'education', 'career', 'health', 'travel', 'other')",
            name='check_event_type',
        ),
        sa.CheckConstraint('event_month >= 1 AND event_month <= 12', name='check_event_month'),
        sa.CheckConstraint('event_date >= 1 AND event_date <= 31', name='check_event_date'),
    )
    op.create_index('idx_person_life_event_person_id', 'person_life_event', ['person_id'])
    op.create_index('idx_person_life_event_year', 'person_life_event', ['event_year'], postgresql_ops={'event_year': 'DESC'})

    # ── person_attachment_request ──
    # Note: requester_user_id and requester_person_id are nullable because they
    # get cleared when the temporary person/user is deleted on approve/deny.
    op.create_table(
        'person_attachment_request',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('requester_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('requester_person_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('target_person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approver_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['requester_user_id'], ['user.id'], name='fk_attachment_request_requester_user'),
        sa.ForeignKeyConstraint(['requester_person_id'], ['person.id'], name='fk_attachment_request_requester_person'),
        sa.ForeignKeyConstraint(['target_person_id'], ['person.id'], name='fk_attachment_request_target_person'),
        sa.ForeignKeyConstraint(['approver_user_id'], ['user.id'], name='fk_attachment_request_approver_user'),
        sa.ForeignKeyConstraint(['resolved_by_user_id'], ['user.id'], name='fk_attachment_request_resolved_by_user'),
        sa.CheckConstraint("status IN ('pending', 'approved', 'denied', 'cancelled')", name='check_attachment_request_status'),
    )
    op.create_index('idx_attachment_request_requester_user', 'person_attachment_request', ['requester_user_id'])
    op.create_index('idx_attachment_request_requester_person', 'person_attachment_request', ['requester_person_id'])
    op.create_index('idx_attachment_request_target_person', 'person_attachment_request', ['target_person_id'])
    op.create_index('idx_attachment_request_approver_user', 'person_attachment_request', ['approver_user_id'])
    op.create_index('idx_attachment_request_status', 'person_attachment_request', ['status'])

    # ── support_ticket ──
    op.create_table(
        'support_ticket',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('issue_type', sa.String(20), nullable=False),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='open'),
        sa.Column('resolved_by_user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['resolved_by_user_id'], ['user.id'], ondelete='SET NULL'),
        sa.CheckConstraint("issue_type IN ('bug', 'feature_request')", name='check_issue_type'),
        sa.CheckConstraint("status IN ('open', 'closed')", name='check_status'),
        sa.CheckConstraint("char_length(description) <= 2000", name='check_description_length'),
    )
    op.create_index('idx_support_ticket_user_id', 'support_ticket', ['user_id'])
    op.create_index('idx_support_ticket_status', 'support_ticket', ['status'])
    op.create_index('idx_support_ticket_created_at', 'support_ticket', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    op.create_index('idx_support_ticket_type', 'support_ticket', ['issue_type'])

    # ── profile_view_tracking ──
    op.create_table(
        'profile_view_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('viewed_person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('viewer_person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('is_aggregated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['viewed_person_id'], ['person.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['viewer_person_id'], ['person.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_profile_view_tracking_viewed_person', 'profile_view_tracking', ['viewed_person_id'])
    op.create_index('idx_profile_view_tracking_viewer_person', 'profile_view_tracking', ['viewer_person_id'])
    op.create_index('idx_profile_view_tracking_composite', 'profile_view_tracking', ['viewed_person_id', 'viewer_person_id', 'is_aggregated'])


def downgrade() -> None:
    op.drop_table('profile_view_tracking')
    op.drop_table('support_ticket')
    op.drop_table('person_attachment_request')
    op.drop_table('person_life_event')
    op.drop_table('person_profession_association')
    op.drop_table('person_profession')
    op.drop_table('person_relationship')
    op.drop_table('person_religion')
    op.drop_table('person_address')
    op.drop_table('person_metadata')
    op.drop_table('person')
    op.drop_table('person_gender')
    op.drop_table('religion_sub_category')
    op.drop_table('religion_category')
    op.drop_table('religion')
    op.drop_table('address_locality')
    op.drop_table('address_sub_district')
    op.drop_table('address_district')
    op.drop_table('address_state')
    op.drop_table('address_country')
    op.drop_table('post')
    op.drop_table('item')
    op.drop_table('user')

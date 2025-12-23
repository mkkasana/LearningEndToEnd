"""Rename address tables with proper prefixes

Revision ID: e5f6g7h8i9j0
Revises: d4e5f6g7h8i9
Create Date: 2024-12-23 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5f6g7h8i9j0'
down_revision = 'd4e5f6g7h8i9'
branch_labels = None
depends_on = None


def upgrade():
    # Rename tables with proper address_ prefix
    op.rename_table('country', 'address_country')
    op.rename_table('state', 'address_state')
    op.rename_table('district', 'address_district')
    op.rename_table('subdistrict', 'address_sub_district')
    op.rename_table('locality', 'address_locality')
    
    # Update foreign key constraints to reference new table names
    # Note: PostgreSQL automatically updates foreign key references when tables are renamed
    # But we need to update the constraint names for consistency
    
    # Rename indexes to match new table names
    op.execute('ALTER INDEX IF EXISTS ix_country_name RENAME TO ix_address_country_name')
    op.execute('ALTER INDEX IF EXISTS ix_country_code RENAME TO ix_address_country_code')
    
    op.execute('ALTER INDEX IF EXISTS ix_state_name RENAME TO ix_address_state_name')
    op.execute('ALTER INDEX IF EXISTS ix_state_country_id RENAME TO ix_address_state_country_id')
    
    op.execute('ALTER INDEX IF EXISTS ix_district_name RENAME TO ix_address_district_name')
    op.execute('ALTER INDEX IF EXISTS ix_district_state_id RENAME TO ix_address_district_state_id')
    
    op.execute('ALTER INDEX IF EXISTS ix_subdistrict_name RENAME TO ix_address_sub_district_name')
    op.execute('ALTER INDEX IF EXISTS ix_subdistrict_district_id RENAME TO ix_address_sub_district_district_id')
    
    op.execute('ALTER INDEX IF EXISTS ix_locality_name RENAME TO ix_address_locality_name')
    op.execute('ALTER INDEX IF EXISTS ix_locality_sub_district_id RENAME TO ix_address_locality_sub_district_id')


def downgrade():
    # Rename indexes back
    op.execute('ALTER INDEX IF EXISTS ix_address_locality_sub_district_id RENAME TO ix_locality_sub_district_id')
    op.execute('ALTER INDEX IF EXISTS ix_address_locality_name RENAME TO ix_locality_name')
    
    op.execute('ALTER INDEX IF EXISTS ix_address_sub_district_district_id RENAME TO ix_subdistrict_district_id')
    op.execute('ALTER INDEX IF EXISTS ix_address_sub_district_name RENAME TO ix_subdistrict_name')
    
    op.execute('ALTER INDEX IF EXISTS ix_address_district_state_id RENAME TO ix_district_state_id')
    op.execute('ALTER INDEX IF EXISTS ix_address_district_name RENAME TO ix_district_name')
    
    op.execute('ALTER INDEX IF EXISTS ix_address_state_country_id RENAME TO ix_state_country_id')
    op.execute('ALTER INDEX IF EXISTS ix_address_state_name RENAME TO ix_state_name')
    
    op.execute('ALTER INDEX IF EXISTS ix_address_country_code RENAME TO ix_country_code')
    op.execute('ALTER INDEX IF EXISTS ix_address_country_name RENAME TO ix_country_name')
    
    # Rename tables back to original names
    op.rename_table('address_locality', 'locality')
    op.rename_table('address_sub_district', 'subdistrict')
    op.rename_table('address_district', 'district')
    op.rename_table('address_state', 'state')
    op.rename_table('address_country', 'country')

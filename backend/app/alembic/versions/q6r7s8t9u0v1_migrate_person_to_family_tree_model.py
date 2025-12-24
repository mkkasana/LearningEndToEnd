"""Migrate person to family tree model

Revision ID: q6r7s8t9u0v1
Revises: p5q6r7s8t9u0
Create Date: 2025-12-24

Changes:
- Add id as new primary key to person table
- Make user_id nullable
- Add created_by_user_id field
- Add is_primary field
- Update foreign keys in related tables to reference person.id instead of person.user_id
"""

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'q6r7s8t9u0v1'
down_revision = 'p5q6r7s8t9u0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Add new id column to person table (nullable initially)
    op.add_column('person', sa.Column('id', sa.UUID(), nullable=True))
    
    # Step 2: Generate UUIDs for existing person records
    op.execute("""
        UPDATE person 
        SET id = gen_random_uuid()
    """)
    
    # Step 3: Make id non-nullable
    op.alter_column('person', 'id', nullable=False)
    
    # Step 4: Add created_by_user_id column (nullable initially)
    op.add_column('person', sa.Column('created_by_user_id', sa.UUID(), nullable=True))
    
    # Step 5: Set created_by_user_id to user_id for existing records (they created themselves)
    op.execute("""
        UPDATE person 
        SET created_by_user_id = user_id
    """)
    
    # Step 6: Make created_by_user_id non-nullable
    op.alter_column('person', 'created_by_user_id', nullable=False)
    
    # Step 7: Add is_primary column (default True for existing records)
    op.add_column('person', sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='true'))
    
    # Step 8: Add temporary columns to related tables to store person.id
    # Handle all tables that reference person.user_id
    op.add_column('person_address', sa.Column('new_person_id', sa.UUID(), nullable=True))
    op.add_column('person_religion', sa.Column('new_person_id', sa.UUID(), nullable=True))
    op.add_column('person_relationship', sa.Column('new_person_id', sa.UUID(), nullable=True))
    op.add_column('person_relationship', sa.Column('new_related_person_id', sa.UUID(), nullable=True))
    op.add_column('person_profession_association', sa.Column('new_person_id', sa.UUID(), nullable=True))
    op.add_column('person_metadata', sa.Column('new_person_id', sa.UUID(), nullable=True))
    
    # Step 9: Populate new_person_id columns with person.id based on user_id
    op.execute("""
        UPDATE person_address pa
        SET new_person_id = p.id
        FROM person p
        WHERE pa.person_id = p.user_id
    """)
    
    op.execute("""
        UPDATE person_religion pr
        SET new_person_id = p.id
        FROM person p
        WHERE pr.person_id = p.user_id
    """)
    
    op.execute("""
        UPDATE person_relationship pr
        SET new_person_id = p.id
        FROM person p
        WHERE pr.person_id = p.user_id
    """)
    
    op.execute("""
        UPDATE person_relationship pr
        SET new_related_person_id = p.id
        FROM person p
        WHERE pr.related_person_id = p.user_id
    """)
    
    op.execute("""
        UPDATE person_profession_association ppa
        SET new_person_id = p.id
        FROM person p
        WHERE ppa.person_id = p.user_id
    """)
    
    op.execute("""
        UPDATE person_metadata pm
        SET new_person_id = p.id
        FROM person p
        WHERE pm.person_id = p.user_id
    """)
    
    # Step 10: Drop old foreign key constraints
    op.drop_constraint('person_address_person_id_fkey', 'person_address', type_='foreignkey')
    op.drop_constraint('person_religion_person_id_fkey', 'person_religion', type_='foreignkey')
    op.drop_constraint('person_relationship_person_id_fkey', 'person_relationship', type_='foreignkey')
    op.drop_constraint('person_relationship_related_person_id_fkey', 'person_relationship', type_='foreignkey')
    op.drop_constraint('person_profession_association_person_id_fkey', 'person_profession_association', type_='foreignkey')
    op.drop_constraint('person_metadata_person_id_fkey', 'person_metadata', type_='foreignkey')
    
    # Step 11: Drop old person_id columns
    op.drop_column('person_address', 'person_id')
    op.drop_column('person_religion', 'person_id')
    op.drop_column('person_relationship', 'person_id')
    op.drop_column('person_relationship', 'related_person_id')
    op.drop_column('person_profession_association', 'person_id')
    op.drop_column('person_metadata', 'person_id')
    
    # Step 12: Rename new_person_id columns to person_id
    op.alter_column('person_address', 'new_person_id', new_column_name='person_id')
    op.alter_column('person_religion', 'new_person_id', new_column_name='person_id')
    op.alter_column('person_relationship', 'new_person_id', new_column_name='person_id')
    op.alter_column('person_relationship', 'new_related_person_id', new_column_name='related_person_id')
    op.alter_column('person_profession_association', 'new_person_id', new_column_name='person_id')
    op.alter_column('person_metadata', 'new_person_id', new_column_name='person_id')
    
    # Step 13: Make person_id columns non-nullable
    op.alter_column('person_address', 'person_id', nullable=False)
    op.alter_column('person_religion', 'person_id', nullable=False)
    op.alter_column('person_relationship', 'person_id', nullable=False)
    op.alter_column('person_relationship', 'related_person_id', nullable=False)
    op.alter_column('person_profession_association', 'person_id', nullable=False)
    op.alter_column('person_metadata', 'person_id', nullable=False)
    
    # Step 14: Drop primary key constraint on person.user_id
    op.drop_constraint('person_pkey', 'person', type_='primary')
    
    # Step 15: Add primary key constraint on person.id
    op.create_primary_key('person_pkey', 'person', ['id'])
    
    # Step 16: Make user_id nullable in person table
    op.alter_column('person', 'user_id', nullable=True)
    
    # Step 17: Add indexes
    op.create_index('ix_person_user_id', 'person', ['user_id'])
    op.create_index('ix_person_created_by_user_id', 'person', ['created_by_user_id'])
    op.create_index('ix_person_is_primary', 'person', ['is_primary'])
    
    # Step 18: Add foreign key for created_by_user_id
    op.create_foreign_key(
        'fk_person_created_by_user_id',
        'person', 'user',
        ['created_by_user_id'], ['id']
    )
    
    # Step 19: Recreate foreign keys for related tables
    op.create_foreign_key(
        'person_address_person_id_fkey',
        'person_address', 'person',
        ['person_id'], ['id']
    )
    
    op.create_foreign_key(
        'person_religion_person_id_fkey',
        'person_religion', 'person',
        ['person_id'], ['id']
    )
    
    op.create_foreign_key(
        'person_relationship_person_id_fkey',
        'person_relationship', 'person',
        ['person_id'], ['id']
    )
    
    op.create_foreign_key(
        'person_relationship_related_person_id_fkey',
        'person_relationship', 'person',
        ['related_person_id'], ['id']
    )
    
    op.create_foreign_key(
        'person_profession_association_person_id_fkey',
        'person_profession_association', 'person',
        ['person_id'], ['id']
    )
    
    op.create_foreign_key(
        'person_metadata_person_id_fkey',
        'person_metadata', 'person',
        ['person_id'], ['id']
    )


def downgrade() -> None:
    # This is a complex migration - downgrade not recommended
    # If needed, restore from backup
    pass

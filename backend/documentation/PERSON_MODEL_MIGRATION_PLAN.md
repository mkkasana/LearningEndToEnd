# Person Model Migration Plan: 1:1 to 1:Many

## Current State vs Desired State

### Current (1:1 Relationship)
```
User (1) ←→ (1) Person
- Each User has exactly ONE Person
- user_id is PRIMARY KEY in Person table
- Cannot add multiple persons per user
```

### Desired (1:Many Relationship)
```
User (1) ←→ (Many) Person
- Each User can have MULTIPLE Persons
- User can add family members (parents, children, spouse, etc.)
- Person can exist without a User account
- One Person can be the "primary" person for the User
```

## New Schema Design

### Person Table (Proposed)
```python
class Person(SQLModel, table=True):
    """Person model - Can be linked to a user or standalone."""
    
    __tablename__ = "person"
    
    # NEW: Separate ID as primary key
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4, 
        primary_key=True,
        description="Unique person identifier"
    )
    
    # CHANGED: user_id is now nullable and not primary key
    user_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="user.id", 
        index=True,  # Index for fast lookups
        description="User account reference (nullable for non-users)"
    )
    
    # NEW: Track who created this person
    created_by_user_id: uuid.UUID = Field(
        foreign_key="user.id",
        description="User who created this person record"
    )
    
    # NEW: Is this the primary person for the user?
    is_primary: bool = Field(
        default=False,
        description="Is this the primary person for the user account"
    )
    
    # Existing fields
    first_name: str = Field(max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str = Field(max_length=100)
    gender_id: uuid.UUID = Field(foreign_key="person_gender.id")
    date_of_birth: date
    date_of_death: date | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Key Changes

### 1. **New Primary Key**
- `id` (UUID) becomes the primary key
- Allows multiple persons per user
- Each person has unique identifier

### 2. **Nullable user_id**
- `user_id` is now optional (nullable)
- Persons without user accounts (family members) have `user_id = NULL`
- Still indexed for fast lookups

### 3. **created_by_user_id**
- Tracks which user created this person record
- Important for permissions and ownership
- Non-nullable (every person must be created by someone)

### 4. **is_primary Flag**
- Marks which person is the "primary" person for a user
- Used for profile display, default selection
- Only one person per user should have `is_primary = True`

## Use Cases

### Use Case 1: User Signup (Primary Person)
```python
# Create user
user = User(email="john@example.com", ...)
session.add(user)
session.flush()

# Create primary person for user
primary_person = Person(
    user_id=user.id,           # Linked to user account
    created_by_user_id=user.id, # Created by self
    is_primary=True,            # This is the user's own profile
    first_name="John",
    last_name="Doe",
    ...
)
session.add(primary_person)
session.commit()
```

### Use Case 2: User Adds Family Member (No User Account)
```python
# User adds their father
father = Person(
    user_id=None,               # No user account
    created_by_user_id=current_user.id,  # Created by current user
    is_primary=False,           # Not a primary person
    first_name="Robert",
    last_name="Doe",
    ...
)
session.add(father)

# Create relationship
relationship = PersonRelationship(
    person_id=primary_person.id,
    related_person_id=father.id,
    relationship_type="father"
)
session.add(relationship)
session.commit()
```

### Use Case 3: User Adds Spouse (Who Also Has Account)
```python
# Spouse already has their own account and person
spouse_user = session.get(User, spouse_user_id)
spouse_person = session.exec(
    select(Person).where(
        Person.user_id == spouse_user_id,
        Person.is_primary == True
    )
).first()

# Create relationship between the two persons
relationship = PersonRelationship(
    person_id=current_user_person.id,
    related_person_id=spouse_person.id,
    relationship_type="spouse"
)
session.add(relationship)
session.commit()
```

## Migration Steps

### Step 1: Create Migration Script
```python
"""Add id as primary key to person table and make user_id nullable

Revision ID: abc123def456
"""

def upgrade() -> None:
    # 1. Add new id column (not primary yet)
    op.add_column('person', 
        sa.Column('id', sa.UUID(), nullable=True)
    )
    
    # 2. Generate UUIDs for existing records
    op.execute("""
        UPDATE person 
        SET id = gen_random_uuid()
    """)
    
    # 3. Make id non-nullable
    op.alter_column('person', 'id', nullable=False)
    
    # 4. Add created_by_user_id column
    op.add_column('person',
        sa.Column('created_by_user_id', sa.UUID(), nullable=True)
    )
    
    # 5. Set created_by_user_id to user_id for existing records
    op.execute("""
        UPDATE person 
        SET created_by_user_id = user_id
    """)
    
    # 6. Make created_by_user_id non-nullable
    op.alter_column('person', 'created_by_user_id', nullable=False)
    
    # 7. Add is_primary column (default True for existing records)
    op.add_column('person',
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='true')
    )
    
    # 8. Drop primary key constraint on user_id
    op.drop_constraint('person_pkey', 'person', type_='primary')
    
    # 9. Add primary key constraint on id
    op.create_primary_key('person_pkey', 'person', ['id'])
    
    # 10. Make user_id nullable
    op.alter_column('person', 'user_id', nullable=True)
    
    # 11. Add index on user_id for fast lookups
    op.create_index('ix_person_user_id', 'person', ['user_id'])
    
    # 12. Add foreign key for created_by_user_id
    op.create_foreign_key(
        'fk_person_created_by_user_id',
        'person', 'user',
        ['created_by_user_id'], ['id']
    )

def downgrade() -> None:
    # Reverse the changes (if needed)
    pass
```

### Step 2: Update Related Tables
All tables that reference `person.user_id` need to be updated to reference `person.id`:

#### Tables to Update:
1. **person_address**
   - Change: `person_id` references `person.id` (not `person.user_id`)
   
2. **person_religion**
   - Change: `person_id` references `person.id` (not `person.user_id`)
   
3. **person_profession**
   - Change: `person_id` references `person.id` (not `person.user_id`)
   
4. **person_relationship**
   - Change: `person_id` references `person.id`
   - Change: `related_person_id` references `person.id`

### Step 3: Update API Endpoints

#### Current Endpoints (Need Updates)
```python
# OLD: Get current user's person
@router.get("/person/me")
def get_my_person(current_user: CurrentUser):
    person = session.get(Person, current_user.id)  # ❌ Won't work
    return person

# NEW: Get current user's primary person
@router.get("/person/me")
def get_my_person(current_user: CurrentUser):
    person = session.exec(
        select(Person).where(
            Person.user_id == current_user.id,
            Person.is_primary == True
        )
    ).first()
    return person
```

#### New Endpoints (To Add)
```python
# Get all persons created by current user
@router.get("/persons")
def get_my_persons(current_user: CurrentUser):
    persons = session.exec(
        select(Person).where(
            Person.created_by_user_id == current_user.id
        )
    ).all()
    return persons

# Create a new person (family member)
@router.post("/persons")
def create_person(
    current_user: CurrentUser,
    person_in: PersonCreate
):
    person = Person(
        **person_in.model_dump(),
        created_by_user_id=current_user.id,
        user_id=None,  # No user account
        is_primary=False
    )
    session.add(person)
    session.commit()
    return person

# Get specific person by ID
@router.get("/persons/{person_id}")
def get_person(
    current_user: CurrentUser,
    person_id: UUID
):
    person = session.get(Person, person_id)
    
    # Check permission: user can only view persons they created
    if person.created_by_user_id != current_user.id:
        raise HTTPException(403, "Not authorized")
    
    return person
```

### Step 4: Update Services and Repositories

```python
class PersonRepository:
    def get_primary_person(self, user_id: UUID) -> Person | None:
        """Get the primary person for a user."""
        return self.session.exec(
            select(Person).where(
                Person.user_id == user_id,
                Person.is_primary == True
            )
        ).first()
    
    def get_persons_by_creator(self, user_id: UUID) -> list[Person]:
        """Get all persons created by a user."""
        return self.session.exec(
            select(Person).where(
                Person.created_by_user_id == user_id
            )
        ).all()
    
    def get_family_members(self, user_id: UUID) -> list[Person]:
        """Get all family members (persons without user accounts)."""
        return self.session.exec(
            select(Person).where(
                Person.created_by_user_id == user_id,
                Person.user_id.is_(None)
            )
        ).all()
```

## Updated Architecture Diagram

```
┌─────────────────────────────────┐
│           USER                  │
│  (Authentication & Account)     │
├─────────────────────────────────┤
│ id (UUID) - PK                  │
│ email                           │
│ hashed_password                 │
└─────────────────────────────────┘
           │
           │ 1:Many relationship
           │
           ▼
┌─────────────────────────────────┐
│          PERSON                 │
│  (Demographics & Personal Info) │
├─────────────────────────────────┤
│ id (UUID) - PK          ← NEW   │
│ user_id (UUID) - FK, nullable   │
│ created_by_user_id - FK ← NEW   │
│ is_primary (bool)       ← NEW   │
│ first_name                      │
│ middle_name                     │
│ last_name                       │
│ gender_id (FK)                  │
│ date_of_birth                   │
│ date_of_death                   │
└─────────────────────────────────┘
           │
           │ Has many relationships
           │
    ┌──────┴──────┬──────────┬──────────┐
    ▼             ▼          ▼          ▼
┌─────────┐  ┌─────────┐ ┌──────┐  ┌──────────┐
│ Address │  │Religion │ │Profes│  │Relation- │
│         │  │         │ │sion  │  │ships     │
└─────────┘  └─────────┘ └──────┘  └──────────┘
```

## Benefits of New Design

### 1. **Family Tree Support**
- Users can add parents, grandparents, children
- Build complete family trees
- Track genealogy

### 2. **Flexible Relationships**
- Person-to-Person relationships (not User-to-User)
- Can link persons who don't have accounts
- Support complex family structures

### 3. **Privacy & Permissions**
- `created_by_user_id` tracks ownership
- Users can only view/edit persons they created
- Can share access in future (family collaboration)

### 4. **Backward Compatible**
- Existing users keep their primary person
- `is_primary` flag maintains current behavior
- Migration preserves all existing data

## Frontend Changes

### New UI Components Needed

1. **Family Members List**
   - Show all persons created by user
   - Distinguish between primary person and family members
   - Add/Edit/Delete family members

2. **Person Selector**
   - Dropdown to switch between persons
   - Show primary person by default
   - Filter by relationship type

3. **Add Family Member Form**
   - Similar to signup form
   - Option to link existing user (if they have account)
   - Relationship type selector

## Example User Flow

### Scenario: User Adds Their Father

1. **User navigates to "Family Members"**
   - Sees their primary person (themselves)
   - Clicks "Add Family Member"

2. **Fills out form**
   - First Name: Robert
   - Last Name: Doe
   - Gender: Male
   - Date of Birth: 1960-01-15
   - Relationship: Father

3. **System creates**
   - New Person record (user_id = NULL)
   - PersonRelationship linking user's primary person to father
   - Father's address, religion, etc. (optional)

4. **User can now**
   - View father's profile
   - Add father's address
   - Add father's profession history
   - Link father to other family members (grandparents)

## Rollout Strategy

### Phase 1: Database Migration (Backend)
- Run migration script
- Update models
- Test with existing data

### Phase 2: API Updates (Backend)
- Update existing endpoints
- Add new endpoints
- Update tests

### Phase 3: Frontend Updates
- Update profile completion to use primary person
- Add family members UI
- Update person selector

### Phase 4: Testing
- Test existing user flows
- Test new family member flows
- Test permissions

### Phase 5: Deployment
- Deploy to staging
- Verify migration
- Deploy to production

## Risks & Mitigation

### Risk 1: Data Loss During Migration
**Mitigation**: 
- Backup database before migration
- Test migration on staging first
- Keep downgrade script ready

### Risk 2: Breaking Existing Code
**Mitigation**:
- Comprehensive test coverage
- Gradual rollout
- Feature flags for new functionality

### Risk 3: Performance Impact
**Mitigation**:
- Add indexes on new columns
- Optimize queries
- Monitor query performance

## Next Steps

1. ✅ Review and approve this migration plan
2. ⬜ Create database migration script
3. ⬜ Update Person model
4. ⬜ Update related models (address, religion, etc.)
5. ⬜ Update API endpoints
6. ⬜ Update frontend components
7. ⬜ Write tests
8. ⬜ Deploy to staging
9. ⬜ Test thoroughly
10. ⬜ Deploy to production

Would you like me to proceed with implementing this migration?

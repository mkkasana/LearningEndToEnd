# User and Person Relationship

## Overview
The system uses a **separation of concerns** pattern where `User` handles authentication/authorization and `Person` handles demographic/personal information.

## Database Relationship

```
┌─────────────────────────────────┐
│           USER                  │
│  (Authentication & Account)     │
├─────────────────────────────────┤
│ id (UUID) - PK                  │
│ email                           │
│ hashed_password                 │
│ is_active                       │
│ is_superuser                    │
│ full_name                       │
└─────────────────────────────────┘
           │
           │ 1:1 relationship
           │
           ▼
┌─────────────────────────────────┐
│          PERSON                 │
│  (Demographics & Personal Info) │
├─────────────────────────────────┤
│ user_id (UUID) - PK, FK         │
│ first_name                      │
│ middle_name                     │
│ last_name                       │
│ gender_id (FK)                  │
│ date_of_birth                   │
│ date_of_death                   │
│ created_at                      │
│ updated_at                      │
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

## Key Design Principles

### 1. **One-to-One Relationship**
- Each `User` has exactly **one** `Person` record
- The `Person.user_id` is both the **Primary Key** and **Foreign Key**
- This ensures a strict 1:1 mapping

```python
# Person model
user_id: uuid.UUID = Field(
    foreign_key="user.id", 
    primary_key=True,  # ← This makes it 1:1
    description="User account reference"
)
```

### 2. **Separation of Concerns**

#### User Table (Authentication Domain)
**Purpose**: Handle authentication, authorization, and account management

**Fields**:
- `id` - Unique identifier for the user account
- `email` - Login credential
- `hashed_password` - Secure password storage
- `is_active` - Account status
- `is_superuser` - Admin privileges
- `full_name` - Display name (computed from Person)

**Responsibilities**:
- Login/logout
- Password management
- Session management
- Permission checks
- Account activation/deactivation

#### Person Table (Demographics Domain)
**Purpose**: Store personal and demographic information

**Fields**:
- `user_id` - Links to User account
- `first_name`, `middle_name`, `last_name` - Name components
- `gender_id` - Gender reference
- `date_of_birth` - Birth date
- `date_of_death` - Death date (for genealogy)
- Timestamps

**Responsibilities**:
- Personal information
- Demographic data
- Genealogical records
- Relationships with other persons

## Why This Design?

### 1. **Flexibility**
- A person can exist in the system without a user account (e.g., family members in genealogy)
- Future: Multiple users could potentially view/manage the same person record (family tree scenarios)

### 2. **Security**
- Authentication data (passwords, tokens) is isolated from personal data
- Easier to implement data privacy controls
- Can delete user account while preserving person data for historical records

### 3. **Domain Separation**
- Authentication logic doesn't mix with demographic logic
- Different teams can work on different domains
- Easier to test and maintain

### 4. **Scalability**
- Person data can be extended without affecting authentication
- Can add complex person relationships without touching user table
- Supports future features like family trees, genealogy

## Data Flow

### During Signup
```
1. User fills signup form
   ↓
2. Create User record
   - email: user@example.com
   - password: hashed
   - id: uuid-1234
   ↓
3. Create Person record
   - user_id: uuid-1234 (same as User.id)
   - first_name: John
   - middle_name: Michael
   - last_name: Doe
   - gender_id: male-uuid
   - date_of_birth: 1990-01-01
   ↓
4. Update User.full_name
   - full_name: "John Michael Doe"
```

### During Login
```
1. User enters email + password
   ↓
2. Authenticate against User table
   ↓
3. If valid, create session with User.id
   ↓
4. Frontend can fetch Person data using User.id
```

### Accessing Profile
```
1. GET /api/v1/users/me
   → Returns User data (email, full_name, etc.)
   
2. GET /api/v1/person/me
   → Returns Person data (first_name, last_name, dob, gender, etc.)
   
3. GET /api/v1/person/me/addresses
   → Returns Person's addresses
   
4. GET /api/v1/person-religion/me
   → Returns Person's religion
```

## Related Tables

### Person has relationships with:

1. **person_address** (1:Many)
   - A person can have multiple addresses (home, work, historical)
   - Links: `person_address.person_id → person.user_id`

2. **person_religion** (1:1)
   - A person has one religion record
   - Links: `person_religion.person_id → person.user_id`

3. **person_profession** (1:Many)
   - A person can have multiple professions over time
   - Links: `person_profession.person_id → person.user_id`

4. **person_relationship** (Many:Many)
   - A person can have relationships with other persons
   - Links: `person_relationship.person_id → person.user_id`
   - Links: `person_relationship.related_person_id → person.user_id`

## Example Queries

### Get complete user profile
```python
# Get user account info
user = session.get(User, user_id)

# Get person demographic info
person = session.get(Person, user_id)  # user_id is PK

# Get addresses
addresses = session.exec(
    select(PersonAddress).where(PersonAddress.person_id == user_id)
).all()

# Get religion
religion = session.exec(
    select(PersonReligion).where(PersonReligion.person_id == user_id)
).first()
```

### Check if user has completed profile
```python
def is_profile_complete(user_id: UUID) -> bool:
    # Check person exists
    person = session.get(Person, user_id)
    if not person:
        return False
    
    # Check address exists
    address = session.exec(
        select(PersonAddress).where(PersonAddress.person_id == user_id)
    ).first()
    if not address:
        return False
    
    # Check religion exists
    religion = session.exec(
        select(PersonReligion).where(PersonReligion.person_id == user_id)
    ).first()
    if not religion:
        return False
    
    return True
```

## Benefits of This Architecture

### 1. **Clean Separation**
- Authentication concerns don't pollute demographic data
- Can change authentication method without affecting person data

### 2. **Extensibility**
- Easy to add new person-related tables (education, employment, etc.)
- Can support complex genealogy features

### 3. **Data Privacy**
- Can implement different access controls for User vs Person data
- Easier GDPR compliance (separate PII from auth data)

### 4. **Performance**
- User table stays small and fast for authentication
- Person queries don't need to join with authentication data

### 5. **Future-Proof**
- Can support scenarios like:
  - Deceased persons (no user account)
  - Historical records
  - Family tree management
  - Multiple users managing same person record

## Common Patterns

### Pattern 1: Get Current User's Person Data
```python
@router.get("/person/me")
def get_my_person(current_user: CurrentUser):
    person = session.get(Person, current_user.id)
    return person
```

### Pattern 2: Create Person During Signup
```python
def create_user_with_person(user_data: UserRegister):
    # Create user
    user = User(email=user_data.email, ...)
    session.add(user)
    session.flush()  # Get user.id
    
    # Create person
    person = Person(
        user_id=user.id,  # Link to user
        first_name=user_data.first_name,
        ...
    )
    session.add(person)
    session.commit()
    
    return user
```

### Pattern 3: Update Full Name
```python
def update_person_name(person: Person):
    # Update person names
    person.first_name = "New Name"
    
    # Update user's full_name for display
    user = session.get(User, person.user_id)
    user.full_name = f"{person.first_name} {person.middle_name} {person.last_name}"
    
    session.commit()
```

## Summary

| Aspect | User | Person |
|--------|------|--------|
| **Purpose** | Authentication & Authorization | Demographics & Personal Info |
| **Primary Key** | `id` (UUID) | `user_id` (UUID, FK to User) |
| **Relationship** | 1:1 with Person | 1:1 with User |
| **Domain** | Security/Auth | Personal/Demographic |
| **Contains** | Email, password, permissions | Name, DOB, gender |
| **Related To** | Items, Posts | Addresses, Religion, Professions, Relationships |
| **Can Exist Without** | Person (temporarily) | User (for genealogy) |
| **Updated When** | Login, password change | Profile updates |

This design provides a robust, scalable foundation for managing both authentication and personal information while keeping concerns properly separated.

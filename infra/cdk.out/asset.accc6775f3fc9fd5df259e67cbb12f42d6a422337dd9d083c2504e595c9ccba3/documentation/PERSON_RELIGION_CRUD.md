# Person Religion CRUD Operations

## Overview
Complete CRUD implementation for managing person-religion associations in the onboarding flow.

## Components Implemented

### 1. Database Model
- **File**: `backend/app/db_models/person/person_religion.py`
- **Table**: `person_religion`
- **Fields**:
  - `id`: UUID primary key
  - `person_id`: Foreign key to person (unique - one religion per person)
  - `religion_id`: Foreign key to religion (required)
  - `religion_category_id`: Foreign key to religion category (optional)
  - `religion_sub_category_id`: Foreign key to religion sub-category (optional)
  - `created_at`, `updated_at`: Timestamps

### 2. Schemas
- **File**: `backend/app/schemas/person/person_religion.py`
- **Schemas**:
  - `PersonReligionBase`: Base properties
  - `PersonReligionCreate`: For creating new religion
  - `PersonReligionUpdate`: For updating (all fields optional)
  - `PersonReligionPublic`: Response schema

### 3. Repository
- **File**: `backend/app/repositories/person/person_religion_repository.py`
- **Methods**:
  - `get_by_person_id()`: Get religion for a person
  - `person_has_religion()`: Check if person has religion
  - Inherits CRUD operations from `BaseRepository`

### 4. Service
- **File**: `backend/app/services/person/person_religion_service.py`
- **Methods**:
  - `get_by_person_id()`: Get religion for a person
  - `create_person_religion()`: Create new religion
  - `update_person_religion()`: Update existing religion
  - `delete_person_religion()`: Delete religion

### 5. API Routes
- **File**: `backend/app/api/routes/person_religion.py`
- **Endpoints**:
  - `POST /api/v1/person-religion/` - Create religion for current user
  - `GET /api/v1/person-religion/me` - Get current user's religion
  - `PUT /api/v1/person-religion/me` - Update current user's religion
  - `DELETE /api/v1/person-religion/me` - Delete current user's religion

### 6. Profile Integration
- **File**: `backend/app/services/profile_service.py`
- Profile completion status now checks for religion
- Returns `has_religion` boolean and includes "religion" in `missing_fields` if not present

## API Usage Examples

### Create Religion
```bash
POST /api/v1/person-religion/
Authorization: Bearer <token>
Content-Type: application/json

{
  "religion_id": "uuid-here",
  "religion_category_id": "uuid-here",  // optional
  "religion_sub_category_id": "uuid-here"  // optional
}
```

### Get My Religion
```bash
GET /api/v1/person-religion/me
Authorization: Bearer <token>
```

### Update Religion
```bash
PUT /api/v1/person-religion/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "religion_category_id": "new-uuid-here"
}
```

### Delete Religion
```bash
DELETE /api/v1/person-religion/me
Authorization: Bearer <token>
```

## Testing

### Integration Test
- **File**: `backend/tests/integration_scripts/test_person_religion_crud.py`
- **Tests**:
  1. Create person religion
  2. Prevent duplicate creation
  3. Get current user's religion
  4. Update religion
  5. Profile completion includes religion
  6. Delete religion
  7. Get after deletion (404)
  8. Profile completion after deletion

### Run Tests
```bash
python backend/tests/integration_scripts/test_person_religion_crud.py
```

## Seed Data

### Religion Metadata
Religions are seeded with categories and sub-categories:
- Hinduism (Vaishnavism → ISKCON)
- Islam (Sunni)
- Christianity (Catholic)
- Sikhism
- Buddhism
- Jainism
- Other

### Seed Command
```bash
docker compose exec backend python -c "import sys; sys.path.insert(0, '/app'); ..."
```

## Onboarding Flow Integration

The religion information is now part of the profile completion check:
1. User signs up
2. Profile completion status checks for:
   - Person record ✓
   - Address ✓
   - **Religion ✓** (NEW)
3. User must complete religion before accessing main app

## Notes

- Each person can have only ONE religion (enforced by unique constraint on `person_id`)
- Religion is required, but category and sub-category are optional
- Deleting religion marks profile as incomplete
- All endpoints require authentication
- Religion metadata is available via `/api/v1/metadata/religion/religions`

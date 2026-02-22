# Person Metadata Module

This module provides metadata management for person-related entities.

## Overview

The person module provides comprehensive person profile management including:

### Metadata Tables (Admin-managed)
- **Professions**: Manage different professions/occupations with weighted sorting
- **Genders**: Manage gender options with code-based identification

### Person Core
- **Person**: Core person profiles linked to user accounts with demographic information

### Association Tables
- **Person Address**: Link persons to addresses with temporal tracking
- **Person Profession**: Link persons to professions with temporal tracking
- **Person Relationship**: Track relationships between persons (spouse, parent, child, etc.)
- **Person Metadata**: Store profile images, bio, and extensible metadata

## Structure

```
backend/app/
├── api/routes/person/
│   ├── __init__.py
│   └── metadata.py              # API endpoints
├── db_models/person/
│   ├── __init__.py
│   └── profession.py            # Database model
├── repositories/person/
│   ├── __init__.py
│   └── profession_repository.py # Data access layer
├── schemas/person/
│   ├── __init__.py
│   └── profession.py            # Pydantic schemas
└── services/person/
    ├── __init__.py
    └── profession_service.py    # Business logic
```

## Features

### Metadata Management (Admin Only)
- **Professions**: Weighted sorting, unique names, active/inactive status
- **Genders**: Code-based identification, unique codes

### Person Profiles
- User-linked person profiles with demographic data
- One person per user account
- Date of birth and optional date of death tracking

### Associations
- **Addresses**: Temporal address history with current address tracking
- **Professions**: Career history with current profession tracking
- **Relationships**: Family and social relationships with relationship types
- **Metadata**: Profile images, biographies, and extensible data

## API Endpoints

### Metadata Endpoints (Admin)
Prefix: `/api/v1/metadata/person`

**Professions:**
- `GET /professions` - List all active professions (public)
- `GET /professions/{id}` - Get profession by ID (public)
- `POST /professions` - Create profession (admin only)
- `PATCH /professions/{id}` - Update profession (admin only)
- `DELETE /professions/{id}` - Delete profession (admin only)

**Genders:**
- `GET /genders` - List all active genders (public)
- `GET /genders/{id}` - Get gender by ID (public)
- `POST /genders` - Create gender (admin only)
- `PATCH /genders/{id}` - Update gender (admin only)
- `DELETE /genders/{id}` - Delete gender (admin only)

### Person Endpoints (User)
Prefix: `/api/v1/person`

**Profile:**
- `GET /me` - Get current user's person profile
- `POST /me` - Create person profile
- `PATCH /me` - Update person profile
- `DELETE /me` - Delete person profile

**Addresses:**
- `GET /me/addresses` - List all addresses
- `POST /me/addresses` - Create address
- `GET /me/addresses/{id}` - Get address by ID
- `PATCH /me/addresses/{id}` - Update address
- `DELETE /me/addresses/{id}` - Delete address

**Professions:**
- `GET /me/professions` - List all profession history
- `POST /me/professions` - Add profession
- `GET /me/professions/{id}` - Get profession by ID
- `PATCH /me/professions/{id}` - Update profession
- `DELETE /me/professions/{id}` - Delete profession

**Relationships:**
- `GET /me/relationships` - List all relationships
- `POST /me/relationships` - Create relationship
- `GET /me/relationships/{id}` - Get relationship by ID
- `PATCH /me/relationships/{id}` - Update relationship
- `DELETE /me/relationships/{id}` - Delete relationship

**Metadata:**
- `GET /me/metadata` - Get person metadata
- `POST /me/metadata` - Create metadata
- `PATCH /me/metadata` - Update metadata
- `DELETE /me/metadata` - Delete metadata

## Database Schema

### Profession Table
```sql
CREATE TABLE profession (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description VARCHAR(500),
    weight INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX ix_profession_name ON profession(name);
```

## Documentation

- [Professions API Documentation](./PROFESSIONS_API.md) - Profession metadata API reference
- [Person Metadata API Documentation](./PERSON_METADATA_API.md) - Person metadata (profile images, bio) API reference

## Testing

Integration tests are available:
```bash
# Test profession metadata
python3 backend/tests/integration_scripts/test_profession_integration.py

# Test person metadata (profile images, bio)
python3 backend/tests/integration_scripts/test_person_metadata_crud.py

# Test all person features (comprehensive)
python3 backend/tests/integration_scripts/test_person_metadata_integration.py
```

## Migrations

Database migrations (in order):
1. `g6h7i8j9k0l1_add_profession_table.py` - Profession metadata
2. `h7i8j9k0l1m2_add_gender_table.py` - Gender metadata
3. `i8j9k0l1m2n3_add_person_table.py` - Person core table
4. `j9k0l1m2n3o4_add_person_address_table.py` - Person-Address association
5. `k0l1m2n3o4p5_add_person_profession_table.py` - Person-Profession association
6. `m2n3o4p5q6r7_add_person_relationship_table.py` - Person relationships
7. `n3o4p5q6r7s8_add_person_metadata_table.py` - Person metadata

To apply all migrations:
```bash
cd backend
alembic upgrade head
```

## Usage Example

### Frontend Integration
```typescript
// Fetch professions for dropdown
const response = await fetch('/api/v1/metadata/person/professions');
const professions = await response.json();

// Display in select
<select name="profession">
  {professions.map(p => (
    <option key={p.professionId} value={p.professionId}>
      {p.professionName}
    </option>
  ))}
</select>
```

### Admin Operations
```bash
# Get admin token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Create profession
curl -X POST "http://localhost:8000/api/v1/metadata/person/professions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Software Engineer",
    "description": "Develops software applications",
    "weight": 100,
    "is_active": true
  }'
```

## Future Enhancements

Potential additions to the person module:
- **Contact Information**: Phone numbers, emails, social media
- **Education History**: Schools, degrees, certifications
- **Employment History**: Companies, positions, dates
- **Skills/Competencies**: Technical and soft skills
- **Languages**: Spoken languages with proficiency levels
- **Documents**: ID cards, passports, licenses
- **Emergency Contacts**: Contact persons for emergencies
- **Medical Information**: Blood type, allergies, conditions
- **Preferences**: Privacy settings, notification preferences

## Architecture

This module follows the clean architecture pattern used throughout the application:
1. **API Layer** (`routes/`) - HTTP endpoints and request/response handling
2. **Service Layer** (`services/`) - Business logic and validation
3. **Repository Layer** (`repositories/`) - Data access and queries
4. **Model Layer** (`db_models/`) - Database table definitions
5. **Schema Layer** (`schemas/`) - Request/response validation

## Related Modules

- [Address Metadata](../address/) - Geographic hierarchy (countries, states, districts, etc.)
- [Religion Metadata](../religion/) - Religious demographics hierarchy

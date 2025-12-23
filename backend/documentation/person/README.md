# Person Metadata Module

This module provides metadata management for person-related entities.

## Overview

The person metadata module currently includes:
- **Professions**: Manage different professions/occupations with weighted sorting

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

### Professions
- Full CRUD operations (Create, Read, Update, Delete)
- Public read access for dropdowns
- Admin-only write operations
- Weighted sorting (higher weight = higher priority)
- Unique name validation
- Active/inactive status

## API Endpoints

All endpoints are prefixed with `/api/v1/metadata/person`

### Professions
- `GET /professions` - List all active professions (public)
- `GET /professions/{id}` - Get profession by ID (public)
- `POST /professions` - Create profession (admin only)
- `PATCH /professions/{id}` - Update profession (admin only)
- `DELETE /professions/{id}` - Delete profession (admin only)

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

- [Professions API Documentation](./PROFESSIONS_API.md) - Complete API reference

## Testing

Integration tests are available:
```bash
python3 backend/tests/integration_scripts/test_profession_integration.py
```

## Migration

Database migration: `g6h7i8j9k0l1_add_profession_table.py`

To apply:
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

Potential additions to the person metadata module:
- Education levels
- Skills/Competencies
- Certifications
- Languages
- Marital status
- Other demographic metadata

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

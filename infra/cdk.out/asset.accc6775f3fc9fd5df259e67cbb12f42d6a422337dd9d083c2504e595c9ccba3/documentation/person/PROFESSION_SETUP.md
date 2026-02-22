# Person Profession CRUD API - Setup Guide

This document provides a quick guide to set up and test the newly implemented Person Profession CRUD API.

## What Was Implemented

A complete CRUD API for managing professions with the following fields:
- `profession_id` (UUID) - Unique identifier
- `profession_name` (string) - Name of the profession (unique)
- `profession_description` (string, optional) - Description
- `profession_weight` (integer) - Weight for sorting/priority

## Files Created

### 1. Database Model
- `backend/app/db_models/person/profession.py`
- `backend/app/db_models/person/__init__.py`

### 2. Repository Layer
- `backend/app/repositories/person/profession_repository.py`
- `backend/app/repositories/person/__init__.py`

### 3. Schema Layer
- `backend/app/schemas/person/profession.py`
- `backend/app/schemas/person/__init__.py`

### 4. Service Layer
- `backend/app/services/person/profession_service.py`
- `backend/app/services/person/__init__.py`

### 5. API Routes
- `backend/app/api/routes/person/metadata.py`
- `backend/app/api/routes/person/__init__.py`

### 6. Database Migration
- `backend/app/alembic/versions/g6h7i8j9k0l1_add_profession_table.py`

### 7. Tests
- `backend/tests/integration_scripts/test_profession_integration.py`

### 8. Documentation
- `backend/documentation/person/PROFESSIONS_API.md`
- `backend/documentation/person/README.md`

### 9. Updated Files
- `backend/app/api/main.py` - Registered the person router
- `backend/app/db_models/__init__.py` - Exported Profession model

## Setup Steps

### 1. Apply Database Migration

```bash
cd backend
alembic upgrade head
```

This will create the `profession` table in your database.

### 2. Restart Backend Server

If the server is running, restart it to load the new routes:

```bash
# Stop the current server (Ctrl+C)
# Then restart
uvicorn app.main:app --reload
```

### 3. Verify API in Swagger

Open your browser and navigate to:
```
http://localhost:8000/docs
```

Look for the **"person-metadata"** tag. You should see 5 endpoints:
- GET `/api/v1/metadata/person/professions`
- GET `/api/v1/metadata/person/professions/{profession_id}`
- POST `/api/v1/metadata/person/professions`
- PATCH `/api/v1/metadata/person/professions/{profession_id}`
- DELETE `/api/v1/metadata/person/professions/{profession_id}`

## Testing

### Manual Testing via Swagger

1. Go to http://localhost:8000/docs
2. Find the "person-metadata" section
3. Try the GET endpoint (no auth required)
4. For POST/PATCH/DELETE:
   - Click "Authorize" button at top
   - Login with: `admin@example.com` / `changethis`
   - Try creating a profession

### Automated Integration Tests

```bash
cd backend
python3 tests/integration_scripts/test_profession_integration.py
```

This will run comprehensive tests including:
- Create profession
- Read profession by ID
- Read all professions
- Update profession
- Delete profession
- Duplicate name validation

### Manual cURL Testing

```bash
# 1. Get all professions (public)
curl http://localhost:8000/api/v1/metadata/person/professions

# 2. Get admin token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 3. Create a profession
curl -X POST "http://localhost:8000/api/v1/metadata/person/professions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Software Engineer",
    "description": "Develops software applications",
    "weight": 100,
    "is_active": true
  }'

# 4. Get profession by ID (replace {id} with actual UUID from step 3)
curl http://localhost:8000/api/v1/metadata/person/professions/{id}

# 5. Update profession
curl -X PATCH "http://localhost:8000/api/v1/metadata/person/professions/{id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Senior Software Engineer",
    "weight": 150
  }'

# 6. Delete profession
curl -X DELETE "http://localhost:8000/api/v1/metadata/person/professions/{id}" \
  -H "Authorization: Bearer $TOKEN"
```

## API Endpoints Summary

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/metadata/person/professions` | None | Get all active professions |
| GET | `/api/v1/metadata/person/professions/{id}` | None | Get profession by ID |
| POST | `/api/v1/metadata/person/professions` | Admin | Create new profession |
| PATCH | `/api/v1/metadata/person/professions/{id}` | Admin | Update profession |
| DELETE | `/api/v1/metadata/person/professions/{id}` | Admin | Delete profession |

## Features

✅ Full CRUD operations
✅ Public read access (GET endpoints)
✅ Admin-only write access (POST/PATCH/DELETE)
✅ Unique name validation
✅ Weighted sorting (higher weight appears first)
✅ Active/inactive status
✅ Comprehensive error handling
✅ Integration tests
✅ Complete documentation

## Architecture Pattern

The implementation follows the same clean architecture pattern as the existing `address` and `religion` modules:

```
API Routes → Services → Repositories → Database Models
     ↓           ↓            ↓              ↓
  HTTP      Business      Data Access    SQLModel
 Handling     Logic        Queries        Tables
```

## Next Steps

1. **Apply Migration**: Run `alembic upgrade head`
2. **Restart Server**: Reload the backend
3. **Test**: Use Swagger UI or run integration tests
4. **Seed Data**: Optionally add initial profession data
5. **Frontend Integration**: Use the API in your frontend forms

## Troubleshooting

### Migration Issues
```bash
# Check current migration status
alembic current

# If needed, downgrade and re-upgrade
alembic downgrade -1
alembic upgrade head
```

### Import Errors
Make sure all `__init__.py` files are present in the person folders.

### API Not Showing in Swagger
Restart the backend server to reload the routes.

## Documentation

For detailed API documentation, see:
- [Professions API Documentation](backend/documentation/person/PROFESSIONS_API.md)
- [Person Module README](backend/documentation/person/README.md)

## Support

If you encounter any issues:
1. Check the backend logs
2. Verify the migration was applied
3. Ensure the server was restarted
4. Review the integration test output

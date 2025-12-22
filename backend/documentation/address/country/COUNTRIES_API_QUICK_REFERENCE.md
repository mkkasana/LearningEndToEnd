# Countries API - Quick Reference Card

## Endpoints Summary

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/v1/metadata/address/countries` | None | Get active countries |
| POST | `/api/v1/metadata/address/countries` | Superuser | Create country |
| PATCH | `/api/v1/metadata/address/countries/{id}` | Superuser | Update country |

## 1. GET Countries (Public)

```bash
curl http://localhost:8000/api/v1/metadata/address/countries
```

**Response:**
```json
[
  {"countryId": "uuid", "countryName": "India"},
  {"countryId": "uuid", "countryName": "United States"}
]
```

## 2. POST Create Country (Admin Only)

```bash
# Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Create country
curl -X POST "http://localhost:8000/api/v1/metadata/address/countries" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Country",
    "code": "NEW",
    "is_active": true
  }'
```

**Request Body:**
```json
{
  "name": "New Country",      // Required
  "code": "NEW",              // Required (3 chars)
  "is_active": true           // Optional (default: true)
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "New Country",
  "code": "NEW",
  "is_active": true
}
```

## 3. PATCH Update Country (Admin Only)

```bash
curl -X PATCH "http://localhost:8000/api/v1/metadata/address/countries/{country_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "is_active": false
  }'
```

**Request Body (all optional):**
```json
{
  "name": "Updated Name",     // Optional
  "code": "UPD",              // Optional
  "is_active": false          // Optional
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Updated Name",
  "code": "UPD",
  "is_active": false
}
```

## Error Responses

**401 Unauthorized (POST/PATCH without auth):**
```json
{"detail": "Not authenticated"}
```

**400 Duplicate Code:**
```json
{"detail": "Country with code 'USA' already exists"}
```

**404 Not Found (PATCH non-existent country):**
```json
{"detail": "Country not found"}
```

## Swagger UI

Interactive documentation: http://localhost:8000/docs

Look for the **metadata** tag.

## Files Modified/Created

```
backend/app/
├── db_models/country.py              # Database model
├── schemas/country.py                # API schemas (Create, Update, Public)
├── repositories/country_repository.py # Data access
├── services/country_service.py       # Business logic
└── api/routes/metadata.py            # API endpoints (GET, POST, PATCH)
```

## Key Features

✅ Public GET for dropdowns
✅ Admin-only CREATE/UPDATE
✅ Duplicate code validation
✅ Active/inactive filtering
✅ Uppercase code normalization
✅ Partial updates (PATCH)
✅ Full Swagger documentation

# Districts API Documentation

Complete reference for the Districts metadata API endpoints.

## Quick Reference

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/v1/metadata/address/state/{state_id}/districts` | None | Get districts by state |
| GET | `/api/v1/metadata/address/districts/{id}` | None | Get district by ID |
| POST | `/api/v1/metadata/address/districts` | Superuser | Create district |
| PATCH | `/api/v1/metadata/address/districts/{id}` | Superuser | Update district |
| DELETE | `/api/v1/metadata/address/districts/{id}` | Superuser | Delete district |

## Endpoints

### 1. GET Districts by State (Public)

```bash
curl http://localhost:8000/api/v1/metadata/address/state/{state_id}/districts
```

**Response:**
```json
[
  {"districtId": "uuid", "districtName": "Los Angeles"},
  {"districtId": "uuid", "districtName": "San Diego"}
]
```

### 2. GET District by ID (Public)

```bash
curl http://localhost:8000/api/v1/metadata/address/districts/{district_id}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Los Angeles",
  "code": "LA",
  "state_id": "uuid",
  "is_active": true
}
```

### 3. POST Create District (Admin)

```bash
curl -X POST "http://localhost:8000/api/v1/metadata/address/districts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New District",
    "code": "ND",
    "state_id": "state-uuid",
    "is_active": true
  }'
```

### 4. PATCH Update District (Admin)

```bash
curl -X PATCH "http://localhost:8000/api/v1/metadata/address/districts/{district_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'
```

### 5. DELETE District (Admin)

```bash
curl -X DELETE "http://localhost:8000/api/v1/metadata/address/districts/{district_id}" \
  -H "Authorization: Bearer $TOKEN"
```

## Schemas

### DistrictCreate (POST)
```typescript
{
  name: string;           // Required, max 255 chars
  code?: string;          // Optional, max 10 chars
  state_id: UUID;         // Required, must exist
  is_active: boolean;     // Optional, default: true
}
```

### DistrictUpdate (PATCH)
```typescript
{
  name?: string;          // Optional
  code?: string;          // Optional
  is_active?: boolean;    // Optional
}
```

### DistrictPublic (GET list)
```typescript
{
  districtId: UUID;
  districtName: string;
}
```

### DistrictDetailPublic (GET by ID, POST, PATCH)
```typescript
{
  id: UUID;
  name: string;
  code: string | null;
  state_id: UUID;
  is_active: boolean;
}
```

## Business Logic

- ✅ State existence validation
- ✅ Duplicate code prevention (within same state)
- ✅ Code converted to uppercase
- ✅ Returns only active districts in list
- ✅ Sorted alphabetically

## Database

**Table:** `address_district`

**Relationships:**
- Many-to-One with `address_state`
- One-to-Many with `address_sub_district`

## Testing

See `backend/tests/integration_scripts/test_address_full_integration.py`

## Swagger Documentation

http://localhost:8000/docs (tag: "address-metadata")

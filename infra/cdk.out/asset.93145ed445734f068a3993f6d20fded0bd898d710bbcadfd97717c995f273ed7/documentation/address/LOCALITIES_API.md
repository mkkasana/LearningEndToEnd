# Localities API Documentation

Complete reference for the Localities (Villages/Towns) metadata API endpoints.

## Quick Reference

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/v1/metadata/address/sub-district/{sub_district_id}/localities` | None | Get localities by sub-district |
| GET | `/api/v1/metadata/address/localities/{id}` | None | Get locality by ID |
| POST | `/api/v1/metadata/address/localities` | Superuser | Create locality |
| PATCH | `/api/v1/metadata/address/localities/{id}` | Superuser | Update locality |
| DELETE | `/api/v1/metadata/address/localities/{id}` | Superuser | Delete locality |

## Endpoints

### 1. GET Localities by Sub-District (Public)

```bash
curl http://localhost:8000/api/v1/metadata/address/sub-district/{sub_district_id}/localities
```

**Response:**
```json
[
  {"localityId": "uuid", "localityName": "Village A"},
  {"localityId": "uuid", "localityName": "Village B"}
]
```

### 2. GET Locality by ID (Public)

```bash
curl http://localhost:8000/api/v1/metadata/address/localities/{locality_id}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Village A",
  "code": "VA",
  "sub_district_id": "uuid",
  "is_active": true
}
```

### 3. POST Create Locality (Admin)

```bash
curl -X POST "http://localhost:8000/api/v1/metadata/address/localities" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Locality",
    "code": "NL",
    "sub_district_id": "sub-district-uuid",
    "is_active": true
  }'
```

### 4. PATCH Update Locality (Admin)

```bash
curl -X PATCH "http://localhost:8000/api/v1/metadata/address/localities/{locality_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'
```

### 5. DELETE Locality (Admin)

```bash
curl -X DELETE "http://localhost:8000/api/v1/metadata/address/localities/{locality_id}" \
  -H "Authorization: Bearer $TOKEN"
```

## Schemas

### LocalityCreate (POST)
```typescript
{
  name: string;              // Required, max 255 chars
  code?: string;             // Optional, max 10 chars
  sub_district_id: UUID;     // Required, must exist
  is_active: boolean;        // Optional, default: true
}
```

### LocalityUpdate (PATCH)
```typescript
{
  name?: string;             // Optional
  code?: string;             // Optional
  is_active?: boolean;       // Optional
}
```

### LocalityPublic (GET list)
```typescript
{
  localityId: UUID;
  localityName: string;
}
```

### LocalityDetailPublic (GET by ID, POST, PATCH)
```typescript
{
  id: UUID;
  name: string;
  code: string | null;
  sub_district_id: UUID;
  is_active: boolean;
}
```

## Business Logic

- ✅ Sub-district existence validation
- ✅ Duplicate code prevention (within same sub-district)
- ✅ Code converted to uppercase
- ✅ Returns only active localities in list
- ✅ Sorted alphabetically

## Database

**Table:** `address_locality`

**Relationships:**
- Many-to-One with `address_sub_district`

## Alternative Names

Localities are also known as:
- **Villages** (rural areas)
- **Towns** (urban areas)
- **Neighborhoods** (cities)

## Testing

See `backend/tests/integration_scripts/test_address_full_integration.py`

## Swagger Documentation

http://localhost:8000/docs (tag: "address-metadata")

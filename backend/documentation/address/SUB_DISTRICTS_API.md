# Sub-Districts API Documentation

Complete reference for the Sub-Districts (Tehsils/Counties) metadata API endpoints.

## Quick Reference

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/v1/metadata/address/district/{district_id}/sub-districts` | None | Get sub-districts by district |
| GET | `/api/v1/metadata/address/sub-districts/{id}` | None | Get sub-district by ID |
| POST | `/api/v1/metadata/address/sub-districts` | Superuser | Create sub-district |
| PATCH | `/api/v1/metadata/address/sub-districts/{id}` | Superuser | Update sub-district |
| DELETE | `/api/v1/metadata/address/sub-districts/{id}` | Superuser | Delete sub-district |

## Endpoints

### 1. GET Sub-Districts by District (Public)

```bash
curl http://localhost:8000/api/v1/metadata/address/district/{district_id}/sub-districts
```

**Response:**
```json
[
  {"tehsilId": "uuid", "tehsilName": "Downtown"},
  {"tehsilId": "uuid", "tehsilName": "Uptown"}
]
```

**Note:** Response uses `tehsilId` and `tehsilName` (alternative name for sub-district).

### 2. GET Sub-District by ID (Public)

```bash
curl http://localhost:8000/api/v1/metadata/address/sub-districts/{sub_district_id}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Downtown",
  "code": "DT",
  "district_id": "uuid",
  "is_active": true
}
```

### 3. POST Create Sub-District (Admin)

```bash
curl -X POST "http://localhost:8000/api/v1/metadata/address/sub-districts" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Sub-District",
    "code": "NSD",
    "district_id": "district-uuid",
    "is_active": true
  }'
```

### 4. PATCH Update Sub-District (Admin)

```bash
curl -X PATCH "http://localhost:8000/api/v1/metadata/address/sub-districts/{sub_district_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'
```

### 5. DELETE Sub-District (Admin)

```bash
curl -X DELETE "http://localhost:8000/api/v1/metadata/address/sub-districts/{sub_district_id}" \
  -H "Authorization: Bearer $TOKEN"
```

## Schemas

### SubDistrictCreate (POST)
```typescript
{
  name: string;           // Required, max 255 chars
  code?: string;          // Optional, max 10 chars
  district_id: UUID;      // Required, must exist
  is_active: boolean;     // Optional, default: true
}
```

### SubDistrictUpdate (PATCH)
```typescript
{
  name?: string;          // Optional
  code?: string;          // Optional
  is_active?: boolean;    // Optional
}
```

### SubDistrictPublic (GET list)
```typescript
{
  tehsilId: UUID;         // Note: tehsilId, not subDistrictId
  tehsilName: string;     // Note: tehsilName, not subDistrictName
}
```

### SubDistrictDetailPublic (GET by ID, POST, PATCH)
```typescript
{
  id: UUID;
  name: string;
  code: string | null;
  district_id: UUID;
  is_active: boolean;
}
```

## Business Logic

- ✅ District existence validation
- ✅ Duplicate code prevention (within same district)
- ✅ Code converted to uppercase
- ✅ Returns only active sub-districts in list
- ✅ Sorted alphabetically

## Database

**Table:** `address_sub_district`

**Relationships:**
- Many-to-One with `address_district`
- One-to-Many with `address_locality`

## Alternative Names

Sub-districts are also known as:
- **Tehsils** (India)
- **Counties** (USA)
- **Talukas** (some regions)

## Testing

See `backend/tests/integration_scripts/test_address_full_integration.py`

## Swagger Documentation

http://localhost:8000/docs (tag: "address-metadata")

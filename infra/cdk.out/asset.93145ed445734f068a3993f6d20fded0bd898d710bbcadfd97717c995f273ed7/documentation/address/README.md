# Address Metadata API - Overview

Complete documentation for the hierarchical address metadata API system.

## Hierarchy

```
Country → State → District → Sub-District → Locality
```

## Component Documentation

Each component has full CRUD operations (Create, Read, Update, Delete):

- **[Countries API](./COUNTRIES_API.md)** - Top-level geographic entities
- **[States API](./STATES_API.md)** - States/Provinces within countries
- **[Districts API](./DISTRICTS_API.md)** - Districts/Counties within states
- **[Sub-Districts API](./SUB_DISTRICTS_API.md)** - Tehsils/Counties within districts
- **[Localities API](./LOCALITIES_API.md)** - Villages/Towns within sub-districts

## Quick Start

### Base URL
```
http://localhost:8000/api/v1/metadata/address
```

### Authentication
- **GET endpoints:** Public (no auth required)
- **POST/PATCH/DELETE:** Superuser only

### Get Auth Token
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

## Common Patterns

### List Endpoints
Return simplified format (camelCase):
```json
[
  {"countryId": "uuid", "countryName": "India"},
  {"stateId": "uuid", "stateName": "California"},
  {"districtId": "uuid", "districtName": "Los Angeles"},
  {"tehsilId": "uuid", "tehsilName": "Downtown"},
  {"localityId": "uuid", "localityName": "Village A"}
]
```

### Detail Endpoints
Return full object (snake_case):
```json
{
  "id": "uuid",
  "name": "India",
  "code": "IND",
  "is_active": true
}
```

## Frontend Integration

```typescript
// Cascading dropdowns example
const [selectedCountry, setSelectedCountry] = useState('');
const [states, setStates] = useState([]);

// Load states when country changes
useEffect(() => {
  if (selectedCountry) {
    fetch(`/api/v1/metadata/address/country/${selectedCountry}/states`)
      .then(res => res.json())
      .then(setStates);
  }
}, [selectedCountry]);
```

## Testing

Run comprehensive integration tests:
```bash
python3 backend/tests/integration_scripts/test_address_full_integration.py
```

**Coverage:** 35 tests across all 25 endpoints (100% coverage)

## Database Tables

- `address_country`
- `address_state`
- `address_district`
- `address_sub_district`
- `address_locality`

All tables follow the same pattern:
- `id` (UUID, primary key)
- `name` (VARCHAR(255))
- `code` (VARCHAR, optional)
- `parent_id` (UUID, foreign key - except country)
- `is_active` (BOOLEAN)

## Swagger Documentation

Interactive API docs: http://localhost:8000/docs

Look for the **address-metadata** tag.

## Error Responses

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Not authenticated |
| 404 | Resource not found |
| 400 | Validation error (e.g., duplicate code) |

## Features

✅ Full CRUD operations for all components
✅ Hierarchical data relationships
✅ Duplicate code prevention (within scope)
✅ Active/inactive filtering
✅ Public read access
✅ Admin-only write access
✅ Comprehensive validation
✅ Foreign key constraints
✅ Cascade deletion support

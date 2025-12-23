# States API Documentation

Complete reference for the States metadata API endpoints.

## Quick Reference

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/v1/metadata/address/country/{country_id}/states` | None | Get states by country |
| GET | `/api/v1/metadata/address/states/{id}` | None | Get state by ID |
| POST | `/api/v1/metadata/address/states` | Superuser | Create state |
| PATCH | `/api/v1/metadata/address/states/{id}` | Superuser | Update state |
| DELETE | `/api/v1/metadata/address/states/{id}` | Superuser | Delete state |

## Endpoints

### 1. GET States by Country (Public)

Returns list of active states for a specific country.

```bash
curl http://localhost:8000/api/v1/metadata/address/country/{country_id}/states
```

**Response:**
```json
[
  {"stateId": "uuid", "stateName": "California"},
  {"stateId": "uuid", "stateName": "Texas"}
]
```

### 2. GET State by ID (Public)

```bash
curl http://localhost:8000/api/v1/metadata/address/states/{state_id}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "California",
  "code": "CA",
  "country_id": "uuid",
  "is_active": true
}
```

### 3. POST Create State (Admin)

```bash
curl -X POST "http://localhost:8000/api/v1/metadata/address/states" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New State",
    "code": "NS",
    "country_id": "country-uuid",
    "is_active": true
  }'
```

**Request Body:**
```json
{
  "name": "New State",        // Required, max 255 chars
  "code": "NS",               // Optional, max 10 chars
  "country_id": "uuid",       // Required, must exist
  "is_active": true           // Optional, default: true
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "New State",
  "code": "NS",
  "country_id": "uuid",
  "is_active": true
}
```

### 4. PATCH Update State (Admin)

```bash
curl -X PATCH "http://localhost:8000/api/v1/metadata/address/states/{state_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type": application/json" \
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

### 5. DELETE State (Admin)

```bash
curl -X DELETE "http://localhost:8000/api/v1/metadata/address/states/{state_id}" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "message": "State deleted successfully"
}
```

## Schemas

### StateCreate (POST)
```typescript
{
  name: string;           // Required, max 255 chars
  code?: string;          // Optional, max 10 chars
  country_id: UUID;       // Required, must exist
  is_active: boolean;     // Optional, default: true
}
```

### StateUpdate (PATCH)
```typescript
{
  name?: string;          // Optional
  code?: string;          // Optional
  is_active?: boolean;    // Optional
}
```

### StatePublic (GET list)
```typescript
{
  stateId: UUID;
  stateName: string;
}
```

### StateDetailPublic (GET by ID, POST, PATCH)
```typescript
{
  id: UUID;
  name: string;
  code: string | null;
  country_id: UUID;
  is_active: boolean;
}
```

## Business Logic

### Validation
- ✅ Country existence check (404 if not found)
- ✅ Duplicate code prevention (within same country)
- ✅ Code converted to uppercase
- ✅ Required field validation

### Filtering
- ✅ GET list returns only active states
- ✅ Sorted alphabetically by name
- ✅ Filtered by country

### Security
- ✅ GET: Public access
- ✅ POST/PATCH/DELETE: Superuser only
- ✅ Foreign key constraint ensures data integrity

## Error Responses

**401 Unauthorized:**
```json
{"detail": "Not authenticated"}
```

**400 Duplicate Code:**
```json
{"detail": "State with code 'CA' already exists in this country"}
```

**404 Country Not Found:**
```json
{"detail": "Country not found"}
```

**404 State Not Found:**
```json
{"detail": "State not found"}
```

## Frontend Integration

```typescript
// Cascading dropdowns: Country -> State
const [countries, setCountries] = useState([]);
const [states, setStates] = useState([]);
const [selectedCountry, setSelectedCountry] = useState('');

// Load countries
useEffect(() => {
  fetch('http://localhost:8000/api/v1/metadata/address/countries')
    .then(res => res.json())
    .then(setCountries);
}, []);

// Load states when country changes
useEffect(() => {
  if (selectedCountry) {
    fetch(`http://localhost:8000/api/v1/metadata/address/country/${selectedCountry}/states`)
      .then(res => res.json())
      .then(setStates);
  } else {
    setStates([]);
  }
}, [selectedCountry]);

// Render
<select onChange={(e) => setSelectedCountry(e.target.value)}>
  <option value="">Select Country</option>
  {countries.map(c => (
    <option key={c.countryId} value={c.countryId}>{c.countryName}</option>
  ))}
</select>

<select disabled={!selectedCountry}>
  <option value="">Select State</option>
  {states.map(s => (
    <option key={s.stateId} value={s.stateId}>{s.stateName}</option>
  ))}
</select>
```

## Database

**Table:** `address_state`

**Columns:**
- `id` (UUID, primary key)
- `name` (VARCHAR(255), indexed)
- `code` (VARCHAR(10), nullable)
- `country_id` (UUID, foreign key to address_country.id, indexed)
- `is_active` (BOOLEAN, default true)

**Relationships:**
- Many-to-One with `address_country`
- One-to-Many with `address_district`

## Seeded Data

- **Indian States:** 36 states and union territories
- **US States:** 50 states

## Testing

See `backend/tests/integration_scripts/test_address_full_integration.py` for comprehensive integration tests.

## Swagger Documentation

Interactive API docs: http://localhost:8000/docs (look for "address-metadata" tag)

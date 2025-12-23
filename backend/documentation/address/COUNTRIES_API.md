# Countries API Documentation

Complete reference for the Countries metadata API endpoints.

## Quick Reference

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/v1/metadata/address/countries` | None | Get active countries |
| GET | `/api/v1/metadata/address/countries/{id}` | None | Get country by ID |
| POST | `/api/v1/metadata/address/countries` | Superuser | Create country |
| PATCH | `/api/v1/metadata/address/countries/{id}` | Superuser | Update country |
| DELETE | `/api/v1/metadata/address/countries/{id}` | Superuser | Delete country |

## Endpoints

### 1. GET All Countries (Public)

Returns list of active countries for dropdowns.

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

### 2. GET Country by ID (Public)

```bash
curl http://localhost:8000/api/v1/metadata/address/countries/{country_id}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "India",
  "code": "IND",
  "is_active": true
}
```

### 3. POST Create Country (Admin)

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
  "name": "New Country",      // Required, max 255 chars
  "code": "NEW",              // Required, 3 chars (ISO code)
  "is_active": true           // Optional, default: true
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

### 4. PATCH Update Country (Admin)

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

### 5. DELETE Country (Admin)

```bash
curl -X DELETE "http://localhost:8000/api/v1/metadata/address/countries/{country_id}" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "message": "Country deleted successfully"
}
```

## Schemas

### CountryCreate (POST)
```typescript
{
  name: string;        // Required, max 255 chars
  code: string;        // Required, 3 chars (ISO code)
  is_active: boolean;  // Optional, default: true
}
```

### CountryUpdate (PATCH)
```typescript
{
  name?: string;       // Optional
  code?: string;       // Optional
  is_active?: boolean; // Optional
}
```

### CountryPublic (GET list)
```typescript
{
  countryId: UUID;
  countryName: string;
}
```

### CountryDetailPublic (GET by ID, POST, PATCH)
```typescript
{
  id: UUID;
  name: string;
  code: string;
  is_active: boolean;
}
```

## Business Logic

### Validation
- ✅ Duplicate code prevention
- ✅ Code converted to uppercase
- ✅ Required field validation
- ✅ Field length limits

### Filtering
- ✅ GET list returns only active countries
- ✅ GET by ID returns all fields
- ✅ Sorted alphabetically by name

### Security
- ✅ GET: Public access
- ✅ POST/PATCH/DELETE: Superuser only
- ✅ Token-based authentication

## Error Responses

**401 Unauthorized:**
```json
{"detail": "Not authenticated"}
```

**400 Duplicate Code:**
```json
{"detail": "Country with code 'USA' already exists"}
```

**404 Not Found:**
```json
{"detail": "Country not found"}
```

## Frontend Integration

```typescript
// Get countries for dropdown
const getCountries = async () => {
  const response = await fetch('http://localhost:8000/api/v1/metadata/address/countries');
  return await response.json();
};

// Create country (admin)
const createCountry = async (token: string, country: CountryCreate) => {
  const response = await fetch('http://localhost:8000/api/v1/metadata/address/countries', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(country),
  });
  return await response.json();
};

// Usage in React
const [countries, setCountries] = useState([]);

useEffect(() => {
  getCountries().then(setCountries);
}, []);

<select name="country">
  {countries.map(c => (
    <option key={c.countryId} value={c.countryId}>
      {c.countryName}
    </option>
  ))}
</select>
```

## Database

**Table:** `address_country`

**Columns:**
- `id` (UUID, primary key)
- `name` (VARCHAR(255), unique, indexed)
- `code` (VARCHAR(3), unique, indexed)
- `is_active` (BOOLEAN, default true)

## Testing

See `backend/tests/integration_scripts/test_address_full_integration.py` for comprehensive integration tests.

## Swagger Documentation

Interactive API docs: http://localhost:8000/docs (look for "address-metadata" tag)

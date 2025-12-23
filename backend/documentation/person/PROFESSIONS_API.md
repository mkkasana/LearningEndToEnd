# Professions API Documentation

Complete reference for the Professions metadata API endpoints.

## Quick Reference

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/api/v1/metadata/person/professions` | None | Get active professions |
| GET | `/api/v1/metadata/person/professions/{id}` | None | Get profession by ID |
| POST | `/api/v1/metadata/person/professions` | Superuser | Create profession |
| PATCH | `/api/v1/metadata/person/professions/{id}` | Superuser | Update profession |
| DELETE | `/api/v1/metadata/person/professions/{id}` | Superuser | Delete profession |

## Endpoints

### 1. GET All Professions (Public)

Returns list of active professions for dropdowns, sorted by weight (descending) then name.

```bash
curl http://localhost:8000/api/v1/metadata/person/professions
```

**Response:**
```json
[
  {
    "professionId": "uuid",
    "professionName": "Software Engineer",
    "professionDescription": "Develops software applications",
    "professionWeight": 100
  },
  {
    "professionId": "uuid",
    "professionName": "Doctor",
    "professionDescription": "Medical professional",
    "professionWeight": 90
  }
]
```

### 2. GET Profession by ID (Public)

```bash
curl http://localhost:8000/api/v1/metadata/person/professions/{profession_id}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Software Engineer",
  "description": "Develops software applications",
  "weight": 100,
  "is_active": true
}
```

### 3. POST Create Profession (Admin)

```bash
# Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Create profession
curl -X POST "http://localhost:8000/api/v1/metadata/person/professions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Data Scientist",
    "description": "Analyzes and interprets complex data",
    "weight": 85,
    "is_active": true
  }'
```

**Request Body:**
```json
{
  "name": "Data Scientist",                        // Required, max 255 chars, unique
  "description": "Analyzes and interprets data",   // Optional, max 500 chars
  "weight": 85,                                    // Optional, default: 0
  "is_active": true                                // Optional, default: true
}
```

**Response:**
```json
{
  "id": "uuid",
  "name": "Data Scientist",
  "description": "Analyzes and interprets complex data",
  "weight": 85,
  "is_active": true
}
```

### 4. PATCH Update Profession (Admin)

```bash
curl -X PATCH "http://localhost:8000/api/v1/metadata/person/professions/{profession_id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Senior Data Scientist",
    "weight": 95
  }'
```

**Request Body (all optional):**
```json
{
  "name": "Senior Data Scientist",  // Optional
  "description": "Updated desc",    // Optional
  "weight": 95,                     // Optional
  "is_active": false                // Optional
}
```

### 5. DELETE Profession (Admin)

```bash
curl -X DELETE "http://localhost:8000/api/v1/metadata/person/professions/{profession_id}" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "message": "Profession deleted successfully"
}
```

## Schemas

### ProfessionCreate (POST)
```typescript
{
  name: string;              // Required, max 255 chars, unique
  description?: string;      // Optional, max 500 chars
  weight?: number;           // Optional, default: 0
  is_active?: boolean;       // Optional, default: true
}
```

### ProfessionUpdate (PATCH)
```typescript
{
  name?: string;             // Optional
  description?: string;      // Optional
  weight?: number;           // Optional
  is_active?: boolean;       // Optional
}
```

### ProfessionPublic (GET list)
```typescript
{
  professionId: UUID;
  professionName: string;
  professionDescription: string | null;
  professionWeight: number;
}
```

### ProfessionDetailPublic (GET by ID, POST, PATCH)
```typescript
{
  id: UUID;
  name: string;
  description: string | null;
  weight: number;
  is_active: boolean;
}
```

## Business Logic

### Validation
- ✅ Duplicate name prevention
- ✅ Required field validation
- ✅ Field length limits (name: 255, description: 500)

### Sorting
- ✅ GET list returns professions sorted by:
  1. Weight (descending) - higher weight appears first
  2. Name (ascending) - alphabetical for same weight
- ✅ Only active professions returned in list

### Weight System
The `weight` field allows prioritizing certain professions:
- Higher weight = appears first in lists
- Use cases:
  - Popular professions: weight 100+
  - Common professions: weight 50-99
  - Less common: weight 0-49
  - Default: 0

### Security
- ✅ GET: Public access
- ✅ POST/PATCH/DELETE: Superuser only
- ✅ Token-based authentication

## Error Responses

**401 Unauthorized:**
```json
{"detail": "Not authenticated"}
```

**400 Duplicate Name:**
```json
{"detail": "Profession with name 'Software Engineer' already exists"}
```

**404 Not Found:**
```json
{"detail": "Profession not found"}
```

## Frontend Integration

```typescript
// Get professions for dropdown
const getProfessions = async () => {
  const response = await fetch('http://localhost:8000/api/v1/metadata/person/professions');
  return await response.json();
};

// Create profession (admin)
const createProfession = async (token: string, profession: ProfessionCreate) => {
  const response = await fetch('http://localhost:8000/api/v1/metadata/person/professions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(profession),
  });
  return await response.json();
};

// Usage in React
const [professions, setProfessions] = useState([]);

useEffect(() => {
  getProfessions().then(setProfessions);
}, []);

<select name="profession">
  {professions.map(p => (
    <option key={p.professionId} value={p.professionId}>
      {p.professionName}
    </option>
  ))}
</select>
```

## Database

**Table:** `profession`

**Columns:**
- `id` (UUID, primary key)
- `name` (VARCHAR(255), unique, indexed)
- `description` (VARCHAR(500), nullable)
- `weight` (INTEGER, default 0)
- `is_active` (BOOLEAN, default true)

**Migration:** `g6h7i8j9k0l1_add_profession_table.py`

## Testing

Run integration tests:
```bash
# Start the backend server first
cd backend
python3 tests/integration_scripts/test_profession_integration.py
```

See `backend/tests/integration_scripts/test_profession_integration.py` for comprehensive integration tests.

## Swagger Documentation

Interactive API docs: http://localhost:8000/docs (look for "person-metadata" tag)

## Example Use Cases

### 1. Populate Profession Dropdown
```typescript
// Fetch and display professions in a form
const professions = await getProfessions();
// Professions are already sorted by weight and name
```

### 2. Admin: Add New Profession
```typescript
await createProfession(adminToken, {
  name: "Machine Learning Engineer",
  description: "Develops ML models and systems",
  weight: 95,  // High priority
  is_active: true
});
```

### 3. Admin: Deactivate Profession
```typescript
await updateProfession(adminToken, professionId, {
  is_active: false  // Hide from public lists
});
```

### 4. Admin: Reorder Professions
```typescript
// Increase weight to move profession higher in list
await updateProfession(adminToken, professionId, {
  weight: 100
});
```

# Address Metadata API Documentation

## Overview

Complete API for managing address metadata including countries and states. Supports cascading dropdowns for address forms.

## Base URL

```
http://localhost:8000/api/v1/metadata/address
```

## Endpoints Summary

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/countries` | None | Get all active countries |
| GET | `/countries/{id}` | None | Get country by ID |
| POST | `/countries` | Admin | Create new country |
| PATCH | `/countries/{id}` | Admin | Update country |
| GET | `/country/{id}/states` | None | Get states for country |
| GET | `/states/{id}` | None | Get state by ID |
| POST | `/states` | Admin | Create new state |
| PATCH | `/states/{id}` | Admin | Update state |

---

## Countries API

### GET /countries

Get list of all active countries for dropdown options.

**Authentication:** None required (public)

**Request:**
```bash
GET /api/v1/metadata/address/countries
```

**Response:** 200 OK
```json
[
  {
    "countryId": "uuid",
    "countryName": "India"
  },
  {
    "countryId": "uuid",
    "countryName": "United States"
  }
]
```

**Example:**
```bash
curl http://localhost:8000/api/v1/metadata/address/countries
```

---

### POST /countries

Create a new country.

**Authentication:** Required (superuser only)

**Request:**
```bash
POST /api/v1/metadata/address/countries
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New Country",
  "code": "NEW",
  "is_active": true
}
```

**Response:** 200 OK
```json
{
  "id": "uuid",
  "name": "New Country",
  "code": "NEW",
  "is_active": true
}
```

**Validation:**
- Country code must be unique
- Code is automatically converted to uppercase

---

### PATCH /countries/{country_id}

Update an existing country.

**Authentication:** Required (superuser only)

**Request:**
```bash
PATCH /api/v1/metadata/address/countries/{country_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "is_active": false
}
```

**Response:** 200 OK
```json
{
  "id": "uuid",
  "name": "Updated Name",
  "code": "UPD",
  "is_active": false
}
```

---

## States API

### GET /country/{country_id}/states

Get list of all active states for a specific country.

**Authentication:** None required (public)

**Request:**
```bash
GET /api/v1/metadata/address/country/{country_id}/states
```

**Response:** 200 OK
```json
[
  {
    "stateId": "uuid",
    "stateName": "Andaman and Nicobar Islands"
  },
  {
    "stateId": "uuid",
    "stateName": "Andhra Pradesh"
  }
]
```

**Error Responses:**
- 404: Country not found

**Example:**
```bash
# Get India's country ID
INDIA_ID=$(curl -s "http://localhost:8000/api/v1/metadata/address/countries" | \
  python3 -c "import sys, json; data = json.load(sys.stdin); india = [c for c in data if c['countryName'] == 'India']; print(india[0]['countryId'])")

# Get states
curl "http://localhost:8000/api/v1/metadata/address/country/$INDIA_ID/states"
```

---

### POST /states

Create a new state.

**Authentication:** Required (superuser only)

**Request:**
```bash
POST /api/v1/metadata/address/states
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "New State",
  "code": "NS",
  "country_id": "uuid",
  "is_active": true
}
```

**Response:** 200 OK
```json
{
  "id": "uuid",
  "name": "New State",
  "code": "NS",
  "country_id": "uuid",
  "is_active": true
}
```

**Validation:**
- Country must exist
- State code must be unique within the country
- Code is automatically converted to uppercase

---

### PATCH /states/{state_id}

Update an existing state.

**Authentication:** Required (superuser only)

**Request:**
```bash
PATCH /api/v1/metadata/address/states/{state_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated State Name",
  "is_active": false
}
```

**Response:** 200 OK
```json
{
  "id": "uuid",
  "name": "Updated State Name",
  "code": "USN",
  "country_id": "uuid",
  "is_active": false
}
```

---

## Data Models

### Country

```typescript
{
  id: UUID;           // Auto-generated
  name: string;       // Max 255 chars, unique
  code: string;       // Max 3 chars, unique, uppercase
  is_active: boolean; // Default: true
}
```

### State

```typescript
{
  id: UUID;           // Auto-generated
  name: string;       // Max 255 chars
  code: string;       // Max 10 chars, optional
  country_id: UUID;   // Foreign key to country
  is_active: boolean; // Default: true
}
```

---

## Frontend Integration

### Cascading Dropdowns Example

```typescript
import { useState, useEffect } from 'react';

const AddressForm = () => {
  const [countries, setCountries] = useState([]);
  const [states, setStates] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedState, setSelectedState] = useState('');

  // Load countries on mount
  useEffect(() => {
    fetch('http://localhost:8000/api/v1/metadata/address/countries')
      .then(res => res.json())
      .then(data => setCountries(data));
  }, []);

  // Load states when country changes
  useEffect(() => {
    if (selectedCountry) {
      fetch(`http://localhost:8000/api/v1/metadata/address/country/${selectedCountry}/states`)
        .then(res => res.json())
        .then(data => setStates(data));
    } else {
      setStates([]);
      setSelectedState('');
    }
  }, [selectedCountry]);

  return (
    <form>
      <select 
        value={selectedCountry}
        onChange={(e) => setSelectedCountry(e.target.value)}
      >
        <option value="">Select Country</option>
        {countries.map(c => (
          <option key={c.countryId} value={c.countryId}>
            {c.countryName}
          </option>
        ))}
      </select>

      <select 
        value={selectedState}
        onChange={(e) => setSelectedState(e.target.value)}
        disabled={!selectedCountry}
      >
        <option value="">Select State</option>
        {states.map(s => (
          <option key={s.stateId} value={s.stateId}>
            {s.stateName}
          </option>
        ))}
      </select>
    </form>
  );
};
```

---

## Seeded Data

### Countries (51 total)
Afghanistan, Albania, Algeria, Argentina, Australia, Austria, Bangladesh, Belgium, Brazil, Canada, China, Denmark, Egypt, Finland, France, Germany, Greece, India, Indonesia, Iran, Iraq, Ireland, Israel, Italy, Japan, Kenya, Malaysia, Mexico, Netherlands, New Zealand, Nigeria, Norway, Pakistan, Philippines, Poland, Portugal, Russia, Saudi Arabia, Singapore, South Africa, South Korea, Spain, Sweden, Switzerland, Thailand, Turkey, Ukraine, United Arab Emirates, United Kingdom, United States, Vietnam

### States
- **India:** 36 states and union territories
- **USA:** 50 states

---

## Setup Instructions

### 1. Run Migrations

```bash
cd backend
alembic upgrade head
```

### 2. Seed Data

```bash
# Seed countries
python init_seed/seed_countries.py

# Seed states
python init_seed/seed_states.py
```

### 3. Verify

```bash
# Test countries endpoint
curl http://localhost:8000/api/v1/metadata/address/countries

# Test states endpoint (replace with actual country ID)
curl http://localhost:8000/api/v1/metadata/address/country/{country_id}/states
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Country with code 'USA' already exists"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Country not found"
}
```

---

## Performance

- **GET Countries:** < 50ms
- **GET States:** < 50ms (indexed by country_id)
- **POST/PATCH:** < 100ms (includes validation)

---

## Security

- **Public Endpoints:** GET countries, GET states
- **Admin Only:** POST/PATCH operations
- **Validation:** Duplicate checks, foreign key constraints
- **Data Integrity:** Uppercase normalization, active/inactive filtering

---

## Swagger Documentation

Interactive API documentation available at:
```
http://localhost:8000/docs
```

Look for the **address-metadata** tag.

---

## Related Documentation

- [Database Workflow](../DATABASE_WORKFLOW.md)
- [Countries API Details](country/COUNTRIES_API_GUIDE.md)
- [States API Test Results](country/STATES_API_TEST_RESULTS.md)

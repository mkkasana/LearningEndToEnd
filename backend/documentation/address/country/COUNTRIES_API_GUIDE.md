# Countries Metadata API - Implementation Guide

## Overview
This document describes the implementation of the `/metadata/address/countries` API endpoint.

## API Endpoint

**URL:** `http://localhost:8000/api/v1/metadata/address/countries`

**Method:** `GET`

**Authentication:** Not required (public endpoint)

**Use Case:** Get list of countries for dropdown options during user registration or profile creation.

## Response Schema

```json
[
  {
    "countryId": "550e8400-e29b-41d4-a716-446655440000",
    "countryName": "India"
  },
  {
    "countryId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "countryName": "United States"
  }
]
```

## Implementation Architecture

### Files Created

1. **Database Model** - `backend/app/db_models/country.py`
   - Defines the `Country` table with id, name, code, and is_active fields

2. **Schema** - `backend/app/schemas/country.py`
   - `CountryPublic`: Response schema with countryId and countryName
   - `CountriesPublic`: List wrapper (optional)

3. **Repository** - `backend/app/repositories/country_repository.py`
   - `CountryRepository`: Data access layer
   - Methods: `get_active_countries()`, `get_by_code()`

4. **Service** - `backend/app/services/country_service.py`
   - `CountryService`: Business logic layer
   - Method: `get_countries()` - returns formatted country list

5. **Route** - `backend/app/api/routes/metadata.py`
   - API endpoint definition
   - Route: `GET /metadata/address/countries`

6. **Migration** - `backend/app/alembic/versions/f3a1b2c4d5e6_add_country_table.py`
   - Database migration to create country table

7. **Seed Script** - `backend/app/seed_countries.py`
   - Populates initial country data (50+ countries)

## Setup Instructions

### 1. Run Database Migration

```bash
cd backend
alembic upgrade head
```

This creates the `country` table in your database.

### 2. Seed Country Data

```bash
cd backend
python -m app.seed_countries
```

This populates the country table with initial data.

### 3. Start the Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 4. Test the Endpoint

**Using curl:**
```bash
curl http://localhost:8000/api/v1/metadata/address/countries
```

**Using browser:**
Navigate to: `http://localhost:8000/api/v1/metadata/address/countries`

**Using Swagger UI:**
Navigate to: `http://localhost:8000/docs`
Look for the `metadata` tag and test the endpoint interactively.

## Example Response

```json
[
  {
    "countryId": "123e4567-e89b-12d3-a456-426614174000",
    "countryName": "Afghanistan"
  },
  {
    "countryId": "223e4567-e89b-12d3-a456-426614174001",
    "countryName": "Albania"
  },
  {
    "countryId": "323e4567-e89b-12d3-a456-426614174002",
    "countryName": "Algeria"
  },
  ...
]
```

## Frontend Integration Example

```typescript
// Fetch countries for dropdown
async function fetchCountries() {
  const response = await fetch('http://localhost:8000/api/v1/metadata/address/countries');
  const countries = await response.json();
  return countries;
}

// Usage in React component
const [countries, setCountries] = useState([]);

useEffect(() => {
  fetchCountries().then(data => setCountries(data));
}, []);

// Render dropdown
<select name="country">
  {countries.map(country => (
    <option key={country.countryId} value={country.countryId}>
      {country.countryName}
    </option>
  ))}
</select>
```

## Architecture Benefits

- **Layered Architecture**: Clear separation of concerns
- **Reusable**: Service and repository can be used by other endpoints
- **Testable**: Each layer can be tested independently
- **Scalable**: Easy to add more metadata endpoints (states, cities, etc.)
- **Type-Safe**: Full type checking with Pydantic schemas

## Future Enhancements

1. Add states/provinces endpoint: `/metadata/address/states/{countryId}`
2. Add cities endpoint: `/metadata/address/cities/{stateId}`
3. Add caching for better performance
4. Add filtering/search capabilities
5. Add pagination for large datasets

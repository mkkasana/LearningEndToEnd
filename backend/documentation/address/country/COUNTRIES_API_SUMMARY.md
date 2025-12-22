# Countries Metadata API - Quick Start

## What Was Created

A complete `/metadata/address/countries` API endpoint following your backend's clean architecture pattern.

## Files Created

1. ✅ `app/db_models/country.py` - Database model
2. ✅ `app/schemas/country.py` - API schemas
3. ✅ `app/repositories/country_repository.py` - Data access
4. ✅ `app/services/country_service.py` - Business logic
5. ✅ `app/api/routes/metadata.py` - API endpoint
6. ✅ `app/alembic/versions/f3a1b2c4d5e6_add_country_table.py` - Migration
7. ✅ `app/seed_countries.py` - Seed script (50+ countries)
8. ✅ `test_countries_api.sh` - Test script

## Files Modified

1. ✅ `app/api/main.py` - Added metadata router

## Quick Start (3 Steps)

### Step 1: Run Migration
```bash
cd backend
alembic upgrade head
```

### Step 2: Seed Data
```bash
python -m app.seed_countries
```

### Step 3: Test
```bash
# Start server (if not running)
uvicorn app.main:app --reload --port 8000

# In another terminal, test the endpoint
./test_countries_api.sh
```

## API Details

**Endpoint:** `GET /api/v1/metadata/address/countries`

**Authentication:** None required (public endpoint)

**Response Example:**
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

## Architecture Pattern Used

```
Route → Service → Repository → Database
  ↓        ↓          ↓
Schema   Logic    Data Access
```

This follows the same pattern as your existing `users` and `items` endpoints.

## Next Steps

1. Run the migration and seed data
2. Test the endpoint using the test script or Swagger UI
3. Integrate with your frontend registration form
4. (Optional) Add more metadata endpoints:
   - States/provinces: `/metadata/address/states/{countryId}`
   - Cities: `/metadata/address/cities/{stateId}`

## Documentation

- 📖 Full guide: `COUNTRIES_API_GUIDE.md`
- 🔄 Flow diagram: `COUNTRIES_API_FLOW.md`
- ⚡ This summary: `COUNTRIES_API_SUMMARY.md`

## Troubleshooting

**Migration fails?**
- Check database connection in `.env`
- Ensure PostgreSQL is running

**No data returned?**
- Run the seed script: `python -m app.seed_countries`

**Import errors?**
- Ensure you're in the backend directory
- Check virtual environment is activated

**Port already in use?**
- Change port: `uvicorn app.main:app --reload --port 8001`
- Update test script: `./test_countries_api.sh 8001`

# Quick Start - Address API Integration Testing

## Run the Full Integration Test Suite

```bash
# From project root
python3 backend/tests/integration_scripts/test_address_full_integration.py

# Or from backend directory
cd backend
python3 tests/integration_scripts/test_address_full_integration.py
```

## What Gets Tested

The comprehensive integration test covers **35 test cases** across all address components:

### 🔐 Authentication (4 tests)
- POST/PATCH/DELETE require superuser authentication
- GET endpoints are public

### 🌍 Countries (6 tests)
- ✓ CREATE country
- ✓ READ country by ID
- ✓ READ all countries
- ✓ UPDATE country
- ✓ Duplicate code validation
- ✓ 404 error handling

### 🏛️ States (5 tests)
- ✓ CREATE state
- ✓ READ state by ID
- ✓ READ states by country
- ✓ UPDATE state
- ✓ Invalid parent validation

### 🏙️ Districts (4 tests)
- ✓ CREATE district
- ✓ READ district by ID
- ✓ READ districts by state
- ✓ UPDATE district

### 🏘️ Sub-Districts (4 tests)
- ✓ CREATE sub-district
- ✓ READ sub-district by ID
- ✓ READ sub-districts by district
- ✓ UPDATE sub-district

### 🏡 Localities (4 tests)
- ✓ CREATE locality
- ✓ READ locality by ID
- ✓ READ localities by sub-district
- ✓ UPDATE locality

### 🗑️ DELETE Operations (8 tests)
- ✓ DELETE locality
- ✓ DELETE sub-district
- ✓ DELETE district
- ✓ DELETE state
- ✓ DELETE country
- ✓ 404 for non-existent resource
- ✓ 401 without authentication
- ✓ Hierarchical cascade deletion

## Expected Output

```
======================================================================
  Address Metadata API - Full Integration Test Suite
======================================================================

Base URL: http://localhost:8000/api/v1
Admin: admin@example.com
→ Getting authentication token... ✓

[... test execution ...]

======================================================================
  TEST SUMMARY
======================================================================

Total Tests: 35
✓ Passed: 35
✗ Failed: 0
Success Rate: 100.0%

======================================================================
  🎉 ALL TESTS PASSED! 🎉
======================================================================
```

## Prerequisites

1. **Backend server must be running**
   ```bash
   docker compose up -d
   ```

2. **Database must be initialized** with migrations applied

3. **Default superuser must exist**
   - Email: `admin@example.com`
   - Password: `changethis`

## Custom Configuration

### Different Port
```bash
python3 backend/tests/integration_scripts/test_address_full_integration.py 8001
```

### Different Credentials
Edit the script constants:
```python
ADMIN_EMAIL = "your-admin@example.com"
ADMIN_PASSWORD = "your-password"
```

## Troubleshooting

### Connection Refused
- Ensure backend is running: `docker compose ps`
- Check port: default is 8000

### Authentication Failed
- Verify superuser exists in database
- Check credentials match

### Tests Failing
- Check backend logs: `docker compose logs backend`
- Verify database migrations are up to date
- Ensure no stale test data conflicts

## Integration with CI/CD

Add to your CI pipeline:

```yaml
- name: Run Address API Integration Tests
  run: |
    python3 backend/tests/integration_scripts/test_address_full_integration.py
```

## Related Scripts

- `test_countries_api.sh` - Simple countries endpoint test
- `test_delete.py` - DELETE operations test
- See `README.md` for full documentation

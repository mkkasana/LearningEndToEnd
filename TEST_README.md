# API Testing

## Test Script

The `test-final.sh` script provides comprehensive testing of the clean architecture backend.

### Usage

```bash
./test-final.sh
```

### What It Tests

1. **Health Check** - Verifies backend is running
2. **Authentication** - Tests login and token generation
3. **List Users** - Tests user listing endpoint
4. **List Items** - Tests item listing endpoint
5. **Create Item** - Tests item creation
6. **Get Item by ID** - Tests item retrieval
7. **Update Item** - Tests item update
8. **Delete Item** - Tests item deletion

### Requirements

- Backend running at `http://localhost:8000`
- Admin user credentials: `admin@example.com` / `changethis`
- `curl` and `python3` installed

### Expected Output

```
========================================
  Final Clean Architecture Test
========================================

=== 1. Health Check ===
✓ PASS

=== 2. Login (Clean Architecture) ===
✓ PASS - Token: eyJ...

...

========================================
           Final Summary
========================================
Passed: 8
Failed: 0
Total:  8

✓✓✓ ALL TESTS PASSED! ✓✓✓
Legacy code removed successfully!
100% Clean Architecture!
```

### Exit Codes

- `0` - All tests passed
- `1` - One or more tests failed

### Architecture Verification

This test script verifies that:
- ✅ All endpoints use clean architecture (no legacy code)
- ✅ Services layer is working correctly
- ✅ Repositories layer is functioning
- ✅ Authentication and authorization work
- ✅ CRUD operations are successful
- ✅ No `/v2` prefix needed (legacy removed)

### Running with Docker

If backend is not running:

```bash
docker compose up -d
sleep 5  # Wait for backend to be healthy
./test-final.sh
```

### Troubleshooting

**Backend not responding:**
```bash
docker compose ps backend
docker compose logs backend
```

**Authentication fails:**
- Check if admin user exists in database
- Verify credentials in `.env` file

**Tests fail:**
- Check backend logs: `docker compose logs backend`
- Verify database is healthy: `docker compose ps db`
- Ensure no port conflicts on 8000

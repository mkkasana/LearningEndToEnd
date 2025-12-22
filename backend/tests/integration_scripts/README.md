# Integration Test Scripts

This directory contains shell scripts for manual integration testing of API endpoints.

## Purpose

These scripts are for:
- Quick manual testing during development
- Verifying API endpoints work end-to-end
- Testing authentication flows
- Validating API responses

**Note:** These are NOT automated tests. For automated tests, see `tests/api/`.

## Available Scripts

### test_countries_api.sh

Tests the countries metadata API endpoints.

**Usage:**
```bash
# Default port (8000)
./tests/integration_scripts/test_countries_api.sh

# Custom port
./tests/integration_scripts/test_countries_api.sh 8001
```

**What it tests:**
- GET /api/v1/metadata/address/countries
- Validates HTTP 200 response
- Checks JSON format
- Counts total countries returned

## Requirements

- Backend server must be running
- `curl` command available
- `python3` with json module (standard library)

## Adding New Scripts

When adding new integration test scripts:

1. Make them executable: `chmod +x script_name.sh`
2. Accept port as optional parameter
3. Include clear output (✅ success, ❌ error)
4. Test both success and error cases
5. Document in this README

## Example Script Template

```bash
#!/bin/bash

PORT=${1:-8000}
BASE_URL="http://localhost:${PORT}/api/v1"

echo "Testing [Feature Name] API"
echo "================================"

# Test 1: Success case
echo "Test 1: [Description]"
response=$(curl -s "${BASE_URL}/endpoint")
# ... validation logic

# Test 2: Error case
echo "Test 2: [Description]"
# ... test logic
```

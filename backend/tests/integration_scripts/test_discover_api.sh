#!/bin/bash

# Test script for the discover-family-members API endpoint
# Usage: ./test_discover_api.sh

echo "=== Testing Discover Family Members API ==="
echo ""

# Login and get token
echo "1. Logging in as testing11@gmail.com..."
TOKEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testing11@gmail.com&password=qweqweqwe")

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get access token"
    echo "Response: $TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Successfully logged in"
echo ""

# Call discover-family-members endpoint
echo "2. Calling /api/v1/person/discover-family-members..."
DISCOVER_RESPONSE=$(curl -s -X GET "http://localhost:8000/api/v1/person/discover-family-members" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo ""
echo "Response:"
echo "$DISCOVER_RESPONSE" | python3 -m json.tool

# Check if response is an array
if echo "$DISCOVER_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); sys.exit(0 if isinstance(data, list) else 1)" 2>/dev/null; then
    COUNT=$(echo "$DISCOVER_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
    echo ""
    echo "✅ API call successful! Found $COUNT potential family member(s)"
else
    echo ""
    echo "❌ API call failed or returned unexpected format"
fi

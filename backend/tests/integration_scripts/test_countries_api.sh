#!/bin/bash

# Test script for countries metadata API
# Usage: ./test_countries_api.sh [port]

PORT=${1:-8000}
BASE_URL="http://localhost:${PORT}/api/v1"

echo "Testing Countries Metadata API"
echo "================================"
echo ""
echo "Endpoint: ${BASE_URL}/metadata/address/countries"
echo ""

# Test the endpoint
echo "Making GET request..."
response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "${BASE_URL}/metadata/address/countries")

# Extract HTTP status
http_status=$(echo "$response" | grep "HTTP_STATUS" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_STATUS/d')

echo "HTTP Status: $http_status"
echo ""

if [ "$http_status" = "200" ]; then
    echo "✅ Success! API is working."
    echo ""
    echo "Response (first 3 countries):"
    echo "$body" | python3 -m json.tool | head -n 20
    echo ""
    echo "Total countries returned:"
    echo "$body" | python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data))"
else
    echo "❌ Error! API returned status $http_status"
    echo ""
    echo "Response:"
    echo "$body"
fi

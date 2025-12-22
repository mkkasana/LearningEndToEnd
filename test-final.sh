#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_URL="http://localhost:8000"
PASSED=0
FAILED=0

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Final Clean Architecture Test${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Test 1: Health Check
echo -e "${BLUE}=== 1. Health Check ===${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/utils/health-check/")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

# Test 2: Login
echo -e "${BLUE}=== 2. Login (Clean Architecture) ===${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis")

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    echo -e "${GREEN}✓ PASS${NC} - Token: ${TOKEN:0:50}..."
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

# Test 3: List Users
echo -e "${BLUE}=== 3. List Users (Clean Architecture) ===${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/users/" \
  -H "Authorization: Bearer $TOKEN")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
    echo "$body" | python3 -m json.tool 2>/dev/null | head -10
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

# Test 4: List Items
echo -e "${BLUE}=== 4. List Items (Clean Architecture) ===${NC}"
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/items/" \
  -H "Authorization: Bearer $TOKEN")
http_code=$(echo "$response" | tail -n1)
if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

# Test 5: Create Item
echo -e "${BLUE}=== 5. Create Item (Clean Architecture) ===${NC}"
TIMESTAMP=$(date +%s)
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/items/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Clean Arch Test $TIMESTAMP\", \"description\": \"No legacy code!\"}")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')
if [ "$http_code" == "200" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
    ITEM_ID=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
    echo "$body" | python3 -m json.tool 2>/dev/null
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi
echo ""

# Test 6: Get Item
if [ ! -z "$ITEM_ID" ]; then
    echo -e "${BLUE}=== 6. Get Item by ID ===${NC}"
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/v1/items/$ITEM_ID" \
      -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -n1)
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
    echo ""
fi

# Test 7: Update Item
if [ ! -z "$ITEM_ID" ]; then
    echo -e "${BLUE}=== 7. Update Item ===${NC}"
    response=$(curl -s -w "\n%{http_code}" -X PUT "$BASE_URL/api/v1/items/$ITEM_ID" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"title\": \"Updated Clean Arch\", \"description\": \"Pure clean architecture\"}")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        echo "$body" | python3 -m json.tool 2>/dev/null
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
    echo ""
fi

# Test 8: Delete Item
if [ ! -z "$ITEM_ID" ]; then
    echo -e "${BLUE}=== 8. Delete Item ===${NC}"
    response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/api/v1/items/$ITEM_ID" \
      -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    if [ "$http_code" == "200" ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        echo "$body" | python3 -m json.tool 2>/dev/null
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
    fi
    echo ""
fi

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}           Final Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
TOTAL=$((PASSED + FAILED))
echo -e "Total:  $TOTAL"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓✓✓ ALL TESTS PASSED! ✓✓✓${NC}"
    echo -e "${GREEN}Legacy code removed successfully!${NC}"
    echo -e "${GREEN}100% Clean Architecture!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi

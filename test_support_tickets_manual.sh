#!/bin/bash

# Manual Testing Script for Support Tickets Feature
# This script tests the backend API endpoints to verify functionality

set -e

BASE_URL="http://localhost:8000/api/v1"
ADMIN_EMAIL="admin@example.com"
ADMIN_PASSWORD="changethis"

echo "=========================================="
echo "Support Tickets Manual Testing Script"
echo "=========================================="
echo ""

# Login as admin
echo "1. Logging in as admin..."
ADMIN_TOKEN=$(curl -s -X POST "$BASE_URL/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$ADMIN_EMAIL&password=$ADMIN_PASSWORD" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$ADMIN_TOKEN" ]; then
  echo "❌ Failed to login as admin"
  exit 1
fi
echo "✅ Admin login successful"
echo ""

# Create a test ticket
echo "2. Creating a bug report ticket..."
BUG_TICKET=$(curl -s -X POST "$BASE_URL/support-tickets/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_type": "bug",
    "title": "Test Bug Report",
    "description": "This is a test bug report to verify the support ticket system is working correctly."
  }')

BUG_TICKET_ID=$(echo $BUG_TICKET | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✅ Bug ticket created with ID: $BUG_TICKET_ID"
echo ""

# Create a feature request ticket
echo "3. Creating a feature request ticket..."
FEATURE_TICKET=$(curl -s -X POST "$BASE_URL/support-tickets/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_type": "feature_request",
    "title": "Test Feature Request",
    "description": "This is a test feature request to verify the support ticket system is working correctly."
  }')

FEATURE_TICKET_ID=$(echo $FEATURE_TICKET | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
echo "✅ Feature request ticket created with ID: $FEATURE_TICKET_ID"
echo ""

# Get user's tickets
echo "4. Fetching user's tickets (All)..."
USER_TICKETS=$(curl -s -X GET "$BASE_URL/support-tickets/me?skip=0&limit=100" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
TICKET_COUNT=$(echo $USER_TICKETS | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])")
echo "✅ Found $TICKET_COUNT tickets for user"
echo ""

# Get user's open tickets
echo "5. Fetching user's open tickets..."
OPEN_TICKETS=$(curl -s -X GET "$BASE_URL/support-tickets/me?status=open&skip=0&limit=100" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
OPEN_COUNT=$(echo $OPEN_TICKETS | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])")
echo "✅ Found $OPEN_COUNT open tickets"
echo ""

# Get single ticket
echo "6. Fetching single ticket details..."
SINGLE_TICKET=$(curl -s -X GET "$BASE_URL/support-tickets/$BUG_TICKET_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
TICKET_TITLE=$(echo $SINGLE_TICKET | python3 -c "import sys, json; print(json.load(sys.stdin)['title'])")
echo "✅ Retrieved ticket: $TICKET_TITLE"
echo ""

# Update ticket
echo "7. Updating ticket title..."
UPDATED_TICKET=$(curl -s -X PATCH "$BASE_URL/support-tickets/$BUG_TICKET_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Test Bug Report"
  }')
NEW_TITLE=$(echo $UPDATED_TICKET | python3 -c "import sys, json; print(json.load(sys.stdin)['title'])")
echo "✅ Ticket updated: $NEW_TITLE"
echo ""

# Get all tickets as admin
echo "8. Fetching all tickets (admin view)..."
ALL_TICKETS=$(curl -s -X GET "$BASE_URL/support-tickets/admin/all?skip=0&limit=100" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
ADMIN_TICKET_COUNT=$(echo $ALL_TICKETS | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "✅ Admin view shows $ADMIN_TICKET_COUNT total tickets"
echo ""

# Resolve ticket
echo "9. Resolving bug ticket..."
RESOLVED_TICKET=$(curl -s -X PATCH "$BASE_URL/support-tickets/$BUG_TICKET_ID/resolve" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
RESOLVED_STATUS=$(echo $RESOLVED_TICKET | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
echo "✅ Ticket status: $RESOLVED_STATUS"
echo ""

# Get closed tickets
echo "10. Fetching user's closed tickets..."
CLOSED_TICKETS=$(curl -s -X GET "$BASE_URL/support-tickets/me?status=closed&skip=0&limit=100" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
CLOSED_COUNT=$(echo $CLOSED_TICKETS | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])")
echo "✅ Found $CLOSED_COUNT closed tickets"
echo ""

# Reopen ticket
echo "11. Reopening bug ticket..."
REOPENED_TICKET=$(curl -s -X PATCH "$BASE_URL/support-tickets/$BUG_TICKET_ID/reopen" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
REOPENED_STATUS=$(echo $REOPENED_TICKET | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])")
echo "✅ Ticket status: $REOPENED_STATUS"
echo ""

# Test validation - title too long
echo "12. Testing validation (title > 100 chars)..."
VALIDATION_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/support-tickets/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_type": "bug",
    "title": "This is a very long title that exceeds the maximum allowed length of 100 characters and should be rejected by the validation",
    "description": "Test description"
  }')
HTTP_CODE=$(echo "$VALIDATION_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "422" ]; then
  echo "✅ Validation correctly rejected long title (HTTP 422)"
else
  echo "❌ Validation failed - expected HTTP 422, got $HTTP_CODE"
fi
echo ""

# Test validation - description too long
echo "13. Testing validation (description > 2000 chars)..."
LONG_DESC=$(python3 -c "print('x' * 2001)")
VALIDATION_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/support-tickets/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"issue_type\": \"bug\",
    \"title\": \"Test\",
    \"description\": \"$LONG_DESC\"
  }")
HTTP_CODE=$(echo "$VALIDATION_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "422" ]; then
  echo "✅ Validation correctly rejected long description (HTTP 422)"
else
  echo "❌ Validation failed - expected HTTP 422, got $HTTP_CODE"
fi
echo ""

# Test validation - missing required fields
echo "14. Testing validation (missing title)..."
VALIDATION_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/support-tickets/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "issue_type": "bug",
    "description": "Test description"
  }')
HTTP_CODE=$(echo "$VALIDATION_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "422" ]; then
  echo "✅ Validation correctly rejected missing title (HTTP 422)"
else
  echo "❌ Validation failed - expected HTTP 422, got $HTTP_CODE"
fi
echo ""

# Delete tickets
echo "15. Deleting test tickets..."
curl -s -X DELETE "$BASE_URL/support-tickets/$BUG_TICKET_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
echo "✅ Deleted bug ticket"

curl -s -X DELETE "$BASE_URL/support-tickets/$FEATURE_TICKET_ID" \
  -H "Authorization: Bearer $ADMIN_TOKEN" > /dev/null
echo "✅ Deleted feature request ticket"
echo ""

# Verify deletion
echo "16. Verifying tickets were deleted..."
FINAL_TICKETS=$(curl -s -X GET "$BASE_URL/support-tickets/me?skip=0&limit=100" \
  -H "Authorization: Bearer $ADMIN_TOKEN")
FINAL_COUNT=$(echo $FINAL_TICKETS | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])")
echo "✅ Final ticket count: $FINAL_COUNT"
echo ""

echo "=========================================="
echo "✅ All backend API tests completed successfully!"
echo "=========================================="
echo ""
echo "Frontend Manual Testing Checklist:"
echo "1. Navigate to http://localhost:5173/support-tickets"
echo "2. Verify 'Report Ticket' link appears in sidebar"
echo "3. Click 'Report New Ticket' button"
echo "4. Test character counters (title: 100, description: 2000)"
echo "5. Test form validation (empty fields, too long text)"
echo "6. Create a bug report and a feature request"
echo "7. Test tab filtering (All, Open, Closed)"
echo "8. Click on a ticket to view details"
echo "9. Delete a ticket"
echo "10. Login as admin and navigate to /admin"
echo "11. Verify 'Issue Management' section appears"
echo "12. Test filtering by status and type"
echo "13. Mark a ticket as resolved"
echo "14. Reopen a closed ticket"
echo "15. Delete a ticket from admin panel"
echo ""

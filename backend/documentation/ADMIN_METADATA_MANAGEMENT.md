# Admin Metadata Management Guide

Complete guide for superusers to manage Address and Religion metadata using Swagger UI.

## 🎯 Quick Start

### 1. Access Swagger UI

Open your browser and navigate to:
```
http://localhost:8000/docs
```

### 2. Authenticate as Superuser

1. Click the **"Authorize"** button (top right, lock icon)
2. In the popup, you'll see two options:
   - **OAuth2PasswordBearer (OAuth2, password)**
   - Click on it

3. Enter credentials:
   - **username:** `admin@example.com`
   - **password:** `changethis`
   - **client_id:** (leave empty)
   - **client_secret:** (leave empty)

4. Click **"Authorize"**
5. Click **"Close"**

You're now authenticated! All protected endpoints will use your token automatically.

## 📍 Address Metadata Management

### Available Endpoints

All address endpoints are under the **`address-metadata`** tag.

#### Hierarchy
```
Country → State → District → Sub-District → Locality
```

### Managing Countries

#### View All Countries (Public)
- **Endpoint:** `GET /api/v1/metadata/address/countries`
- **Auth:** None required
- **Returns:** List of active countries

**Steps:**
1. Find `GET /api/v1/metadata/address/countries`
2. Click "Try it out"
3. Click "Execute"
4. See response below

#### View Country Details
- **Endpoint:** `GET /api/v1/metadata/address/countries/{country_id}`
- **Auth:** None required

**Steps:**
1. Copy a country ID from the list
2. Find `GET /api/v1/metadata/address/countries/{country_id}`
3. Click "Try it out"
4. Paste the ID in `country_id` field
5. Click "Execute"

#### Create New Country
- **Endpoint:** `POST /api/v1/metadata/address/countries`
- **Auth:** Superuser required ✅

**Steps:**
1. Find `POST /api/v1/metadata/address/countries`
2. Click "Try it out"
3. Edit the request body:
```json
{
  "name": "New Country Name",
  "code": "NCN",
  "is_active": true
}
```
4. Click "Execute"
5. Check response for the created country with ID

**Validation:**
- `name`: Required, max 255 characters, must be unique
- `code`: Required, 3 characters (ISO code), must be unique
- `is_active`: Optional, defaults to true

#### Update Country
- **Endpoint:** `PATCH /api/v1/metadata/address/countries/{country_id}`
- **Auth:** Superuser required ✅

**Steps:**
1. Find `PATCH /api/v1/metadata/address/countries/{country_id}`
2. Click "Try it out"
3. Enter the country ID
4. Edit request body (all fields optional):
```json
{
  "name": "Updated Name",
  "is_active": false
}
```
5. Click "Execute"

#### Delete Country
- **Endpoint:** `DELETE /api/v1/metadata/address/countries/{country_id}`
- **Auth:** Superuser required ✅

**Steps:**
1. Find `DELETE /api/v1/metadata/address/countries/{country_id}`
2. Click "Try it out"
3. Enter the country ID
4. Click "Execute"
5. Confirm deletion in response

⚠️ **Warning:** Deleting a country will cascade delete all related states, districts, sub-districts, and localities!

### Managing States

#### View States for a Country
- **Endpoint:** `GET /api/v1/metadata/address/country/{country_id}/states`
- **Auth:** None required

**Steps:**
1. Get a country ID
2. Find `GET /api/v1/metadata/address/country/{country_id}/states`
3. Click "Try it out"
4. Enter the country ID
5. Click "Execute"

#### Create New State
- **Endpoint:** `POST /api/v1/metadata/address/states`
- **Auth:** Superuser required ✅

**Request Body:**
```json
{
  "name": "California",
  "code": "CA",
  "country_id": "uuid-of-country",
  "is_active": true
}
```

**Validation:**
- `country_id`: Must exist
- `code`: Must be unique within the same country

#### Update/Delete State
Same pattern as countries, using state endpoints.

### Managing Districts, Sub-Districts, Localities

Follow the same pattern:
1. **Districts** belong to States
2. **Sub-Districts** belong to Districts
3. **Localities** belong to Sub-Districts

Each level has the same 5 operations:
- GET list (by parent)
- GET detail (by ID)
- POST create
- PATCH update
- DELETE delete

## 🕉️ Religion Metadata Management

### Available Endpoints

All religion endpoints are under the **`religion-metadata`** tag.

#### Hierarchy
```
Religion → Category → Sub-Category
```

### Managing Religions

#### View All Religions
- **Endpoint:** `GET /api/v1/metadata/religion/religions`
- **Auth:** None required

#### Create New Religion
- **Endpoint:** `POST /api/v1/metadata/religion/religions`
- **Auth:** Superuser required ✅

**Request Body:**
```json
{
  "name": "Hinduism",
  "code": "HIN",
  "description": "One of the world's oldest religions",
  "is_active": true
}
```

**Fields:**
- `name`: Required, max 255 characters
- `code`: Required, max 10 characters, must be unique
- `description`: Optional, max 500 characters
- `is_active`: Optional, defaults to true

### Managing Categories

Categories represent:
- **Castes** for Hinduism
- **Sects** for Islam
- **Denominations** for Christianity
- **Schools** for Buddhism

#### View Categories for a Religion
- **Endpoint:** `GET /api/v1/metadata/religion/religion/{religion_id}/categories`

#### Create New Category
- **Endpoint:** `POST /api/v1/metadata/religion/categories`
- **Auth:** Superuser required ✅

**Request Body:**
```json
{
  "name": "Brahmin",
  "code": "BRM",
  "religion_id": "uuid-of-religion",
  "description": "Priestly caste in Hinduism",
  "is_active": true
}
```

### Managing Sub-Categories

Sub-categories represent:
- **Sub-castes** for Hindu castes
- **Sub-sects** for Islamic sects
- **Sub-denominations** for Christian denominations
- **Traditions** for Buddhist schools

#### View Sub-Categories for a Category
- **Endpoint:** `GET /api/v1/metadata/religion/category/{category_id}/sub-categories`

#### Create New Sub-Category
- **Endpoint:** `POST /api/v1/metadata/religion/sub-categories`
- **Auth:** Superuser required ✅

**Request Body:**
```json
{
  "name": "Iyer",
  "code": "IYR",
  "category_id": "uuid-of-category",
  "description": "Tamil Brahmin sub-caste",
  "is_active": true
}
```

## 💡 Best Practices

### 1. Test Before Production
Use the "Try it out" feature to test operations before implementing in your app.

### 2. Check Responses
Always review the response to ensure the operation succeeded:
- **200 OK** - Success
- **401 Unauthorized** - Need to authenticate
- **404 Not Found** - Resource doesn't exist
- **400 Bad Request** - Validation error (check error message)

### 3. Hierarchical Order
Always create in order:
1. Create parent first (e.g., Country)
2. Then create children (e.g., States)
3. Copy the parent's ID for the child's foreign key

### 4. Deactivate Instead of Delete
Instead of deleting, consider setting `is_active: false`:
```json
{
  "is_active": false
}
```
This preserves data integrity and historical records.

### 5. Use Meaningful Codes
Codes should be:
- Short (3-10 characters)
- Uppercase
- Standardized (e.g., ISO codes for countries)
- Unique within scope

## 🔍 Common Tasks

### Task 1: Add a New Country with States

1. **Create Country:**
```json
POST /api/v1/metadata/address/countries
{
  "name": "Canada",
  "code": "CAN",
  "is_active": true
}
```
→ Copy the returned `id`

2. **Create States:**
```json
POST /api/v1/metadata/address/states
{
  "name": "Ontario",
  "code": "ON",
  "country_id": "canada-id-here",
  "is_active": true
}
```

Repeat for other provinces.

### Task 2: Add a Religion with Categories

1. **Create Religion:**
```json
POST /api/v1/metadata/religion/religions
{
  "name": "Buddhism",
  "code": "BUD",
  "description": "Ancient Indian religion founded by Buddha",
  "is_active": true
}
```
→ Copy the returned `id`

2. **Create Categories (Schools):**
```json
POST /api/v1/metadata/religion/categories
{
  "name": "Theravada",
  "code": "THER",
  "religion_id": "buddhism-id-here",
  "description": "School of the Elders",
  "is_active": true
}
```

3. **Create Sub-Categories (Traditions):**
```json
POST /api/v1/metadata/religion/sub-categories
{
  "name": "Thai Forest Tradition",
  "code": "THFOR",
  "category_id": "theravada-id-here",
  "description": "Meditation-focused tradition from Thailand",
  "is_active": true
}
```

### Task 3: Update Multiple Records

To deactivate old records:
1. Find the record ID using GET endpoint
2. Use PATCH with `{"is_active": false}`
3. Repeat for each record

### Task 4: View Hierarchy

To see the full hierarchy:
1. GET all religions
2. For each religion, GET its categories
3. For each category, GET its sub-categories

## 🚨 Troubleshooting

### "Not authenticated" Error
- Click "Authorize" button again
- Re-enter credentials
- Make sure you're using superuser account

### "Already exists" Error
- Code must be unique
- Try a different code
- Or update the existing record instead

### "Not found" Error
- Check the ID is correct
- Ensure parent record exists
- Verify you're using the right endpoint

### Can't See New Records in List
- Check `is_active` is `true`
- List endpoints only show active records
- Use GET by ID to see inactive records

## 📊 Response Formats

### List Endpoints (GET collections)
Return simplified camelCase format:
```json
[
  {"countryId": "uuid", "countryName": "India"},
  {"religionId": "uuid", "religionName": "Hinduism"}
]
```

### Detail Endpoints (GET by ID, POST, PATCH)
Return full object with all fields:
```json
{
  "id": "uuid",
  "name": "India",
  "code": "IND",
  "is_active": true
}
```

## 🎓 Advanced: Using cURL

If you prefer command line:

```bash
# Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=changethis" | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Create country
curl -X POST "http://localhost:8000/api/v1/metadata/address/countries" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Country", "code": "TST", "is_active": true}'
```

## 📝 Summary

**For Admin Metadata Management:**
1. ✅ **Use Swagger UI** - Perfect for technical admins
2. ✅ **No custom UI needed** - Everything is already there
3. ✅ **Full CRUD operations** - All endpoints available
4. ✅ **Authentication built-in** - Secure by default
5. ✅ **Interactive testing** - Try before you commit

**When to Build Custom UI:**
- Non-technical users need access
- Bulk operations required
- CSV/Excel import needed
- Custom workflows required
- Better visualization needed

For now, **Swagger UI is the recommended approach** for superuser metadata management! 🎉

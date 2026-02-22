# Swagger UI Quick Start for Admins

Visual guide to managing metadata using Swagger UI.

## 🚀 Step-by-Step Guide

### Step 1: Open Swagger UI

Navigate to: **http://localhost:8000/docs**

You'll see the interactive API documentation with all available endpoints organized by tags.

### Step 2: Authenticate

1. **Click the "Authorize" button** (green lock icon, top right)

2. **Enter credentials:**
   ```
   username: admin@example.com
   password: changethis
   ```

3. **Click "Authorize"** then **"Close"**

✅ You're now authenticated! The lock icon will show as closed.

### Step 3: Find Your Endpoint

Scroll down to find the section you need:

- **`address-metadata`** - For managing addresses (Countries, States, Districts, etc.)
- **`religion-metadata`** - For managing religions (Religions, Categories, Sub-Categories)

### Step 4: Try an Operation

Let's create a new country as an example:

#### A. Expand the Endpoint
Click on **`POST /api/v1/metadata/address/countries`**

#### B. Click "Try it out"
This enables the form for editing

#### C. Edit the Request Body
You'll see a JSON template:
```json
{
  "name": "string",
  "code": "str",
  "is_active": true
}
```

Change it to:
```json
{
  "name": "New Zealand",
  "code": "NZL",
  "is_active": true
}
```

#### D. Click "Execute"
The request will be sent to the server

#### E. Check the Response
Scroll down to see:
- **Response Code:** `200` (success!)
- **Response Body:** The created country with its ID
```json
{
  "id": "uuid-here",
  "name": "New Zealand",
  "code": "NZL",
  "is_active": true
}
```

#### F. Copy the ID
You'll need this ID to create states for this country!

## 📋 Common Operations

### View All Records (GET List)

**Example: View all countries**

1. Find `GET /api/v1/metadata/address/countries`
2. Click "Try it out"
3. Click "Execute"
4. See the list in Response Body

**No authentication needed** for GET operations!

### View Single Record (GET Detail)

**Example: View a specific country**

1. Copy a country ID from the list
2. Find `GET /api/v1/metadata/address/countries/{country_id}`
3. Click "Try it out"
4. Paste the ID in the `country_id` field
5. Click "Execute"

### Create Record (POST)

**Example: Create a state**

1. First, get a country ID
2. Find `POST /api/v1/metadata/address/states`
3. Click "Try it out"
4. Edit the request body:
```json
{
  "name": "Auckland",
  "code": "AUK",
  "country_id": "paste-country-id-here",
  "is_active": true
}
```
5. Click "Execute"

**Authentication required!** Make sure you're authorized.

### Update Record (PATCH)

**Example: Rename a country**

1. Get the country ID
2. Find `PATCH /api/v1/metadata/address/countries/{country_id}`
3. Click "Try it out"
4. Enter the country ID
5. Edit request body (only include fields to update):
```json
{
  "name": "Aotearoa New Zealand"
}
```
6. Click "Execute"

### Delete Record (DELETE)

**Example: Delete a country**

1. Get the country ID
2. Find `DELETE /api/v1/metadata/address/countries/{country_id}`
3. Click "Try it out"
4. Enter the country ID
5. Click "Execute"
6. Confirm in response: `{"message": "Country deleted successfully"}`

⚠️ **Warning:** This will cascade delete all related data!

## 🎯 Real-World Workflow

### Workflow 1: Add Complete Address Hierarchy

**Goal:** Add India with states and districts

```
1. Create Country: India (IND)
   ↓ Copy country_id
   
2. Create State: Maharashtra (MH)
   ↓ Use country_id, copy state_id
   
3. Create District: Mumbai (MUM)
   ↓ Use state_id, copy district_id
   
4. Create Sub-District: Mumbai City (MUMC)
   ↓ Use district_id, copy sub_district_id
   
5. Create Locality: Andheri (AND)
   ↓ Use sub_district_id
```

**In Swagger:**

1. **POST** `/api/v1/metadata/address/countries`
   ```json
   {"name": "India", "code": "IND", "is_active": true}
   ```
   → Copy `id` from response

2. **POST** `/api/v1/metadata/address/states`
   ```json
   {
     "name": "Maharashtra",
     "code": "MH",
     "country_id": "india-id-here",
     "is_active": true
   }
   ```
   → Copy `id` from response

3. **POST** `/api/v1/metadata/address/districts`
   ```json
   {
     "name": "Mumbai",
     "code": "MUM",
     "state_id": "maharashtra-id-here",
     "is_active": true
   }
   ```
   → Continue pattern...

### Workflow 2: Add Religion Hierarchy

**Goal:** Add Hinduism with castes and sub-castes

```
1. Create Religion: Hinduism (HIN)
   ↓ Copy religion_id
   
2. Create Category: Brahmin (BRM)
   ↓ Use religion_id, copy category_id
   
3. Create Sub-Category: Iyer (IYR)
   ↓ Use category_id
```

**In Swagger:**

1. **POST** `/api/v1/metadata/religion/religions`
   ```json
   {
     "name": "Hinduism",
     "code": "HIN",
     "description": "Ancient Indian religion",
     "is_active": true
   }
   ```

2. **POST** `/api/v1/metadata/religion/categories`
   ```json
   {
     "name": "Brahmin",
     "code": "BRM",
     "religion_id": "hinduism-id-here",
     "description": "Priestly caste",
     "is_active": true
   }
   ```

3. **POST** `/api/v1/metadata/religion/sub-categories`
   ```json
   {
     "name": "Iyer",
     "code": "IYR",
     "category_id": "brahmin-id-here",
     "description": "Tamil Brahmin sub-caste",
     "is_active": true
   }
   ```

## 💡 Pro Tips

### Tip 1: Use the Schema Section
Each endpoint shows:
- **Request body schema** - What fields are required
- **Response schema** - What you'll get back
- **Example values** - Sample data

### Tip 2: Check Response Codes
- **200** - Success
- **401** - Not authenticated (click Authorize)
- **404** - Resource not found (check ID)
- **400** - Validation error (read error message)

### Tip 3: Copy-Paste IDs
Keep a text file open to copy/paste IDs as you create hierarchies.

### Tip 4: Test Before Committing
Use Swagger to test your data structure before building frontend forms.

### Tip 5: Deactivate Instead of Delete
Set `is_active: false` instead of deleting to preserve data integrity.

## 🔍 Finding Specific Data

### Find a Country by Name
1. **GET** `/api/v1/metadata/address/countries`
2. Search the response for your country
3. Copy its `countryId`

### Find States for a Country
1. Get the country ID
2. **GET** `/api/v1/metadata/address/country/{country_id}/states`
3. See all states for that country

### Find Categories for a Religion
1. Get the religion ID
2. **GET** `/api/v1/metadata/religion/religion/{religion_id}/categories`
3. See all categories for that religion

## 🎨 Swagger UI Features

### Schemas Section (Bottom)
Shows all data models with field types and descriptions.

### Models Tab
Click on any schema to see its structure.

### Try It Out
Makes the form editable so you can test.

### Execute
Sends the actual request to the server.

### Clear
Resets the form to default values.

### Download
Download the OpenAPI specification.

## 📱 Alternative: ReDoc

For read-only documentation with better formatting:

**http://localhost:8000/redoc**

- Better for reading
- Not interactive
- Good for sharing with team

## ✅ Checklist for Admins

Before managing metadata:
- [ ] Swagger UI is accessible at `/docs`
- [ ] You have superuser credentials
- [ ] You've clicked "Authorize" and entered credentials
- [ ] You understand the hierarchy (parent → child)
- [ ] You have a plan for codes (standardized, unique)

When creating records:
- [ ] Create parent first
- [ ] Copy parent ID
- [ ] Use parent ID in child's foreign key field
- [ ] Verify creation in response
- [ ] Test by fetching the record

## 🎓 Summary

**Swagger UI is perfect for:**
- ✅ Technical admins
- ✅ API testing
- ✅ Quick CRUD operations
- ✅ Understanding API structure
- ✅ No extra development needed

**Consider custom UI if you need:**
- ❌ Non-technical user access
- ❌ Bulk operations
- ❌ CSV import/export
- ❌ Advanced search/filter
- ❌ Custom workflows

For most admin tasks, **Swagger UI is sufficient and recommended!** 🚀

# Person Metadata API

## Overview

The Person Metadata API provides endpoints to manage additional person details such as profile images and biographies. Each person can have one metadata record that stores extensible information about their profile.

## Table Structure

```sql
CREATE TABLE person_metadata (
    id UUID PRIMARY KEY,
    person_id UUID NOT NULL UNIQUE REFERENCES person(user_id),
    profile_image_url VARCHAR(500),
    bio TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

## Features

- **One-to-One Relationship**: Each person can have only one metadata record
- **Profile Image**: Store URL to person's profile image
- **Biography**: Store person's bio/description
- **Extensible**: Can be expanded with additional fields in the future
- **Temporal Tracking**: Tracks creation and update timestamps

## API Endpoints

### Get Person Metadata
```http
GET /api/v1/person/me/metadata
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "person_id": "uuid",
  "profile_image_url": "https://example.com/profile.jpg",
  "bio": "This is my biography",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### Create Person Metadata
```http
POST /api/v1/person/me/metadata
Authorization: Bearer <token>
Content-Type: application/json

{
  "profile_image_url": "https://example.com/profile.jpg",
  "bio": "This is my biography"
}
```

**Notes:**
- Both fields are optional
- Returns 400 if metadata already exists for the person
- Requires person profile to exist first

### Update Person Metadata
```http
PATCH /api/v1/person/me/metadata
Authorization: Bearer <token>
Content-Type: application/json

{
  "profile_image_url": "https://example.com/new-profile.jpg",
  "bio": "Updated biography"
}
```

**Notes:**
- All fields are optional (partial updates supported)
- Set field to `null` to clear it
- Returns 404 if metadata doesn't exist

### Delete Person Metadata
```http
DELETE /api/v1/person/me/metadata
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Person metadata deleted successfully"
}
```

## Validation Rules

1. **Unique Constraint**: Only one metadata record per person
2. **Profile Image URL**: Maximum 500 characters
3. **Bio**: No length limit (TEXT field)
4. **Person Required**: Person profile must exist before creating metadata
5. **Authentication**: All endpoints require valid JWT token

## Usage Examples

### Complete Profile Setup Flow

```bash
# 1. Create person profile
curl -X POST http://localhost:8000/api/v1/person/me \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "uuid",
    "first_name": "John",
    "last_name": "Doe",
    "gender_id": "uuid",
    "date_of_birth": "1990-01-01"
  }'

# 2. Add metadata
curl -X POST http://localhost:8000/api/v1/person/me/metadata \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_image_url": "https://example.com/john-doe.jpg",
    "bio": "Software engineer passionate about clean code"
  }'

# 3. Update profile image
curl -X PATCH http://localhost:8000/api/v1/person/me/metadata \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_image_url": "https://example.com/john-doe-new.jpg"
  }'

# 4. Clear bio
curl -X PATCH http://localhost:8000/api/v1/person/me/metadata \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "bio": null
  }'
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Person metadata already exists"
}
```

### 404 Not Found
```json
{
  "detail": "Person profile not found"
}
```
or
```json
{
  "detail": "Person metadata not found"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

## Testing

Run the integration tests:
```bash
python3 backend/tests/integration_scripts/test_person_metadata_crud.py
```

## Future Enhancements

Potential fields to add:
- `social_media_links` (JSONB): Store social media profiles
- `preferences` (JSONB): User preferences and settings
- `custom_fields` (JSONB): Extensible custom data
- `profile_visibility` (ENUM): Public/private/friends-only
- `last_active_at` (TIMESTAMP): Track user activity

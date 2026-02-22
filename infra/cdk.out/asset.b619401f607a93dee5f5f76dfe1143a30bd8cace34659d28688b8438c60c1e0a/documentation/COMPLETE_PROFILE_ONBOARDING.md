# Complete Profile Onboarding Flow

## Overview
Complete onboarding flow requiring users to fill in personal information, address, and religion details before accessing the main application.

## Flow Steps

### 1. User Signup
- User registers with email, password, and basic personal info (first name, middle name, last name, gender, date of birth)
- Backend automatically creates both `User` and `Person` records
- User is redirected to `/complete-profile`

### 2. Profile Completion Page (`/complete-profile`)
Shows three sections with completion status:

#### ✅ Personal Information
- Automatically completed during signup
- Shows green checkmark and "Complete" status

#### 📍 Address Information
- User clicks "Add Address" button
- Opens `AddAddressDialog` with cascading dropdowns:
  1. **Country** (required)
  2. **State** (optional, loads based on country)
  3. **District** (optional, loads based on state)
  4. **Sub-District** (optional, loads based on district)
  5. **Locality** (optional, loads based on sub-district)
  6. **Address Line** (optional text field)
  7. **Start Date** (required)
- Saves to `person_address` table
- Shows green checkmark after completion

#### 🕉️ Religion Information
- User clicks "Add Religion" button
- Opens `AddReligionDialog` with cascading dropdowns:
  1. **Religion** (required) - e.g., Hinduism, Islam, Christianity, Buddhism, etc.
  2. **Category** (optional, loads based on religion) - e.g., Vaishnavism, Sunni, Catholic
  3. **Sub-Category** (optional, loads based on category) - e.g., ISKCON, Hanafi
- Saves to `person_religion` table
- Shows green checkmark after completion

### 3. Profile Complete
- Once all three sections are complete, "Continue to Dashboard" button appears
- User can access the main application

## Technical Implementation

### Backend

#### API Endpoints
```
GET  /api/v1/profile/completion-status  - Check profile completion
POST /api/v1/person/me/addresses        - Add address
GET  /api/v1/person/me/addresses        - Get addresses
POST /api/v1/person-religion/           - Add religion
GET  /api/v1/person-religion/me         - Get religion
PUT  /api/v1/person-religion/me         - Update religion
DELETE /api/v1/person-religion/me       - Delete religion
```

#### Metadata Endpoints
```
GET /api/v1/metadata/address/countries
GET /api/v1/metadata/address/countries/{id}/states
GET /api/v1/metadata/address/states/{id}/districts
GET /api/v1/metadata/address/districts/{id}/sub-districts
GET /api/v1/metadata/address/sub-districts/{id}/localities

GET /api/v1/metadata/religion/religions
GET /api/v1/metadata/religion/religion/{id}/categories
GET /api/v1/metadata/religion/category/{id}/sub-categories
```

#### Profile Completion Logic
```python
class ProfileService:
    def check_profile_completion(self, user_id: UUID) -> ProfileCompletionStatus:
        has_person = person_exists(user_id)
        has_address = address_exists(user_id)
        has_religion = religion_exists(user_id)
        
        is_complete = has_person and has_address and has_religion
        
        return ProfileCompletionStatus(
            is_complete=is_complete,
            has_person=has_person,
            has_address=has_address,
            has_religion=has_religion,
            missing_fields=[...]
        )
```

### Frontend

#### Components
- `frontend/src/routes/complete-profile.tsx` - Main onboarding page
- `frontend/src/components/Profile/AddAddressDialog.tsx` - Address form with cascading dropdowns
- `frontend/src/components/Profile/AddReligionDialog.tsx` - Religion form with cascading dropdowns

#### State Management
- Uses `@tanstack/react-query` for API calls and caching
- Cascading dropdowns implemented with local state
- Auto-refetch profile status after each completion

#### UI/UX
- Clean card-based layout
- Visual indicators (checkmarks) for completed sections
- Disabled/enabled states for dependent dropdowns
- Loading states during API calls
- Toast notifications for success/error

## Database Schema

### person_religion Table
```sql
CREATE TABLE person_religion (
    id UUID PRIMARY KEY,
    person_id UUID UNIQUE REFERENCES person(user_id),
    religion_id UUID REFERENCES religion(id),
    religion_category_id UUID REFERENCES religion_category(id),
    religion_sub_category_id UUID REFERENCES religion_sub_category(id),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Constraints
- One religion per person (enforced by unique constraint on `person_id`)
- Religion is required, category and sub-category are optional
- Cascading relationships ensure data integrity

## Testing

### Integration Tests
```bash
# Test profile completion flow
python backend/tests/integration_scripts/test_profile_completion.py

# Test person religion CRUD
python backend/tests/integration_scripts/test_person_religion_crud.py
```

### Test Coverage
- ✅ User signup creates person record
- ✅ Profile incomplete without address
- ✅ Profile incomplete without religion
- ✅ Profile complete after adding both
- ✅ Religion CRUD operations
- ✅ Cascading dropdown data loading
- ✅ Duplicate prevention
- ✅ Profile status API

## Seed Data

### Religions Seeded
- Hinduism (with Vaishnavism → ISKCON)
- Islam (with Sunni)
- Christianity (with Catholic)
- Sikhism
- Buddhism
- Jainism
- Other

### Seed Command
```bash
docker compose exec backend python -c "import sys; sys.path.insert(0, '/app'); ..."
```

## User Experience Flow

1. **New User Signs Up**
   - Fills registration form
   - Redirected to `/complete-profile`

2. **Sees Completion Checklist**
   - ✅ Personal Info (auto-completed)
   - ⭕ Address (needs action)
   - ⭕ Religion (needs action)

3. **Adds Address**
   - Clicks "Add Address"
   - Selects country, state, district, etc.
   - Submits form
   - ✅ Address marked complete

4. **Adds Religion**
   - Clicks "Add Religion"
   - Selects religion, optionally category and sub-category
   - Submits form
   - ✅ Religion marked complete

5. **Profile Complete**
   - All sections show green checkmarks
   - "Continue to Dashboard" button appears
   - User can access main application

## Future Enhancements

- [ ] Allow editing of address and religion after initial setup
- [ ] Support multiple addresses (home, work, etc.)
- [ ] Add profile completion progress bar
- [ ] Email verification step
- [ ] Phone number verification
- [ ] Profile photo upload
- [ ] Additional demographic fields (caste, occupation, education)

# Design Document: Person Marital Status

## Overview

This design adds marital status tracking to the Person model. The feature includes a new MaritalStatus enum stored directly on the Person table, updates to the profile completion flow to collect this information, and API endpoints for managing marital status.

## Architecture

The feature follows the existing patterns in the codebase:
- Enum stored in `backend/app/enums/`
- Direct field on Person model (similar to `gender_id`)
- Profile completion check in ProfileService
- Frontend dialog component for editing (similar to AddReligionDialog)

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend                                  │
│  ┌─────────────────┐    ┌──────────────────────────────────┐   │
│  │ complete-profile │───▶│ EditMaritalStatusDialog          │   │
│  │ (updated step)   │    │ (new component)                  │   │
│  └─────────────────┘    └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Backend API                               │
│  ┌─────────────────┐    ┌──────────────────────────────────┐   │
│  │ GET /profile/   │    │ PATCH /persons/{id}              │   │
│  │ completion-status│    │ (existing, add marital_status)   │   │
│  └─────────────────┘    └──────────────────────────────────┘   │
│  ┌─────────────────┐                                            │
│  │ GET /metadata/  │                                            │
│  │ marital-statuses│                                            │
│  └─────────────────┘                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Database                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ person table                                             │   │
│  │ + marital_status VARCHAR NOT NULL DEFAULT 'UNKNOWN'      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Backend Components

#### 1. MaritalStatus Enum

Location: `backend/app/enums/marital_status.py`

```python
from enum import Enum

class MaritalStatus(str, Enum):
    """Marital status options for a person."""
    
    UNKNOWN = "unknown"
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    SEPARATED = "separated"
    
    @property
    def label(self) -> str:
        """Get human-readable label."""
        return _MARITAL_STATUS_LABELS.get(self.value, self.value.title())
    
    @classmethod
    def get_selectable_options(cls) -> list["MaritalStatus"]:
        """Get options that users can select (excludes UNKNOWN)."""
        return [status for status in cls if status != cls.UNKNOWN]

_MARITAL_STATUS_LABELS = {
    "unknown": "Unknown",
    "single": "Single",
    "married": "Married",
    "divorced": "Divorced",
    "widowed": "Widowed",
    "separated": "Separated",
}
```

#### 2. Person Model Update

Location: `backend/app/db_models/person/person.py`

Add field:
```python
from app.enums.marital_status import MaritalStatus

marital_status: MaritalStatus = Field(
    default=MaritalStatus.UNKNOWN,
    description="Person's marital status"
)
```

#### 3. ProfileService Update

Location: `backend/app/services/profile_service.py`

Update `check_profile_completion` method to include marital status check:
```python
def check_profile_completion(self, user_id: uuid.UUID) -> ProfileCompletionStatus:
    # ... existing checks ...
    
    # Check marital status
    has_marital_status = False
    if has_person and person is not None:
        has_marital_status = person.marital_status != MaritalStatus.UNKNOWN
        if not has_marital_status:
            missing_fields.append("marital_status")
    else:
        missing_fields.append("marital_status")
    
    is_complete = has_person and has_address and has_religion and has_marital_status
    
    return ProfileCompletionStatus(
        is_complete=is_complete,
        has_person=has_person,
        has_address=has_address,
        has_religion=has_religion,
        has_marital_status=has_marital_status,
        missing_fields=missing_fields,
    )
```

#### 4. ProfileCompletionStatus Schema Update

Location: `backend/app/schemas/profile.py`

```python
class ProfileCompletionStatus(SQLModel):
    """Profile completion status response."""
    
    is_complete: bool
    has_person: bool
    has_address: bool
    has_religion: bool
    has_marital_status: bool  # NEW
    missing_fields: list[str]
```

#### 5. Marital Status Metadata Endpoint

Location: `backend/app/api/routes/metadata.py` (or new file)

```python
@router.get("/marital-statuses")
def get_marital_statuses() -> list[dict]:
    """Get available marital status options for selection."""
    return [
        {"value": status.value, "label": status.label}
        for status in MaritalStatus.get_selectable_options()
    ]
```

### Frontend Components

#### 1. EditMaritalStatusDialog

Location: `frontend/src/components/Profile/EditMaritalStatusDialog.tsx`

A dialog component similar to AddReligionDialog that:
- Fetches marital status options from the API
- Displays a select dropdown with options
- Calls PATCH endpoint to update person's marital status
- Triggers refetch of profile completion status on success

#### 2. Complete Profile Page Update

Location: `frontend/src/routes/complete-profile.tsx`

Transform the "Personal Information" step:
- Show person details (name, gender, DOB) as read-only text
- Add "Edit Marital Status" button when `has_marital_status` is false
- Show current marital status when set
- Show green checkmark only when marital status is set

## Data Models

### MaritalStatus Enum Values

| Value | Label | Description |
|-------|-------|-------------|
| UNKNOWN | Unknown | Default value, indicates not yet set |
| SINGLE | Single | Never married |
| MARRIED | Married | Currently married |
| DIVORCED | Divorced | Previously married, now divorced |
| WIDOWED | Widowed | Spouse has passed away |
| SEPARATED | Separated | Married but living separately |

### Person Table Changes

```sql
ALTER TABLE person 
ADD COLUMN marital_status VARCHAR(20) NOT NULL DEFAULT 'unknown';
```

### Updated ProfileCompletionStatus Response

```json
{
  "is_complete": false,
  "has_person": true,
  "has_address": true,
  "has_religion": true,
  "has_marital_status": false,
  "missing_fields": ["marital_status"]
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*



### Property 1: Default Marital Status on Person Creation

*For any* person created without explicitly setting marital_status, the marital_status field SHALL be set to UNKNOWN.

**Validates: Requirements 1.3, 4.3**

### Property 2: Marital Status Non-Nullability

*For any* person record in the database, the marital_status field SHALL always contain a valid MaritalStatus enum value and never be null.

**Validates: Requirements 1.4**

### Property 3: Profile Completion Status for UNKNOWN Marital Status

*For any* person with marital_status equal to UNKNOWN, the ProfileCompletionStatus SHALL return has_marital_status as false AND include "marital_status" in the missing_fields list.

**Validates: Requirements 2.4, 2.5**

### Property 4: Profile Completion Status for Non-UNKNOWN Marital Status

*For any* person with marital_status NOT equal to UNKNOWN (i.e., SINGLE, MARRIED, DIVORCED, WIDOWED, or SEPARATED), the ProfileCompletionStatus SHALL return has_marital_status as true.

**Validates: Requirements 2.6**

### Property 5: Profile Completeness Requires Marital Status

*For any* profile where has_person, has_address, has_religion, and has_marital_status are all true, the ProfileCompletionStatus SHALL return is_complete as true.

**Validates: Requirements 2.7**

### Property 6: Marital Status Validation on Update

*For any* marital status update request, if the provided value is a valid MaritalStatus enum value (excluding UNKNOWN for user selection), the update SHALL succeed. If the value is invalid, the System SHALL return a 400 error.

**Validates: Requirements 3.3, 3.4**

### Property 7: Person Serialization Includes Marital Status

*For any* person record, when serialized to PersonPublic, the response SHALL include the marital_status field with the current enum value.

**Validates: Requirements 3.5, 4.4**

## Error Handling

| Error Scenario | HTTP Status | Error Message |
|----------------|-------------|---------------|
| Invalid marital status value | 400 | "Invalid marital status: {value}. Must be one of: single, married, divorced, widowed, separated" |
| Person not found for update | 404 | "Person not found" |
| Unauthorized update attempt | 403 | "Not authorized to update this person" |

## Testing Strategy

### Unit Tests

1. **MaritalStatus Enum Tests**
   - Verify all enum values exist (UNKNOWN, SINGLE, MARRIED, DIVORCED, WIDOWED, SEPARATED)
   - Verify label property returns correct human-readable labels
   - Verify get_selectable_options excludes UNKNOWN

2. **Person Model Tests**
   - Verify marital_status field exists with correct type
   - Verify default value is UNKNOWN

3. **ProfileService Tests**
   - Test has_marital_status is false when status is UNKNOWN
   - Test has_marital_status is true for each non-UNKNOWN status
   - Test missing_fields includes "marital_status" when UNKNOWN
   - Test is_complete logic with all combinations

4. **Schema Tests**
   - Verify PersonPublic includes marital_status
   - Verify PersonUpdate accepts marital_status
   - Verify PersonCreate defaults to UNKNOWN

### Property-Based Tests

Property-based tests will use pytest with Hypothesis to generate random inputs and verify properties hold across all valid inputs.

**Test Configuration:**
- Minimum 100 iterations per property test
- Use Hypothesis strategies for generating valid Person objects
- Tag format: **Feature: person-marital-status, Property {number}: {property_text}**

### Integration Tests

1. **API Endpoint Tests**
   - GET /metadata/marital-statuses returns all options except UNKNOWN
   - PATCH /persons/{id} updates marital_status successfully
   - PATCH /persons/{id} with invalid value returns 400
   - GET /profile/completion-status reflects marital status correctly

2. **Profile Completion Flow Tests**
   - New user signup creates person with UNKNOWN status
   - Profile shows incomplete until marital status is set
   - Setting marital status updates profile completion

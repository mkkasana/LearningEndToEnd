# Design Document: Person Attachment Signup Flow (Phase 2)

## Overview

This design document describes the modifications to the signup and complete-profile flow to integrate with the Person Attachment Approval System. The system will create inactive Person records during signup, add a duplicate check step to the profile completion flow, and handle the pending approval state.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Frontend                                        │
│  ┌─────────────────┐    ┌──────────────────────────────────────────────┐   │
│  │ /signup         │───▶│ /complete-profile                            │   │
│  │ (creates user   │    │ ┌────────────────────────────────────────┐  │   │
│  │  + inactive     │    │ │ Step 1: Personal Info (read-only)      │  │   │
│  │  person)        │    │ │ Step 2: Address                        │  │   │
│  └─────────────────┘    │ │ Step 3: Religion                       │  │   │
│                         │ │ Step 4: Marital Status                 │  │   │
│                         │ │ Step 5: Duplicate Check (NEW)          │  │   │
│                         │ │ Step 6: Pending Approval (NEW)         │  │   │
│                         │ └────────────────────────────────────────┘  │   │
│                         └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Backend API                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ProfileRouter (/api/v1/profile) - Updated                           │   │
│  │ - GET /completion-status        Updated with new fields             │   │
│  │ - GET /duplicate-check          NEW: Search for matching persons    │   │
│  │ - POST /complete-without-attachment  NEW: Activate person           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ UsersRouter (/api/v1/users) - Updated                               │   │
│  │ - POST /signup                  Updated: creates inactive person    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Service Layer                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ ProfileService (Updated)                                            │   │
│  │ - check_profile_completion()    Updated with new fields             │   │
│  │ - get_duplicate_matches()       NEW: Find matching persons          │   │
│  │ - complete_without_attachment() NEW: Activate person                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ PersonMatchingService (Existing)                                    │   │
│  │ - search_matching_persons()     Reused for duplicate check          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ AttachmentRequestService (Existing from Phase 1)                    │   │
│  │ - create_request()              Used when user selects "This is me" │   │
│  │ - get_my_pending_request()      Used for pending approval step      │   │
│  │ - cancel_request()              Used when user cancels request      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Backend Changes

#### User Signup Update

Location: `backend/app/api/routes/users.py`

Update the `/signup` endpoint to create Person with `is_active=False`:

```python
@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    # ... existing validation code ...
    
    # Create person with is_active=False
    person = Person(
        **person_create.model_dump(),
        created_by_user_id=user.id,
        is_active=False,  # NEW: Person starts as inactive
    )
    session.add(person)
    session.commit()
    
    return user
```

#### Profile Completion Status Schema Update

Location: `backend/app/schemas/profile.py`

```python
class ProfileCompletionStatus(SQLModel):
    """Profile completion status response."""
    
    is_complete: bool
    has_person: bool
    has_address: bool
    has_religion: bool
    has_marital_status: bool
    has_duplicate_check: bool  # NEW
    has_pending_attachment_request: bool  # NEW
    pending_request_id: uuid.UUID | None  # NEW
    missing_fields: list[str]
```

#### Profile Service Update

Location: `backend/app/services/profile_service.py`

```python
class ProfileService:
    def __init__(self, session: Session):
        self.session = session
        self.person_repo = PersonRepository(session)
        self.address_repo = PersonAddressRepository(session)
        self.religion_repo = PersonReligionRepository(session)
        self.attachment_request_repo = AttachmentRequestRepository(session)
    
    def check_profile_completion(self, user_id: uuid.UUID) -> ProfileCompletionStatus:
        """Check if user has completed their profile."""
        # ... existing checks for person, address, religion, marital_status ...
        
        # NEW: Check for pending attachment request
        pending_request = self.attachment_request_repo.get_pending_by_requester(user_id)
        has_pending_attachment_request = pending_request is not None
        pending_request_id = pending_request.id if pending_request else None
        
        # NEW: Check if duplicate check is complete
        # Duplicate check is complete if:
        # 1. Person is active (user completed without attachment), OR
        # 2. User has a pending/approved attachment request
        has_duplicate_check = False
        if person:
            has_duplicate_check = person.is_active or has_pending_attachment_request
        
        # Profile is complete when all steps done AND no pending request
        is_complete = (
            has_person and 
            has_address and 
            has_religion and 
            has_marital_status and
            has_duplicate_check and
            not has_pending_attachment_request
        )
        
        return ProfileCompletionStatus(
            is_complete=is_complete,
            has_person=has_person,
            has_address=has_address,
            has_religion=has_religion,
            has_marital_status=has_marital_status,
            has_duplicate_check=has_duplicate_check,
            has_pending_attachment_request=has_pending_attachment_request,
            pending_request_id=pending_request_id,
            missing_fields=missing_fields,
        )
    
    def get_duplicate_matches(self, user_id: uuid.UUID) -> list[PersonMatchResult]:
        """Find potential duplicate persons for the current user."""
        person = self.person_repo.get_by_user_id(user_id)
        if not person:
            return []
        
        # Get user's address and religion for matching
        addresses = self.address_repo.get_by_person_id(person.id)
        religion = self.religion_repo.get_by_person_id(person.id)
        
        if not addresses or not religion:
            return []
        
        address = addresses[0]  # Use primary/first address
        
        # Build search criteria from user's data
        search_criteria = PersonSearchRequest(
            first_name=person.first_name,
            last_name=person.last_name,
            gender_id=person.gender_id,
            country_id=address.country_id,
            state_id=address.state_id,
            district_id=address.district_id,
            sub_district_id=address.sub_district_id,
            locality_id=address.locality_id,
            religion_id=religion.religion_id,
            religion_category_id=religion.religion_category_id,
            religion_sub_category_id=religion.religion_sub_category_id,
            address_display=self._build_address_display(address),
            religion_display=self._build_religion_display(religion),
        )
        
        # Use existing matching service
        matching_service = PersonMatchingService(self.session)
        matches = matching_service.search_matching_persons(user_id, search_criteria)
        
        # Filter out persons that already have a user linked
        # (they can't be attachment targets)
        filtered_matches = [
            m for m in matches 
            if not self._person_has_user(m.person_id)
            and m.person_id != person.id  # Exclude self
        ]
        
        return filtered_matches
    
    def complete_without_attachment(self, user_id: uuid.UUID) -> ProfileCompletionStatus:
        """Complete profile without attaching to existing person."""
        # Check for pending request
        pending_request = self.attachment_request_repo.get_pending_by_requester(user_id)
        if pending_request:
            raise HTTPException(
                status_code=400,
                detail="Cannot complete profile while attachment request is pending"
            )
        
        # Activate the person
        person = self.person_repo.get_by_user_id(user_id)
        if not person:
            raise HTTPException(status_code=404, detail="Person not found")
        
        person.is_active = True
        self.session.add(person)
        self.session.commit()
        
        return self.check_profile_completion(user_id)
```

#### Profile Routes Update

Location: `backend/app/api/routes/profile.py`

```python
router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/completion-status", response_model=ProfileCompletionStatus)
def get_profile_completion_status(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """Get current user's profile completion status."""
    profile_service = ProfileService(session)
    return profile_service.check_profile_completion(current_user.id)

@router.get("/duplicate-check", response_model=list[PersonMatchResult])
def get_duplicate_check(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Search for potential duplicate persons matching the current user's data.
    Returns persons that could be the same person as the current user.
    """
    profile_service = ProfileService(session)
    return profile_service.get_duplicate_matches(current_user.id)

@router.post("/complete-without-attachment", response_model=ProfileCompletionStatus)
def complete_without_attachment(
    session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Complete profile without attaching to an existing person.
    Activates the current user's person record.
    """
    profile_service = ProfileService(session)
    return profile_service.complete_without_attachment(current_user.id)
```

### 2. Frontend Changes

#### Complete Profile Page Restructure

Location: `frontend/src/routes/complete-profile.tsx`

The page will be restructured to handle multiple steps with state management:

```typescript
type ProfileStep = 
  | "personal-info"
  | "address"
  | "religion"
  | "marital-status"
  | "duplicate-check"
  | "pending-approval"

function CompleteProfile() {
  const [currentStep, setCurrentStep] = useState<ProfileStep>("personal-info")
  
  const { data: profileStatus, refetch } = useQuery({
    queryKey: ["profileCompletion"],
    queryFn: () => ProfileService.getProfileCompletionStatus(),
  })
  
  // Determine current step based on profile status
  useEffect(() => {
    if (!profileStatus) return
    
    if (profileStatus.has_pending_attachment_request) {
      setCurrentStep("pending-approval")
    } else if (!profileStatus.has_address) {
      setCurrentStep("address")
    } else if (!profileStatus.has_religion) {
      setCurrentStep("religion")
    } else if (!profileStatus.has_marital_status) {
      setCurrentStep("marital-status")
    } else if (!profileStatus.has_duplicate_check) {
      setCurrentStep("duplicate-check")
    }
  }, [profileStatus])
  
  // Render appropriate step component
  return (
    <div className="container">
      <ProgressIndicator currentStep={currentStep} profileStatus={profileStatus} />
      
      {currentStep === "personal-info" && <PersonalInfoStep />}
      {currentStep === "address" && <AddressStep onComplete={refetch} />}
      {currentStep === "religion" && <ReligionStep onComplete={refetch} />}
      {currentStep === "marital-status" && <MaritalStatusStep onComplete={refetch} />}
      {currentStep === "duplicate-check" && <DuplicateCheckStep onComplete={refetch} />}
      {currentStep === "pending-approval" && <PendingApprovalStep onCancel={refetch} />}
    </div>
  )
}
```

#### Duplicate Check Step Component

Location: `frontend/src/components/Profile/DuplicateCheckStep.tsx`

```typescript
interface DuplicateCheckStepProps {
  onComplete: () => void
}

function DuplicateCheckStep({ onComplete }: DuplicateCheckStepProps) {
  const { data: matches, isLoading } = useQuery({
    queryKey: ["duplicateCheck"],
    queryFn: () => ProfileService.getDuplicateCheck(),
  })
  
  const createRequestMutation = useMutation({
    mutationFn: (targetPersonId: string) => 
      AttachmentRequestsService.createAttachmentRequest({ target_person_id: targetPersonId }),
    onSuccess: () => onComplete(),
  })
  
  const completeWithoutAttachmentMutation = useMutation({
    mutationFn: () => ProfileService.completeWithoutAttachment(),
    onSuccess: () => {
      window.location.href = "/"
    },
  })
  
  if (isLoading) {
    return <LoadingSpinner />
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Check for Existing Records</CardTitle>
        <CardDescription>
          We found some people that might be you. If you see yourself in the list,
          click "This is me" to link your account. Otherwise, click "None of these are me".
        </CardDescription>
      </CardHeader>
      <CardContent>
        {matches && matches.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2">
            {matches.map((match) => (
              <MatchCard
                key={match.person_id}
                match={match}
                onSelect={() => createRequestMutation.mutate(match.person_id)}
              />
            ))}
          </div>
        ) : (
          <p className="text-muted-foreground">No matching records found.</p>
        )}
        
        <Button
          variant="outline"
          className="w-full mt-4"
          onClick={() => completeWithoutAttachmentMutation.mutate()}
        >
          None of these are me - Complete my profile
        </Button>
      </CardContent>
    </Card>
  )
}
```

#### Match Card Component

Location: `frontend/src/components/Profile/MatchCard.tsx`

```typescript
interface MatchCardProps {
  match: PersonMatchResult
  onSelect: () => void
}

function MatchCard({ match, onSelect }: MatchCardProps) {
  const scoreColor = match.match_score >= 80 ? "text-green-600" : 
                     match.match_score >= 60 ? "text-yellow-600" : "text-gray-600"
  
  return (
    <Card className="cursor-pointer hover:border-primary" onClick={onSelect}>
      <CardContent className="p-4">
        <div className="flex justify-between items-start">
          <div>
            <h4 className="font-semibold">
              {match.first_name} {match.middle_name} {match.last_name}
            </h4>
            <p className="text-sm text-muted-foreground">
              Born: {formatDate(match.date_of_birth)}
            </p>
            <p className="text-sm text-muted-foreground">{match.address_display}</p>
            <p className="text-sm text-muted-foreground">{match.religion_display}</p>
          </div>
          <Badge className={scoreColor}>
            {match.match_score}% match
          </Badge>
        </div>
        <Button size="sm" className="mt-2 w-full">
          This is me
        </Button>
      </CardContent>
    </Card>
  )
}
```

#### Pending Approval Step Component

Location: `frontend/src/components/Profile/PendingApprovalStep.tsx`

```typescript
interface PendingApprovalStepProps {
  onCancel: () => void
}

function PendingApprovalStep({ onCancel }: PendingApprovalStepProps) {
  const { data: pendingRequest, refetch } = useQuery({
    queryKey: ["myPendingRequest"],
    queryFn: () => AttachmentRequestsService.getMyPendingRequest(),
    refetchInterval: 30000, // Poll every 30 seconds
  })
  
  const cancelMutation = useMutation({
    mutationFn: (requestId: string) => 
      AttachmentRequestsService.cancelRequest(requestId),
    onSuccess: () => onCancel(),
  })
  
  // Check if request was approved (user would have been redirected)
  useEffect(() => {
    if (!pendingRequest) {
      // Request might have been approved or denied
      // Check profile status
      ProfileService.getProfileCompletionStatus().then((status) => {
        if (status.is_complete) {
          window.location.href = "/"
        }
      })
    }
  }, [pendingRequest])
  
  if (!pendingRequest) {
    return <LoadingSpinner />
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Waiting for Approval
        </CardTitle>
        <CardDescription>
          Your request to link your account is pending approval from the person
          who created this record.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="p-4 bg-muted rounded-lg">
          <h4 className="font-semibold">Requested Person</h4>
          <p>
            {pendingRequest.target_first_name} {pendingRequest.target_middle_name}{" "}
            {pendingRequest.target_last_name}
          </p>
          <p className="text-sm text-muted-foreground">
            Born: {formatDate(pendingRequest.target_date_of_birth)}
          </p>
        </div>
        
        <p className="text-sm text-muted-foreground">
          Request submitted: {formatDate(pendingRequest.created_at)}
        </p>
        
        <Button
          variant="outline"
          onClick={() => cancelMutation.mutate(pendingRequest.id)}
        >
          Cancel Request
        </Button>
      </CardContent>
    </Card>
  )
}
```

#### Progress Indicator Component

Location: `frontend/src/components/Profile/ProgressIndicator.tsx`

```typescript
interface ProgressIndicatorProps {
  currentStep: ProfileStep
  profileStatus: ProfileCompletionStatus | undefined
}

function ProgressIndicator({ currentStep, profileStatus }: ProgressIndicatorProps) {
  const steps = [
    { id: "personal-info", label: "Personal Info", complete: profileStatus?.has_person },
    { id: "address", label: "Address", complete: profileStatus?.has_address },
    { id: "religion", label: "Religion", complete: profileStatus?.has_religion },
    { id: "marital-status", label: "Marital Status", complete: profileStatus?.has_marital_status },
    { id: "duplicate-check", label: "Verification", complete: profileStatus?.has_duplicate_check },
  ]
  
  return (
    <div className="flex justify-between mb-8">
      {steps.map((step, index) => (
        <div key={step.id} className="flex items-center">
          <div className={cn(
            "w-8 h-8 rounded-full flex items-center justify-center",
            step.complete ? "bg-green-500 text-white" :
            currentStep === step.id ? "bg-primary text-white" : "bg-muted"
          )}>
            {step.complete ? <Check className="h-4 w-4" /> : index + 1}
          </div>
          <span className="ml-2 text-sm hidden md:inline">{step.label}</span>
          {index < steps.length - 1 && (
            <div className="w-8 h-0.5 bg-muted mx-2" />
          )}
        </div>
      ))}
    </div>
  )
}
```

## Data Models

### Updated Profile Completion Status

```json
{
  "is_complete": false,
  "has_person": true,
  "has_address": true,
  "has_religion": true,
  "has_marital_status": true,
  "has_duplicate_check": false,
  "has_pending_attachment_request": false,
  "pending_request_id": null,
  "missing_fields": ["duplicate_check"]
}
```

### Duplicate Check Response

Uses existing `PersonMatchResult` schema:

```json
[
  {
    "person_id": "uuid",
    "first_name": "John",
    "middle_name": null,
    "last_name": "Doe",
    "date_of_birth": "1990-01-15",
    "date_of_death": null,
    "address_display": "Mumbai, Maharashtra, India",
    "religion_display": "Hinduism - Vaishnavism",
    "match_score": 85.5,
    "name_match_score": 85.5,
    "is_current_user": false,
    "is_already_connected": false
  }
]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*



### Property 1: Signup Creates Inactive Person

*For any* new user registration with valid data, the created Person record SHALL have `is_active` set to `False`.

**Validates: Requirements 1.1**

### Property 2: Profile Completion Status Accuracy

*For any* user, the profile completion status SHALL accurately reflect:
- `has_duplicate_check` is `True` if and only if the user's Person is active OR user has a pending/resolved attachment request
- `has_pending_attachment_request` is `True` if and only if the user has a PENDING attachment request
- `is_complete` is `True` if and only if all profile fields are complete AND `has_duplicate_check` is `True` AND `has_pending_attachment_request` is `False`

**Validates: Requirements 2.2, 5.1, 5.2, 5.3, 5.4**

### Property 3: Duplicate Check Results Filtering

*For any* call to the duplicate-check endpoint, all returned persons SHALL:
- NOT be the current user's own Person record
- NOT have a linked user account (user_id is NULL)
- Have a match score >= 40%
- Be active persons (is_active = True)

**Validates: Requirements 3.2, 7.2, 7.3, 7.4, 7.5**

### Property 4: Complete Without Attachment Activates Person

*For any* successful call to complete-without-attachment endpoint:
- The current user's Person `is_active` SHALL be set to `True`
- The response SHALL include updated profile completion status with `has_duplicate_check` = `True`
- The response SHALL include `is_complete` = `True` (assuming other fields are complete)

**Validates: Requirements 3.8, 6.1, 8.2, 8.3**

### Property 5: Complete Without Attachment Blocked by Pending Request

*For any* user with a PENDING attachment request, calling complete-without-attachment SHALL return a 400 error and NOT modify the Person's `is_active` status.

**Validates: Requirements 8.4**

## Error Handling

### API Error Responses

| Scenario | HTTP Status | Error Message |
|----------|-------------|---------------|
| Person not found for duplicate check | 404 | "Person not found" |
| Missing address for duplicate check | 200 | Returns empty array (no matches possible) |
| Missing religion for duplicate check | 200 | Returns empty array (no matches possible) |
| Complete without attachment with pending request | 400 | "Cannot complete profile while attachment request is pending" |
| Person not found for complete without attachment | 404 | "Person not found" |

### Frontend Error Handling

- Display toast notifications for API errors
- Show loading states during API calls
- Handle network errors gracefully with retry options
- Show appropriate messages when no matches found

## Testing Strategy

### Unit Tests

Unit tests should cover:
- ProfileService.check_profile_completion() with various states
- ProfileService.get_duplicate_matches() filtering logic
- ProfileService.complete_without_attachment() activation logic
- Signup endpoint creates inactive person

### Property-Based Tests

Property-based tests using `hypothesis` library should cover:
- Property 1: Signup creates inactive person
- Property 2: Profile completion status accuracy
- Property 3: Duplicate check results filtering
- Property 4: Complete without attachment activates person
- Property 5: Complete without attachment blocked by pending request

Configuration:
- Minimum 100 iterations per property test
- Tag format: `Feature: person-attachment-signup-flow, Property N: description`

### Integration Tests

Integration tests should cover:
- Full signup → complete-profile → duplicate-check → complete flow
- Signup → complete-profile → duplicate-check → attachment-request → approval flow
- Profile completion status transitions
- API endpoint responses

### Frontend Tests

- Component rendering tests for new steps
- User interaction tests (button clicks, navigation)
- Loading and error state display
- Responsive layout verification

## Security Considerations

1. **Authorization**: All profile endpoints verify the current user
2. **Data Privacy**: Duplicate check only returns persons without linked users
3. **Rate Limiting**: Consider rate limiting duplicate check to prevent abuse
4. **Input Validation**: All inputs validated before processing

## Migration Notes

### No Database Migration Required

This phase does not require database schema changes. The `is_active` field and `person_attachment_request` table were created in Phase 1.

### Backward Compatibility

- Existing users with active Person records are unaffected
- New users will go through the updated flow
- Profile completion status API is backward compatible (new fields are additive)


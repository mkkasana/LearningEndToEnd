# Design Document: Person Attachment Approval System

## Overview

This design document describes the implementation of a person attachment approval system that prevents duplicate Person records when new users sign up. The system allows new users to request attachment to existing Person records, with approval required from the original creator.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Frontend                                    │
│  ┌─────────────────┐    ┌──────────────────────────────────────────┐   │
│  │ AppSidebar      │───▶│ User Approvals Page                      │   │
│  │ (menu item)     │    │ - List pending requests                  │   │
│  └─────────────────┘    │ - Approval detail dialog                 │   │
│                         └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              Backend API                                 │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ AttachmentRequestRouter (/api/v1/attachment-requests)           │   │
│  │ - POST /                    Create request                      │   │
│  │ - GET /to-approve           List requests to approve            │   │
│  │ - GET /my-pending           Get my pending request              │   │
│  │ - POST /{id}/approve        Approve request                     │   │
│  │ - POST /{id}/deny           Deny request                        │   │
│  │ - POST /{id}/cancel         Cancel request                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Service Layer                                  │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ AttachmentRequestService                                        │   │
│  │ - create_request()                                              │   │
│  │ - get_requests_to_approve()                                     │   │
│  │ - get_my_pending_request()                                      │   │
│  │ - approve_request()                                             │   │
│  │ - deny_request()                                                │   │
│  │ - cancel_request()                                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           Data Layer                                     │
│  ┌──────────────────────┐    ┌──────────────────────────────────┐      │
│  │ PersonAttachment     │    │ Person (updated)                 │      │
│  │ Request              │    │ + is_active: bool                │      │
│  │ - id                 │    └──────────────────────────────────┘      │
│  │ - requester_user_id  │                                              │
│  │ - requester_person_id│    ┌──────────────────────────────────┐      │
│  │ - target_person_id   │    │ AttachmentRequestRepository      │      │
│  │ - approver_user_id   │    │ - create()                       │      │
│  │ - status             │    │ - get_by_id()                    │      │
│  │ - created_at         │    │ - get_pending_by_approver()      │      │
│  │ - resolved_at        │    │ - get_pending_by_requester()     │      │
│  │ - resolved_by_user_id│    │ - update()                       │      │
│  └──────────────────────┘    └──────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Database Models

#### Person Model Update

Location: `backend/app/db_models/person/person.py`

```python
class Person(SQLModel, table=True):
    # ... existing fields ...
    
    is_active: bool = Field(
        default=True, 
        description="Whether person is active and visible in searches"
    )
```

#### Attachment Request Status Enum

Location: `backend/app/enums/attachment_request_status.py`

```python
from enum import Enum

class AttachmentRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"
```

#### PersonAttachmentRequest Model

Location: `backend/app/db_models/person/person_attachment_request.py`

```python
class PersonAttachmentRequest(SQLModel, table=True):
    __tablename__ = "person_attachment_request"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    requester_user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    requester_person_id: uuid.UUID = Field(foreign_key="person.id", index=True)
    target_person_id: uuid.UUID = Field(foreign_key="person.id", index=True)
    approver_user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    status: AttachmentRequestStatus = Field(default=AttachmentRequestStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: datetime | None = Field(default=None)
    resolved_by_user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
```

### 2. Schemas

Location: `backend/app/schemas/attachment_request.py`

```python
class AttachmentRequestCreate(SQLModel):
    """Schema for creating an attachment request."""
    target_person_id: uuid.UUID

class AttachmentRequestPublic(SQLModel):
    """Schema for public attachment request response."""
    id: uuid.UUID
    requester_user_id: uuid.UUID
    requester_person_id: uuid.UUID
    target_person_id: uuid.UUID
    approver_user_id: uuid.UUID
    status: AttachmentRequestStatus
    created_at: datetime
    resolved_at: datetime | None
    resolved_by_user_id: uuid.UUID | None

class AttachmentRequestWithDetails(SQLModel):
    """Schema for attachment request with requester and target details."""
    id: uuid.UUID
    status: AttachmentRequestStatus
    created_at: datetime
    
    # Requester details
    requester_first_name: str
    requester_middle_name: str | None
    requester_last_name: str
    requester_date_of_birth: date
    requester_gender: str
    requester_address_display: str | None
    requester_religion_display: str | None
    
    # Target person details
    target_first_name: str
    target_middle_name: str | None
    target_last_name: str
    target_date_of_birth: date

class MyPendingRequestResponse(SQLModel):
    """Schema for requester's pending request view."""
    id: uuid.UUID
    status: AttachmentRequestStatus
    created_at: datetime
    
    # Target person details
    target_first_name: str
    target_middle_name: str | None
    target_last_name: str
    target_date_of_birth: date
    target_gender: str
```

### 3. Repository Layer

Location: `backend/app/repositories/attachment_request_repository.py`

```python
class AttachmentRequestRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, request: PersonAttachmentRequest) -> PersonAttachmentRequest:
        """Create a new attachment request."""
        pass
    
    def get_by_id(self, request_id: uuid.UUID) -> PersonAttachmentRequest | None:
        """Get attachment request by ID."""
        pass
    
    def get_pending_by_requester(self, user_id: uuid.UUID) -> PersonAttachmentRequest | None:
        """Get pending request for a requester (only one allowed)."""
        pass
    
    def get_pending_by_approver(self, user_id: uuid.UUID) -> list[PersonAttachmentRequest]:
        """Get all pending requests for an approver."""
        pass
    
    def count_pending_by_approver(self, user_id: uuid.UUID) -> int:
        """Count pending requests for badge display."""
        pass
    
    def update(self, request: PersonAttachmentRequest) -> PersonAttachmentRequest:
        """Update an attachment request."""
        pass
```

### 4. Service Layer

Location: `backend/app/services/attachment_request_service.py`

```python
class AttachmentRequestService:
    def __init__(self, session: Session):
        self.session = session
        self.request_repo = AttachmentRequestRepository(session)
        self.person_repo = PersonRepository(session)
        self.user_repo = UserRepository(session)
    
    def create_request(
        self, 
        requester_user_id: uuid.UUID, 
        target_person_id: uuid.UUID
    ) -> PersonAttachmentRequest:
        """
        Create a new attachment request.
        
        Validations:
        - Requester must have a person record
        - Requester cannot have existing pending request
        - Target person must exist and have no user_id
        - Target person must not be created by requester
        """
        pass
    
    def get_requests_to_approve(
        self, 
        approver_user_id: uuid.UUID
    ) -> list[AttachmentRequestWithDetails]:
        """Get all pending requests for approver with full details."""
        pass
    
    def get_my_pending_request(
        self, 
        requester_user_id: uuid.UUID
    ) -> MyPendingRequestResponse | None:
        """Get requester's pending request with target details."""
        pass
    
    def approve_request(
        self, 
        request_id: uuid.UUID, 
        approver_user_id: uuid.UUID
    ) -> None:
        """
        Approve an attachment request.
        
        Actions:
        1. Validate request exists and is pending
        2. Validate current user is the approver
        3. Link requester user to target person
        4. Set target person as primary
        5. Delete requester's temp person and all metadata
        6. Update request status to APPROVED
        """
        pass
    
    def deny_request(
        self, 
        request_id: uuid.UUID, 
        approver_user_id: uuid.UUID
    ) -> None:
        """
        Deny an attachment request.
        
        Actions:
        1. Validate request exists and is pending
        2. Validate current user is the approver
        3. Delete requester's temp person and all metadata
        4. Delete requester's user account
        5. Update request status to DENIED
        """
        pass
    
    def cancel_request(
        self, 
        request_id: uuid.UUID, 
        requester_user_id: uuid.UUID
    ) -> None:
        """
        Cancel an attachment request.
        
        Actions:
        1. Validate request exists and is pending
        2. Validate current user is the requester
        3. Update request status to CANCELLED
        """
        pass
    
    def _delete_person_with_metadata(self, person_id: uuid.UUID) -> None:
        """Delete a person and all associated metadata."""
        # Delete in order to respect foreign keys:
        # 1. person_address
        # 2. person_religion
        # 3. person_relationship
        # 4. person_life_event
        # 5. person_metadata
        # 6. person_profession
        # 7. person
        pass
```

### 5. API Routes

Location: `backend/app/api/routes/attachment_requests.py`

```python
router = APIRouter(prefix="/attachment-requests", tags=["attachment-requests"])

@router.post("/", response_model=AttachmentRequestPublic)
def create_attachment_request(
    session: SessionDep,
    current_user: CurrentUser,
    request_in: AttachmentRequestCreate
) -> Any:
    """Create a new attachment request."""
    pass

@router.get("/to-approve", response_model=list[AttachmentRequestWithDetails])
def get_requests_to_approve(
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """Get all pending requests for current user to approve."""
    pass

@router.get("/my-pending", response_model=MyPendingRequestResponse)
def get_my_pending_request(
    session: SessionDep,
    current_user: CurrentUser
) -> Any:
    """Get current user's pending attachment request."""
    pass

@router.get("/pending-count")
def get_pending_count(
    session: SessionDep,
    current_user: CurrentUser
) -> dict:
    """Get count of pending requests for badge display."""
    pass

@router.post("/{request_id}/approve", response_model=Message)
def approve_request(
    session: SessionDep,
    current_user: CurrentUser,
    request_id: uuid.UUID
) -> Any:
    """Approve an attachment request."""
    pass

@router.post("/{request_id}/deny", response_model=Message)
def deny_request(
    session: SessionDep,
    current_user: CurrentUser,
    request_id: uuid.UUID
) -> Any:
    """Deny an attachment request."""
    pass

@router.post("/{request_id}/cancel", response_model=Message)
def cancel_request(
    session: SessionDep,
    current_user: CurrentUser,
    request_id: uuid.UUID
) -> Any:
    """Cancel an attachment request (requester only)."""
    pass
```

### 6. Frontend Components

#### Sidebar Update

Location: `frontend/src/components/Sidebar/AppSidebar.tsx`

Add "User Approvals" menu item after "My Contributions":
- Icon: `UserCheck` from lucide-react
- Route: `/user-approvals`
- Badge showing pending count (fetched via `/pending-count` API)

#### User Approvals Page

Location: `frontend/src/routes/_layout/user-approvals.tsx`

```typescript
// Route component for /user-approvals
export const Route = createFileRoute("/_layout/user-approvals")({
  component: UserApprovalsPage,
})

function UserApprovalsPage() {
  // Fetch pending requests using useQuery
  // Display grid of request cards
  // Handle empty state
  // Open detail dialog on card click
}
```

#### Approval Request Card

Location: `frontend/src/components/UserApprovals/ApprovalRequestCard.tsx`

Displays:
- Requester name, DOB, gender
- Requester address (formatted)
- Requester religion (formatted)
- Target person name, DOB
- Request date
- Click to open detail dialog

#### Approval Detail Dialog

Location: `frontend/src/components/UserApprovals/ApprovalDetailDialog.tsx`

Displays full details and action buttons:
- Complete requester information
- Complete target person information
- "Approve" button (primary action)
- "Deny" button (destructive action with confirmation)

## Data Models

### Database Schema

```sql
-- Add is_active to person table
ALTER TABLE person ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;

-- Create attachment request status enum
CREATE TYPE attachment_request_status AS ENUM ('pending', 'approved', 'denied', 'cancelled');

-- Create person_attachment_request table
CREATE TABLE person_attachment_request (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_user_id UUID NOT NULL REFERENCES "user"(id),
    requester_person_id UUID NOT NULL REFERENCES person(id),
    target_person_id UUID NOT NULL REFERENCES person(id),
    approver_user_id UUID NOT NULL REFERENCES "user"(id),
    status attachment_request_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMP,
    resolved_by_user_id UUID REFERENCES "user"(id),
    
    -- Indexes for common queries
    CONSTRAINT idx_requester_pending UNIQUE (requester_user_id) 
        WHERE status = 'pending'
);

CREATE INDEX idx_attachment_request_approver ON person_attachment_request(approver_user_id) 
    WHERE status = 'pending';
CREATE INDEX idx_attachment_request_requester ON person_attachment_request(requester_user_id);
```

### Entity Relationship

```
┌─────────────┐       ┌──────────────────────────┐       ┌─────────────┐
│    User     │       │ PersonAttachmentRequest  │       │   Person    │
├─────────────┤       ├──────────────────────────┤       ├─────────────┤
│ id          │◄──────│ requester_user_id        │       │ id          │
│ email       │       │ approver_user_id         │──────►│ user_id     │
│ ...         │       │ resolved_by_user_id      │       │ is_active   │
└─────────────┘       │                          │       │ ...         │
                      │ requester_person_id      │──────►└─────────────┘
                      │ target_person_id         │──────►
                      │                          │
                      │ status                   │
                      │ created_at               │
                      │ resolved_at              │
                      └──────────────────────────┘
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*



### Property 1: Person is_active Default Value

*For any* Person created without explicitly setting `is_active`, the field SHALL default to `True`.

**Validates: Requirements 1.1**

### Property 2: Inactive Person Search Exclusion

*For any* search operation (person matching, family tree queries, contributions), all returned persons SHALL have `is_active` equal to `True`. No inactive persons should appear in search results.

**Validates: Requirements 1.3**

### Property 3: Approval Preserves Target Person is_active

*For any* attachment request approval, the target Person's `is_active` value SHALL remain unchanged after the approval operation completes.

**Validates: Requirements 1.5**

### Property 4: One Pending Request Per User

*For any* user, attempting to create a second attachment request while having an existing PENDING request SHALL result in a 400 error. The system SHALL enforce at most one PENDING request per requester.

**Validates: Requirements 2.2, 3.7**

### Property 5: Target Person Must Not Have User

*For any* attachment request creation, if the target Person already has a non-null `user_id`, the system SHALL return a 400 error. Only persons without linked users can be attachment targets.

**Validates: Requirements 2.3, 3.8**

### Property 6: Cannot Attach to Own Creation

*For any* attachment request creation, if the target Person's `created_by_user_id` equals the requester's user ID, the system SHALL return a 400 error.

**Validates: Requirements 3.9**

### Property 7: Create Request Auto-Population

*For any* successfully created attachment request, the `requester_user_id` SHALL equal the current user's ID, `requester_person_id` SHALL equal the current user's Person ID, `approver_user_id` SHALL equal the target Person's `created_by_user_id`, and `status` SHALL be PENDING.

**Validates: Requirements 3.2, 3.3, 3.4, 3.5, 3.6**

### Property 8: List To-Approve Filtering

*For any* call to the to-approve endpoint, all returned requests SHALL have `approver_user_id` equal to the current user AND `status` equal to PENDING. No requests for other approvers or with non-pending status should be returned.

**Validates: Requirements 4.2, 4.3**

### Property 9: List To-Approve Ordering

*For any* list of requests returned by the to-approve endpoint, the requests SHALL be sorted by `created_at` in descending order (newest first).

**Validates: Requirements 4.8**

### Property 10: Approve Authorization

*For any* approve request operation, if the current user is not the `approver_user_id` of the request, the system SHALL return a 403 error. Only the designated approver can approve.

**Validates: Requirements 6.2**

### Property 11: Approve State Validation

*For any* approve request operation, if the request status is not PENDING, the system SHALL return an appropriate error. Only pending requests can be approved.

**Validates: Requirements 6.3**

### Property 12: Approve Side Effects

*For any* successful approval operation:
- The target Person's `user_id` SHALL be set to the `requester_user_id`
- The target Person's `is_primary` SHALL be set to `True`
- The requester's temporary Person record SHALL be deleted
- All metadata associated with the temp Person (address, religion, etc.) SHALL be deleted
- The request `status` SHALL be APPROVED
- The request `resolved_at` SHALL be set to current timestamp

**Validates: Requirements 6.4**

### Property 13: Deny Side Effects

*For any* successful denial operation:
- The requester's temporary Person record SHALL be deleted
- All metadata associated with the temp Person SHALL be deleted
- The requester's User record SHALL be deleted
- The request `status` SHALL be DENIED
- The request `resolved_at` SHALL be set to current timestamp

**Validates: Requirements 7.4**

### Property 14: Cancel Preserves Records

*For any* successful cancel operation:
- The requester's Person record SHALL NOT be deleted
- The requester's User record SHALL NOT be deleted
- Only the request `status` SHALL be updated to CANCELLED

**Validates: Requirements 8.4, 8.5**

## Error Handling

### API Error Responses

| Scenario | HTTP Status | Error Message |
|----------|-------------|---------------|
| User already has pending request | 400 | "You already have a pending attachment request" |
| Target person has user linked | 400 | "This person is already linked to a user account" |
| Target person created by requester | 400 | "You cannot attach to a person you created" |
| Target person not found | 404 | "Person not found" |
| Request not found | 404 | "Attachment request not found" |
| Not authorized to approve/deny | 403 | "You are not authorized to perform this action" |
| Request not in pending status | 400 | "This request has already been resolved" |
| Not authorized to cancel | 403 | "You can only cancel your own requests" |

### Cascade Deletion Error Handling

When deleting a Person with metadata, the service should:
1. Use a database transaction to ensure atomicity
2. Delete in correct order to respect foreign key constraints
3. Roll back entire transaction if any deletion fails
4. Log detailed error information for debugging

### Frontend Error Handling

- Display toast notifications for API errors
- Show loading states during API calls
- Disable action buttons while requests are in progress
- Show confirmation dialog before destructive actions (deny)

## Testing Strategy

### Unit Tests

Unit tests should cover:
- Schema validation for request creation
- Repository methods (CRUD operations)
- Service method business logic (mocked dependencies)
- Authorization checks
- Error condition handling

### Property-Based Tests

Property-based tests using `hypothesis` library should cover:
- Property 1: Default is_active value
- Property 2: Inactive person exclusion from searches
- Property 4: One pending request constraint
- Property 7: Auto-population of request fields
- Property 8: Filtering logic for to-approve endpoint
- Property 12: Approval side effects
- Property 13: Denial side effects
- Property 14: Cancel preserves records

Configuration:
- Minimum 100 iterations per property test
- Tag format: `Feature: person-attachment-approval, Property N: description`

### Integration Tests

Integration tests should cover:
- Full API request/response cycle
- Database state changes after operations
- Cascade deletion of person metadata
- Authorization enforcement across endpoints

### Frontend Tests

- Component rendering tests
- User interaction tests (click handlers)
- Loading and error state display
- Responsive layout verification

## Migration Plan

### Alembic Migration

```python
"""Add is_active to person and create attachment request table

Revision ID: xxx
"""

def upgrade():
    # Add is_active column to person table
    op.add_column('person', sa.Column('is_active', sa.Boolean(), 
                                       nullable=False, server_default='true'))
    
    # Create enum type
    attachment_status = postgresql.ENUM('pending', 'approved', 'denied', 'cancelled',
                                         name='attachment_request_status')
    attachment_status.create(op.get_bind())
    
    # Create attachment request table
    op.create_table(
        'person_attachment_request',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('requester_user_id', postgresql.UUID(as_uuid=True), 
                  sa.ForeignKey('user.id'), nullable=False),
        sa.Column('requester_person_id', postgresql.UUID(as_uuid=True), 
                  sa.ForeignKey('person.id'), nullable=False),
        sa.Column('target_person_id', postgresql.UUID(as_uuid=True), 
                  sa.ForeignKey('person.id'), nullable=False),
        sa.Column('approver_user_id', postgresql.UUID(as_uuid=True), 
                  sa.ForeignKey('user.id'), nullable=False),
        sa.Column('status', attachment_status, nullable=False, 
                  server_default='pending'),
        sa.Column('created_at', sa.DateTime(), nullable=False, 
                  server_default=sa.func.now()),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by_user_id', postgresql.UUID(as_uuid=True), 
                  sa.ForeignKey('user.id'), nullable=True),
    )
    
    # Create indexes
    op.create_index('idx_attachment_request_approver_pending', 
                    'person_attachment_request', ['approver_user_id'],
                    postgresql_where=sa.text("status = 'pending'"))
    op.create_index('idx_attachment_request_requester', 
                    'person_attachment_request', ['requester_user_id'])

def downgrade():
    op.drop_table('person_attachment_request')
    op.execute('DROP TYPE attachment_request_status')
    op.drop_column('person', 'is_active')
```

## Security Considerations

1. **Authorization**: All endpoints verify the current user has permission to perform the action
2. **Data Privacy**: Requester details are only visible to the designated approver
3. **Cascade Deletion**: Ensure complete cleanup of user data on denial
4. **Rate Limiting**: Consider adding rate limits to prevent abuse of request creation
5. **Audit Trail**: Request status changes are tracked with timestamps and user IDs

# Design Document: Support Ticket and Feature Request Tracking System

## Overview

The support ticket system enables users to report bugs and request features while providing administrators with tools to manage and resolve these submissions. The system follows the existing application architecture with a React frontend, FastAPI backend, and PostgreSQL database.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
├─────────────────────────────────────────────────────────────┤
│  - SupportTicketsPage (User view)                                   │
│  - CreateSupportTicketDialog                                         │
│  - SupportTicketListTable                                            │
│  - SupportTicketDetailDialog                                         │
│  - AdminSupportTicketsPanel (Admin view)                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  Routes: /api/v1/support-tickets                                     │
│  - POST   /support-tickets (create)                                  │
│  - GET    /support-tickets/me (user's issues)                        │
│  - GET    /support-tickets/{id} (get single)                         │
│  - PATCH  /support-tickets/{id} (update)                             │
│  - DELETE /support-tickets/{id} (delete)                             │
│  - GET    /support-tickets/admin/all (admin: all tickets)            │
│  - PATCH  /support-tickets/{id}/resolve (admin: mark resolved)      │
│  - PATCH  /support-tickets/{id}/reopen (admin: reopen)              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
├─────────────────────────────────────────────────────────────┤
│  SupportTicketService                                               │
│  - create_support_ticket()                                           │
│  - get_user_support_tickets()                                        │
│  - get_all_support_tickets_admin()                                   │
│  - update_support_ticket()                                           │
│  - resolve_support_ticket()                                          │
│  - reopen_support_ticket()                                           │
│  - delete_support_ticket()                                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Repository Layer                            │
├─────────────────────────────────────────────────────────────┤
│  SupportTicketRepository                                            │
│  - create()                                                 │
│  - get_by_id()                                              │
│  - get_by_user_id()                                         │
│  - get_all()                                                │
│  - get_by_status()                                          │
│  - update()                                                 │
│  - delete()                                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Database (PostgreSQL)                     │
├─────────────────────────────────────────────────────────────┤
│  Table: support_ticket                                               │
│  - id (UUID, PK)                                            │
│  - user_id (UUID, FK → user.id)                            │
│  - issue_type (VARCHAR: 'bug' | 'feature_request')         │
│  - title (VARCHAR(100))                                     │
│  - description (TEXT, max 2000 chars)                       │
│  - status (VARCHAR: 'open' | 'closed')                      │
│  - resolved_by_user_id (UUID, FK → user.id, nullable)      │
│  - resolved_at (TIMESTAMP, nullable)                        │
│  - created_at (TIMESTAMP)                                   │
│  - updated_at (TIMESTAMP)                                   │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Database Model

**Table: support_ticket**

```sql
CREATE TABLE support_ticket (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    issue_type VARCHAR(20) NOT NULL CHECK (issue_type IN ('bug', 'feature_request')),
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL CHECK (char_length(description) <= 2000),
    status VARCHAR(20) NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'closed')),
    resolved_by_user_id UUID REFERENCES "user"(id) ON DELETE SET NULL,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_support_ticket_user_id ON support_ticket(user_id);
CREATE INDEX idx_support_ticket_status ON support_ticket(status);
CREATE INDEX idx_support_ticket_created_at ON support_ticket(created_at DESC);
CREATE INDEX idx_support_ticket_type ON support_ticket(issue_type);
```

### Backend Schemas (Pydantic)

**IssueType Enum:**
```python
class IssueType(str, Enum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
```

**IssueStatus Enum:**
```python
class IssueStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
```

**SupportTicketCreate:**
```python
class SupportTicketCreate(SQLModel):
    issue_type: SupportTicketType
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=2000)
```

**SupportTicketUpdate:**
```python
class SupportTicketUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=2000)
```

**SupportTicketPublic:**
```python
class SupportTicketPublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    issue_type: SupportTicketType
    title: str
    description: str
    status: SupportTicketStatus
    resolved_by_user_id: uuid.UUID | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

**SupportTicketPublicWithUser:**
```python
class SupportTicketPublicWithUser(SupportTicketPublic):
    user_email: str
    user_full_name: str | None
    resolved_by_email: str | None
```

**SupportTicketsPublicList:**
```python
class SupportTicketsPublicList(SQLModel):
    data: list[SupportTicketPublic]
    count: int
```

### Repository Layer

**SupportTicketRepository:**
```python
class SupportTicketRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, issue: SupportTicket) -> Issue:
        """Create a new issue"""
        
    def get_by_id(self, support_ticket_id: uuid.UUID) -> SupportTicket | None:
        """Get ticket by ID"""
        
    def get_by_user_id(
        self, 
        user_id: uuid.UUID, 
        status: SupportTicketStatus | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[SupportTicket]:
        """Get all tickets for a specific user with optional status filter"""
        
    def get_all(
        self,
        status: SupportTicketStatus | None = None,
        issue_type: SupportTicketType | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[SupportTicket]:
        """Get all tickets with optional filters (admin only)"""
        
    def update(self, issue: SupportTicket) -> Issue:
        """Update a ticket"""
        
    def delete(self, issue: SupportTicket) -> None:
        """Delete a ticket"""
        
    def count_by_user_id(self, user_id: uuid.UUID, status: SupportTicketStatus | None = None) -> int:
        """Count tickets for a user"""
        
    def count_all(self, status: SupportTicketStatus | None = None, issue_type: SupportTicketType | None = None) -> int:
        """Count all tickets (admin only)"""
```

### Service Layer

**SupportTicketService:**
```python
class SupportTicketService:
    def __init__(self, session: Session):
        self.session = session
        self.support_ticket_repo = SupportTicketRepository(session)
    
    def create_support_ticket(self, user_id: uuid.UUID, support_ticket_in: SupportTicketCreate) -> Issue:
        """Create a new ticket for a user"""
        
    def get_user_support_tickets(
        self, 
        user_id: uuid.UUID, 
        status: SupportTicketStatus | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[SupportTicket], int]:
        """Get all tickets for a user with pagination"""
        
    def get_all_support_tickets_admin(
        self,
        status: SupportTicketStatus | None = None,
        issue_type: SupportTicketType | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[SupportTicket], int]:
        """Get all tickets for admin with filters and pagination"""
        
    def get_support_ticket_by_id(self, support_ticket_id: uuid.UUID) -> SupportTicket | None:
        """Get a single ticket by ID"""
        
    def update_support_ticket(self, issue: SupportTicket, support_ticket_in: SupportTicketUpdate) -> Issue:
        """Update a ticket"""
        
    def resolve_support_ticket(self, issue: SupportTicket, resolved_by_user_id: uuid.UUID) -> Issue:
        """Mark a ticket as resolved"""
        
    def reopen_support_ticket(self, issue: SupportTicket) -> Issue:
        """Reopen a closed issue"""
        
    def delete_support_ticket(self, issue: SupportTicket) -> None:
        """Delete a ticket"""
        
    def can_user_access_support_ticket(self, issue: SupportTicket, user_id: uuid.UUID, is_superuser: bool) -> bool:
        """Check if user can access a ticket"""
```

### API Routes

**Endpoints:**

1. **POST /api/v1/support-tickets** - Create new issue
   - Auth: Required
   - Body: SupportTicketCreate
   - Returns: SupportTicketPublic

2. **GET /api/v1/support-tickets/me** - Get current user's issues
   - Auth: Required
   - Query params: status, skip, limit
   - Returns: SupportTicketsPublicList

3. **GET /api/v1/support-tickets/{support_ticket_id}** - Get single issue
   - Auth: Required
   - Authorization: Owner or admin
   - Returns: SupportTicketPublic

4. **PATCH /api/v1/support-tickets/{support_ticket_id}** - Update issue
   - Auth: Required
   - Authorization: Owner only
   - Body: SupportTicketUpdate
   - Returns: SupportTicketPublic

5. **DELETE /api/v1/support-tickets/{support_ticket_id}** - Delete issue
   - Auth: Required
   - Authorization: Owner or admin
   - Returns: Success message

6. **GET /api/v1/support-tickets/admin/all** - Get all tickets (admin)
   - Auth: Required (superuser)
   - Query params: status, issue_type, skip, limit
   - Returns: List[SupportTicketPublicWithUser]

7. **PATCH /api/v1/support-tickets/{support_ticket_id}/resolve** - Mark resolved (admin)
   - Auth: Required (superuser)
   - Returns: SupportTicketPublic

8. **PATCH /api/v1/support-tickets/{support_ticket_id}/reopen** - Reopen ticket (admin)
   - Auth: Required (superuser)
   - Returns: SupportTicketPublic

### Frontend Components

**1. SupportTicketsPage (User View)**
- Location: `frontend/src/routes/support-tickets.tsx`
- Features:
  - Tab navigation (All, Open, Closed)
  - SupportTicket list table with pagination
  - "Report New Ticket" button
  - SupportTicket detail modal
  - Delete confirmation dialog

**2. CreateSupportTicketDialog**
- Location: `frontend/src/components/SupportTickets/CreateSupportTicketDialog.tsx`
- Features:
  - SupportTicket type selector (Bug/Feature Request)
  - Title input (max 100 chars with counter)
  - Description textarea (max 2000 chars with counter)
  - Form validation
  - Submit button

**3. SupportTicketListTable**
- Location: `frontend/src/components/SupportTickets/SupportTicketListTable.tsx`
- Columns:
  - SupportTicket # (auto-generated)
  - Type (icon badge)
  - Title
  - Status (badge)
  - Created Date
  - Actions (View, Delete)

**4. SupportTicketDetailDialog**
- Location: `frontend/src/components/SupportTickets/SupportTicketDetailDialog.tsx`
- Displays:
  - Full title
  - Complete description
  - SupportTicket type
  - Status
  - Created date
  - Updated date
  - Resolved date (if applicable)

**5. AdminSupportTicketsPanel**
- Location: `frontend/src/components/Admin/AdminSupportTicketsPanel.tsx`
- Features:
  - Filter by status and type
  - Sort by creation date (oldest first)
  - Shows submitter information
  - Resolve/Reopen buttons
  - Delete button
  - Pagination

## Data Models

### SupportTicket Model (SQLModel)

```python
class SupportTicket(SQLModel, table=True):
    __tablename__ = "support_ticket"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    issue_type: SupportTicketType
    title: str = Field(max_length=100)
    description: str = Field(max_length=2000)
    status: SupportTicketStatus = Field(default=IssueStatus.OPEN, index=True)
    resolved_by_user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    resolved_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: SupportTicket ownership validation
*For any* ticket and any user, when a non-admin user attempts to access a ticket, access should only be granted if the user_id matches the ticket's user_id
**Validates: Requirements 8.1, 8.2**

### Property 2: Status transition validity
*For any* issue, when the status changes from open to closed, the resolved_at timestamp should be set to the current time and resolved_by_user_id should be set
**Validates: Requirements 5.1, 5.3**

### Property 3: Status transition reversal
*For any* issue, when the status changes from closed to open, the resolved_at timestamp should be cleared (set to null) and resolved_by_user_id should be cleared
**Validates: Requirements 5.2, 5.3**

### Property 4: Title length constraint
*For any* ticket creation or update, when the title exceeds 100 characters, the operation should be rejected with a validation error
**Validates: Requirements 2.1, 1.5**

### Property 5: Description length constraint
*For any* ticket creation or update, when the description exceeds 2000 characters, the operation should be rejected with a validation error
**Validates: Requirements 2.2**

### Property 6: Required field validation
*For any* ticket creation, when any required field (issue_type, title, description) is missing or empty, the operation should be rejected with a validation error
**Validates: Requirements 2.3, 2.4, 2.5**

### Property 7: User ticket list isolation
*For any* user's ticket list query, all returned tickets should have a user_id matching the requesting user's ID
**Validates: Requirements 8.1**

### Property 8: Admin access privilege
*For any* admin-only operation, when a non-superuser attempts the operation, the system should return a 403 Forbidden error
**Validates: Requirements 4.4, 4.5**

### Property 9: Timestamp consistency
*For any* ticket update operation, the updated_at timestamp should be greater than or equal to the created_at timestamp
**Validates: Requirements 7.2**

### Property 10: Deletion cascade
*For any* issue, when the ticket is deleted, it should no longer appear in any user or admin queries
**Validates: Requirements 10.3, 10.4**

## Error Handling

### Validation Errors (400)
- Missing required fields
- Title exceeds 100 characters
- Description exceeds 2000 characters
- Invalid ticket type or status

### Authorization Errors (403)
- Non-owner accessing another user's issue
- Non-admin accessing admin endpoints
- Non-owner attempting to update another user's issue

### Not Found Errors (404)
- SupportTicket ID does not exist
- User has no tickets

### Server Errors (500)
- Database connection failures
- Unexpected exceptions

## Testing Strategy

### Unit Tests
- Schema validation (title/description length limits)
- Repository CRUD operations
- Service business logic
- Authorization checks

### Integration Tests
- API endpoint responses
- Database transactions
- User authentication flow
- Admin authorization flow

### Property-Based Tests
- Property 1: SupportTicket ownership validation
- Property 2: Status transition validity
- Property 4: Title length constraint
- Property 5: Description length constraint
- Property 6: Required field validation

### End-to-End Tests
- User creates ticket flow
- User views their tickets
- Admin resolves ticket flow
- SupportTicket deletion flow

## Security Considerations

1. **Authentication**: All endpoints require valid JWT token
2. **Authorization**: 
   - Users can only access their own issues
   - Admins can access all tickets
   - Only admins can resolve/reopen tickets
3. **Input Validation**: 
   - Length limits enforced at multiple layers
   - SQL injection prevented by SQLModel parameterization
   - XSS prevention through React's automatic escaping
4. **Rate Limiting**: Consider implementing rate limits on ticket creation to prevent spam
5. **Audit Trail**: All actions tracked with timestamps and user IDs

## Performance Considerations

1. **Database Indexes**:
   - user_id for fast user ticket queries
   - status for filtering
   - created_at for sorting
   - issue_type for admin filtering

2. **Pagination**: 
   - Default limit of 10 items per page
   - Maximum limit of 100 items per page

3. **Query Optimization**:
   - Use SELECT with specific columns
   - Avoid N+1 queries when fetching user details
   - Consider caching for admin statistics

4. **Frontend Optimization**:
   - React Query for caching and automatic refetching
   - Debounced search inputs
   - Virtual scrolling for large lists (if needed)

## Migration Strategy

1. Create database migration file for `issue` table
2. Deploy backend changes (models, schemas, routes, services, repositories)
3. Generate OpenAPI client for frontend
4. Deploy frontend components
5. Add navigation link to main menu
6. Update admin panel with new tickets section

## Future Enhancements

1. **Comments**: Allow users and admins to add comments to issues
2. **Attachments**: Support file uploads (screenshots for bugs)
3. **Email Notifications**: Notify users when their tickets are resolved
4. **Priority Levels**: Add priority field (Low, Medium, High, Critical)
5. **Labels/Tags**: Allow categorization with custom labels
6. **Search**: Full-text search across title and description
7. **Analytics**: Dashboard showing ticket trends and statistics
8. **Voting**: Allow users to upvote feature requests
9. **Duplicate Detection**: Suggest similar tickets before submission
10. **Export**: Export tickets to CSV or PDF

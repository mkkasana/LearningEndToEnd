# Design Document: Issue and Feature Request Tracking System

## Overview

The issue tracking system enables users to report bugs and request features while providing administrators with tools to manage and resolve these submissions. The system follows the existing application architecture with a React frontend, FastAPI backend, and PostgreSQL database.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
├─────────────────────────────────────────────────────────────┤
│  - IssuesPage (User view)                                   │
│  - CreateIssueDialog                                         │
│  - IssueListTable                                            │
│  - IssueDetailDialog                                         │
│  - AdminIssuesPanel (Admin view)                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│  Routes: /api/v1/issues                                     │
│  - POST   /issues (create)                                  │
│  - GET    /issues/me (user's issues)                        │
│  - GET    /issues/{id} (get single)                         │
│  - PATCH  /issues/{id} (update)                             │
│  - DELETE /issues/{id} (delete)                             │
│  - GET    /issues/admin/all (admin: all issues)            │
│  - PATCH  /issues/{id}/resolve (admin: mark resolved)      │
│  - PATCH  /issues/{id}/reopen (admin: reopen)              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
├─────────────────────────────────────────────────────────────┤
│  IssueService                                               │
│  - create_issue()                                           │
│  - get_user_issues()                                        │
│  - get_all_issues_admin()                                   │
│  - update_issue()                                           │
│  - resolve_issue()                                          │
│  - reopen_issue()                                           │
│  - delete_issue()                                           │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Repository Layer                            │
├─────────────────────────────────────────────────────────────┤
│  IssueRepository                                            │
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
│  Table: issue                                               │
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

**Table: issue**

```sql
CREATE TABLE issue (
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

CREATE INDEX idx_issue_user_id ON issue(user_id);
CREATE INDEX idx_issue_status ON issue(status);
CREATE INDEX idx_issue_created_at ON issue(created_at DESC);
CREATE INDEX idx_issue_type ON issue(issue_type);
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

**IssueCreate:**
```python
class IssueCreate(SQLModel):
    issue_type: IssueType
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=2000)
```

**IssueUpdate:**
```python
class IssueUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=2000)
```

**IssuePublic:**
```python
class IssuePublic(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    issue_type: IssueType
    title: str
    description: str
    status: IssueStatus
    resolved_by_user_id: uuid.UUID | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime
```

**IssuePublicWithUser:**
```python
class IssuePublicWithUser(IssuePublic):
    user_email: str
    user_full_name: str | None
    resolved_by_email: str | None
```

**IssuesPublicList:**
```python
class IssuesPublicList(SQLModel):
    data: list[IssuePublic]
    count: int
```

### Repository Layer

**IssueRepository:**
```python
class IssueRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, issue: Issue) -> Issue:
        """Create a new issue"""
        
    def get_by_id(self, issue_id: uuid.UUID) -> Issue | None:
        """Get issue by ID"""
        
    def get_by_user_id(
        self, 
        user_id: uuid.UUID, 
        status: IssueStatus | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Issue]:
        """Get all issues for a specific user with optional status filter"""
        
    def get_all(
        self,
        status: IssueStatus | None = None,
        issue_type: IssueType | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[Issue]:
        """Get all issues with optional filters (admin only)"""
        
    def update(self, issue: Issue) -> Issue:
        """Update an issue"""
        
    def delete(self, issue: Issue) -> None:
        """Delete an issue"""
        
    def count_by_user_id(self, user_id: uuid.UUID, status: IssueStatus | None = None) -> int:
        """Count issues for a user"""
        
    def count_all(self, status: IssueStatus | None = None, issue_type: IssueType | None = None) -> int:
        """Count all issues (admin only)"""
```

### Service Layer

**IssueService:**
```python
class IssueService:
    def __init__(self, session: Session):
        self.session = session
        self.issue_repo = IssueRepository(session)
    
    def create_issue(self, user_id: uuid.UUID, issue_in: IssueCreate) -> Issue:
        """Create a new issue for a user"""
        
    def get_user_issues(
        self, 
        user_id: uuid.UUID, 
        status: IssueStatus | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[Issue], int]:
        """Get all issues for a user with pagination"""
        
    def get_all_issues_admin(
        self,
        status: IssueStatus | None = None,
        issue_type: IssueType | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[list[Issue], int]:
        """Get all issues for admin with filters and pagination"""
        
    def get_issue_by_id(self, issue_id: uuid.UUID) -> Issue | None:
        """Get a single issue by ID"""
        
    def update_issue(self, issue: Issue, issue_in: IssueUpdate) -> Issue:
        """Update an issue"""
        
    def resolve_issue(self, issue: Issue, resolved_by_user_id: uuid.UUID) -> Issue:
        """Mark an issue as resolved"""
        
    def reopen_issue(self, issue: Issue) -> Issue:
        """Reopen a closed issue"""
        
    def delete_issue(self, issue: Issue) -> None:
        """Delete an issue"""
        
    def can_user_access_issue(self, issue: Issue, user_id: uuid.UUID, is_superuser: bool) -> bool:
        """Check if user can access an issue"""
```

### API Routes

**Endpoints:**

1. **POST /api/v1/issues** - Create new issue
   - Auth: Required
   - Body: IssueCreate
   - Returns: IssuePublic

2. **GET /api/v1/issues/me** - Get current user's issues
   - Auth: Required
   - Query params: status, skip, limit
   - Returns: IssuesPublicList

3. **GET /api/v1/issues/{issue_id}** - Get single issue
   - Auth: Required
   - Authorization: Owner or admin
   - Returns: IssuePublic

4. **PATCH /api/v1/issues/{issue_id}** - Update issue
   - Auth: Required
   - Authorization: Owner only
   - Body: IssueUpdate
   - Returns: IssuePublic

5. **DELETE /api/v1/issues/{issue_id}** - Delete issue
   - Auth: Required
   - Authorization: Owner or admin
   - Returns: Success message

6. **GET /api/v1/issues/admin/all** - Get all issues (admin)
   - Auth: Required (superuser)
   - Query params: status, issue_type, skip, limit
   - Returns: List[IssuePublicWithUser]

7. **PATCH /api/v1/issues/{issue_id}/resolve** - Mark resolved (admin)
   - Auth: Required (superuser)
   - Returns: IssuePublic

8. **PATCH /api/v1/issues/{issue_id}/reopen** - Reopen issue (admin)
   - Auth: Required (superuser)
   - Returns: IssuePublic

### Frontend Components

**1. IssuesPage (User View)**
- Location: `frontend/src/routes/issues.tsx`
- Features:
  - Tab navigation (All, Open, Closed)
  - Issue list table with pagination
  - "Report New Issue" button
  - Issue detail modal
  - Delete confirmation dialog

**2. CreateIssueDialog**
- Location: `frontend/src/components/Issues/CreateIssueDialog.tsx`
- Features:
  - Issue type selector (Bug/Feature Request)
  - Title input (max 100 chars with counter)
  - Description textarea (max 2000 chars with counter)
  - Form validation
  - Submit button

**3. IssueListTable**
- Location: `frontend/src/components/Issues/IssueListTable.tsx`
- Columns:
  - Issue # (auto-generated)
  - Type (icon badge)
  - Title
  - Status (badge)
  - Created Date
  - Actions (View, Delete)

**4. IssueDetailDialog**
- Location: `frontend/src/components/Issues/IssueDetailDialog.tsx`
- Displays:
  - Full title
  - Complete description
  - Issue type
  - Status
  - Created date
  - Updated date
  - Resolved date (if applicable)

**5. AdminIssuesPanel**
- Location: `frontend/src/components/Admin/AdminIssuesPanel.tsx`
- Features:
  - Filter by status and type
  - Sort by creation date (oldest first)
  - Shows submitter information
  - Resolve/Reopen buttons
  - Delete button
  - Pagination

## Data Models

### Issue Model (SQLModel)

```python
class Issue(SQLModel, table=True):
    __tablename__ = "issue"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    issue_type: IssueType
    title: str = Field(max_length=100)
    description: str = Field(max_length=2000)
    status: IssueStatus = Field(default=IssueStatus.OPEN, index=True)
    resolved_by_user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    resolved_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Issue ownership validation
*For any* issue and any user, when a non-admin user attempts to access an issue, access should only be granted if the user_id matches the issue's user_id
**Validates: Requirements 8.1, 8.2**

### Property 2: Status transition validity
*For any* issue, when the status changes from open to closed, the resolved_at timestamp should be set to the current time and resolved_by_user_id should be set
**Validates: Requirements 5.1, 5.3**

### Property 3: Status transition reversal
*For any* issue, when the status changes from closed to open, the resolved_at timestamp should be cleared (set to null) and resolved_by_user_id should be cleared
**Validates: Requirements 5.2, 5.3**

### Property 4: Title length constraint
*For any* issue creation or update, when the title exceeds 100 characters, the operation should be rejected with a validation error
**Validates: Requirements 2.1, 1.5**

### Property 5: Description length constraint
*For any* issue creation or update, when the description exceeds 2000 characters, the operation should be rejected with a validation error
**Validates: Requirements 2.2**

### Property 6: Required field validation
*For any* issue creation, when any required field (issue_type, title, description) is missing or empty, the operation should be rejected with a validation error
**Validates: Requirements 2.3, 2.4, 2.5**

### Property 7: User issue list isolation
*For any* user's issue list query, all returned issues should have a user_id matching the requesting user's ID
**Validates: Requirements 8.1**

### Property 8: Admin access privilege
*For any* admin-only operation, when a non-superuser attempts the operation, the system should return a 403 Forbidden error
**Validates: Requirements 4.4, 4.5**

### Property 9: Timestamp consistency
*For any* issue update operation, the updated_at timestamp should be greater than or equal to the created_at timestamp
**Validates: Requirements 7.2**

### Property 10: Deletion cascade
*For any* issue, when the issue is deleted, it should no longer appear in any user or admin queries
**Validates: Requirements 10.3, 10.4**

## Error Handling

### Validation Errors (400)
- Missing required fields
- Title exceeds 100 characters
- Description exceeds 2000 characters
- Invalid issue type or status

### Authorization Errors (403)
- Non-owner accessing another user's issue
- Non-admin accessing admin endpoints
- Non-owner attempting to update another user's issue

### Not Found Errors (404)
- Issue ID does not exist
- User has no issues

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
- Property 1: Issue ownership validation
- Property 2: Status transition validity
- Property 4: Title length constraint
- Property 5: Description length constraint
- Property 6: Required field validation

### End-to-End Tests
- User creates issue flow
- User views their issues
- Admin resolves issue flow
- Issue deletion flow

## Security Considerations

1. **Authentication**: All endpoints require valid JWT token
2. **Authorization**: 
   - Users can only access their own issues
   - Admins can access all issues
   - Only admins can resolve/reopen issues
3. **Input Validation**: 
   - Length limits enforced at multiple layers
   - SQL injection prevented by SQLModel parameterization
   - XSS prevention through React's automatic escaping
4. **Rate Limiting**: Consider implementing rate limits on issue creation to prevent spam
5. **Audit Trail**: All actions tracked with timestamps and user IDs

## Performance Considerations

1. **Database Indexes**:
   - user_id for fast user issue queries
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
6. Update admin panel with new issues section

## Future Enhancements

1. **Comments**: Allow users and admins to add comments to issues
2. **Attachments**: Support file uploads (screenshots for bugs)
3. **Email Notifications**: Notify users when their issues are resolved
4. **Priority Levels**: Add priority field (Low, Medium, High, Critical)
5. **Labels/Tags**: Allow categorization with custom labels
6. **Search**: Full-text search across title and description
7. **Analytics**: Dashboard showing issue trends and statistics
8. **Voting**: Allow users to upvote feature requests
9. **Duplicate Detection**: Suggest similar issues before submission
10. **Export**: Export issues to CSV or PDF

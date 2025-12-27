# Implementation Plan: Issue and Feature Request Tracking System

## Task Overview

This implementation plan follows a bottom-up approach: database → backend (models, schemas, repository, service, routes) → frontend (components, pages, routing) → integration and testing.

**Current Status:** No implementation has started. All tasks need to be completed.

---

## Backend Implementation

### 1. Database Schema and Migration
- [ ] 1. Database Schema and Migration
 - [ ] 1.1 Create database migration file for issue table
  - Create Alembic migration file in `backend/app/alembic/versions/`
  - Define issue table with all columns: id, user_id, issue_type, title, description, status, resolved_by_user_id, resolved_at, created_at, updated_at
  - Add foreign key constraints to user table with ON DELETE CASCADE for user_id
  - Add check constraints for issue_type ('bug', 'feature_request') and status ('open', 'closed') enums
  - Add check constraint for description length (max 2000 chars)
  - Create indexes on user_id, status, created_at DESC, and issue_type
  - _Requirements: 1.1, 2.1, 2.2, 7.1_

### 2. Backend Models and Schemas
- [ ] 2. Backend Models and Schemas
 - [ ] 2.1 Create Issue database model
  - Create `backend/app/db_models/issue.py`
  - Define Issue SQLModel class with all fields matching the migration
  - Add table=True configuration with __tablename__ = "issue"
  - Define field constraints (max_length for title, foreign keys, defaults)
  - Follow the pattern from `backend/app/db_models/post.py`
  - _Requirements: 1.1, 2.1, 2.2, 7.1_

 - [ ] 2.2 Create Issue Pydantic schemas
  - Create `backend/app/schemas/issue.py`
  - Define IssueType enum (bug, feature_request)
  - Define IssueStatus enum (open, closed)
  - Define IssueCreate schema with Field validation (title max 100, description max 2000)
  - Define IssueUpdate schema (all fields optional)
  - Define IssuePublic schema (response model)
  - Define IssuePublicWithUser schema (includes user_email, user_full_name, resolved_by_email)
  - Define IssuesPublic schema for pagination (data: list, count: int)
  - Follow the pattern from `backend/app/schemas/post.py`
  - _Requirements: 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 6.1_

### 3. Repository Layer
- [ ] 3. Repository Layer
 - [ ] 3.1 Create IssueRepository class
  - Create `backend/app/repositories/issue_repository.py`
  - Extend BaseRepository[Issue] (follow pattern from PostRepository)
  - Implement get_by_user_id() method with optional status filter and pagination
  - Implement get_all() method with filters (status, issue_type) and pagination
  - Implement count_by_user_id() method with optional status filter
  - Implement count_all() method with optional filters
  - Use SQLModel select() with where(), order_by(), offset(), limit()
  - _Requirements: 1.1, 3.1, 3.2, 4.1, 8.1, 9.1_

### 4. Service Layer
- [ ] 4. Service Layer
 - [ ] 4.1 Create IssueService class
  - Create `backend/app/services/issue_service.py`
  - Initialize with session and IssueRepository
  - Implement create_issue() method (creates Issue with status='open')
  - Implement get_user_issues() method with pagination (returns tuple[list[Issue], int])
  - Implement get_all_issues_admin() method with filters and pagination
  - Implement get_issue_by_id() method
  - Implement update_issue() method (updates title/description, sets updated_at)
  - Implement resolve_issue() method (sets status='closed', resolved_at=now, resolved_by_user_id)
  - Implement reopen_issue() method (sets status='open', clears resolved_at and resolved_by_user_id)
  - Implement delete_issue() method
  - Implement can_user_access_issue() helper (returns True if owner or superuser)
  - Follow the pattern from `backend/app/services/post_service.py`
  - _Requirements: 1.1, 1.4, 3.1, 4.1, 5.1, 5.2, 5.3, 8.1, 8.2, 10.3_

 - [ ] 4.2 Write property test for issue ownership validation
  - Create `backend/tests/services/test_issue_service.py`
  - **Property 1: Issue ownership validation**
  - **Validates: Requirements 8.1, 8.2**
  - Generate random issues and users
  - Test that non-admin users can only access their own issues via can_user_access_issue()
  - Test that admins can access all issues
  - Use pytest with hypothesis for property-based testing
  - Run minimum 100 iterations

 - [ ] 4.3 Write property test for status transitions
  - Add to `backend/tests/services/test_issue_service.py`
  - **Property 2: Status transition validity**
  - **Validates: Requirements 5.1, 5.3**
  - Generate random open issues
  - Test that resolve_issue() sets resolved_at (not None) and resolved_by_user_id
  - **Property 3: Status transition reversal**
  - **Validates: Requirements 5.2, 5.3**
  - Test that reopen_issue() clears resolved_at (sets to None) and resolved_by_user_id (sets to None)
  - Run minimum 100 iterations

### 5. API Routes
- [ ] 5. API Routes
 - [ ] 5.1 Create issue API routes file
  - Create `backend/app/api/routes/issues.py`
  - Set up APIRouter with prefix="/issues" and tags=["issues"]
  - Import dependencies (SessionDep, CurrentUser, get_current_active_superuser)
  - Follow the pattern from `backend/app/api/routes/posts.py`
  - _Requirements: 1.1_

 - [ ] 5.2 Implement user issue endpoints
  - POST /issues - Create new issue (authenticated users)
  - GET /issues/me - Get current user's issues with query params (status, skip, limit)
  - GET /issues/{issue_id} - Get single issue (check ownership with can_user_access_issue)
  - PATCH /issues/{issue_id} - Update issue (owner only, check user_id match)
  - DELETE /issues/{issue_id} - Delete issue (owner or admin)
  - Add proper error handling (400 validation, 403 forbidden, 404 not found)
  - Return appropriate response models (IssuePublic, IssuesPublic, Message)
  - _Requirements: 1.1, 1.4, 3.1, 3.3, 8.1, 8.2, 8.3, 10.1, 10.2, 10.3_

 - [ ] 5.3 Implement admin issue endpoints
  - GET /issues/admin/all - Get all issues with filters (superuser only, use get_current_active_superuser dependency)
  - PATCH /issues/{issue_id}/resolve - Mark issue as resolved (superuser only)
  - PATCH /issues/{issue_id}/reopen - Reopen closed issue (superuser only)
  - Return IssuePublicWithUser for admin endpoints (includes user details)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.4, 5.5_

 - [ ] 5.4 Write property test for validation constraints
  - Create `backend/tests/api/test_issues_api.py`
  - **Property 4: Title length constraint**
  - **Validates: Requirements 2.1, 1.5**
  - Generate random titles of various lengths
  - Test that POST /issues with title > 100 chars returns 422 validation error
  - **Property 5: Description length constraint**
  - **Validates: Requirements 2.2**
  - Test that POST /issues with description > 2000 chars returns 422 validation error
  - **Property 6: Required field validation**
  - **Validates: Requirements 2.3, 2.4, 2.5**
  - Test that POST /issues with missing required fields returns 422 validation error
  - Use pytest with hypothesis
  - Run minimum 100 iterations

 - [ ] 5.5 Register issue routes in main API router
  - Update `backend/app/api/main.py`
  - Import issues router: `from app.api.routes import issues`
  - Add to api_router: `api_router.include_router(issues.router)`
  - _Requirements: 1.1_

### 6. Backend Checkpoint
- [ ] 6. Backend Checkpoint
 - [ ] 6.1 Ensure all backend tests pass
  - Run all property-based tests (pytest backend/tests/services/test_issue_service.py backend/tests/api/test_issues_api.py)
  - Verify all properties pass with 100+ iterations
  - Test API endpoints manually via Swagger UI at http://localhost:8000/docs
  - Verify database migration applied successfully
  - Fix any failing tests before proceeding to frontend

---

## Frontend Implementation

### 7. Generate OpenAPI Client
- [ ] 7. Generate OpenAPI Client
 - [ ] 7.1 Generate TypeScript client from OpenAPI spec
  - Run `npm run generate-client` in frontend directory
  - Verify new IssuesService is generated in `frontend/src/client/`
  - Check `frontend/src/client/schemas.gen.ts` for Issue types (IssuePublic, IssueCreate, etc.)
  - Verify IssueType and IssueStatus enums are generated
  - _Requirements: 1.1_

### 8. Create Issue Dialog Component
- [ ] 8. Create Issue Dialog Component
 - [ ] 8.1 Create CreateIssueDialog component
  - Create `frontend/src/components/Issues/CreateIssueDialog.tsx`
  - Implement dialog with form using shadcn/ui Dialog, Form components
  - Add issue type selector (Bug/Feature Request) using Select or RadioGroup
  - Add title input with max 100 chars and character counter
  - Add description textarea with max 2000 chars and character counter
  - Add Zod schema validation matching backend constraints
  - Implement form submission with IssuesService.createIssue()
  - Add loading state during submission
  - Show success toast on creation using useToast
  - Handle errors and display error messages
  - Close dialog and invalidate queries on success
  - _Requirements: 1.3, 2.1, 2.2, 2.3, 2.4, 2.5_

### 9. Create Issue List Components
- [ ] 9. Create Issue List Components
 - [ ] 9.1 Create IssueListTable component
  - Create `frontend/src/components/Issues/IssueListTable.tsx`
  - Display issues in table format using shadcn/ui Table or DataTable
  - Columns: Issue # (auto-generated from index), Type badge, Title, Status badge, Created date, Actions
  - Add Badge component for issue type (Bug/Feature Request with different colors)
  - Add Badge component for status (Open/Closed with different colors)
  - Format dates using date-fns or similar
  - Add "View Details" button for each issue (opens IssueDetailDialog)
  - Add "Delete" button with confirmation using AlertDialog
  - Handle empty state (no issues) with appropriate message
  - Implement pagination controls if count > limit
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 10.1, 10.2_

 - [ ] 9.2 Create IssueDetailDialog component
  - Create `frontend/src/components/Issues/IssueDetailDialog.tsx`
  - Display full issue details in a Dialog
  - Show: Title (heading), Full description, Type badge, Status badge
  - Show timestamps: Created date, Updated date, Resolved date (if status is closed)
  - Format dates in readable format
  - Add close button
  - Make description scrollable if long
  - _Requirements: 3.3, 7.4_

### 10. Create User Issues Page
- [ ] 10. Create User Issues Page
 - [ ] 10.1 Create IssuesPage route component
  - Create `frontend/src/routes/_layout/issues.tsx`
  - Use createFileRoute from @tanstack/react-router
  - Implement tab navigation (All, Open, Closed) using shadcn/ui Tabs
  - Fetch user's issues using useSuspenseQuery with IssuesService.getMyIssues()
  - Implement status filtering based on active tab (pass status param to API)
  - Add "Report New Issue" button that opens CreateIssueDialog
  - Integrate IssueListTable component to display issues
  - Integrate IssueDetailDialog component (controlled by state)
  - Use React Query for data fetching and caching
  - Implement query invalidation after create/delete using queryClient.invalidateQueries
  - Add Suspense boundary with loading fallback
  - Follow the pattern from `frontend/src/routes/_layout/admin.tsx`
  - _Requirements: 1.1, 1.2, 3.1, 9.1, 9.2, 9.3_

### 11. Create Admin Issues Panel
- [ ] 11. Create Admin Issues Panel
 - [ ] 11.1 Create AdminIssuesPanel component
  - Create `frontend/src/components/Admin/AdminIssuesPanel.tsx`
  - Fetch all issues using useSuspenseQuery with IssuesService.getAdminAllIssues()
  - Display issues in table with columns: Issue #, Submitter (email/name), Type, Title, Status, Created date, Actions
  - Sort by creation date (oldest first) - handle in query or component
  - Add filter controls using Select components (status: All/Open/Closed, type: All/Bug/Feature)
  - Add "Mark Resolved" button for open issues (calls IssuesService.resolveIssue)
  - Add "Reopen" button for closed issues (calls IssuesService.reopenIssue)
  - Add "Delete" button with AlertDialog confirmation
  - Implement pagination if needed
  - Show issue statistics at top: Total open bugs, Total open feature requests (calculate from data)
  - Invalidate queries after resolve/reopen/delete actions
  - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.4, 5.5, 6.3, 6.5_

 - [ ] 11.2 Integrate AdminIssuesPanel into Admin page
  - Update `frontend/src/routes/_layout/admin.tsx`
  - Add new section for "Issue Management" below or above Users section
  - Add heading "Issue Management" or "User Issues"
  - Integrate AdminIssuesPanel component with Suspense boundary
  - Ensure proper authorization (page already requires superuser)
  - _Requirements: 4.1, 4.4, 4.5_

### 12. Add Navigation
- [ ] 12. Add Navigation
 - [ ] 12.1 Add "Report Issue" to main navigation
  - Update `frontend/src/components/Sidebar/AppSidebar.tsx`
  - Import appropriate icon from lucide-react (e.g., Bug, MessageSquareWarning, or AlertCircle)
  - Add new item to baseItems array: `{ icon: Bug, title: "Report Issue", path: "/issues" }`
  - Place after "Update Family" and before "Admin" in the menu
  - _Requirements: 1.1_

### 13. Frontend Checkpoint
- [ ] 13. Frontend Checkpoint
 - [ ] 13.1 Ensure all frontend functionality works
  - Manually test user issue flow: create issue, view in list, view details, delete issue
  - Test tab filtering (All, Open, Closed)
  - Test character counters in create dialog
  - Test form validation (empty fields, too long title/description)
  - Manually test admin issue flow: view all issues, filter by status/type, resolve issue, reopen issue, delete issue
  - Verify issue statistics display correctly
  - Test responsive design on mobile and desktop
  - Verify pagination works if applicable
  - Check that navigation link appears and works

---

## Final Integration

### 14. End-to-End Verification
- [ ] 14. End-to-End Verification
 - [ ] 14.1 Perform complete system test
  - Test complete user flow: register → login → create issue → view issues → delete issue
  - Test complete admin flow: login as admin → view all issues → resolve issue → reopen issue → delete issue
  - Test authorization: verify non-admin cannot access admin endpoints (403 error)
  - Test edge cases: empty states, long text, special characters in title/description
  - Verify all timestamps display correctly
  - Verify issue counts and statistics are accurate
  - Test with multiple users to ensure isolation (users only see their own issues)
  - _Requirements: 1.1, 1.4, 4.1, 5.1, 8.1_

---

## Summary

This implementation plan creates a complete issue tracking system with:

**Backend (Tasks 1-6):**
- Database schema with proper constraints and indexes
- Repository layer for data access
- Service layer with business logic and authorization
- RESTful API with 8 endpoints
- Property-based testing for correctness properties

**Frontend (Tasks 7-13):**
- User interface for reporting and viewing issues
- Admin panel for managing all issues
- Form validation with character counters
- Filtering, sorting, and pagination
- Responsive design

**Integration (Task 14):**
- End-to-end verification

The system follows the existing application architecture and patterns, ensuring consistency and maintainability.

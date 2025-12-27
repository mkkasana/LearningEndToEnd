# Implementation Plan: Support Ticket and Feature Request Tracking System

## Task Overview

This implementation plan follows a bottom-up approach: database → backend (models, schemas, repository, service, routes) → frontend (components, pages, routing) → integration and testing.

**Current Status:** No implementation has started. All tasks need to be completed.

---

## Backend Implementation

### 1. Database Schema and Migration
- [x] 1. Database Schema and Migration
 - [x] 1.1 Create database migration file for ticket table
  - Create Alembic migration file in `backend/app/alembic/versions/`
  - Define ticket table with all columns: id, user_id, issue_type, title, description, status, resolved_by_user_id, resolved_at, created_at, updated_at
  - Add foreign key constraints to user table with ON DELETE CASCADE for user_id
  - Add check constraints for issue_type ('bug', 'feature_request') and status ('open', 'closed') enums
  - Add check constraint for description length (max 2000 chars)
  - Create indexes on user_id, status, created_at DESC, and issue_type
  - _Requirements: 1.1, 2.1, 2.2, 7.1_

 - [x] 1.2 Commit database migration changes

### 2. Backend Models and Schemas
- [x] 2. Backend Models and Schemas
 - [x] 2.1 Create SupportTicket database model
  - Create `backend/app/db_models/support_ticket.py`
  - Define SupportTicket SQLModel class with all fields matching the migration
  - Add table=True configuration with __tablename__ = "support_ticket"
  - Define field constraints (max_length for title, foreign keys, defaults)
  - Follow the pattern from `backend/app/db_models/post.py`
  - _Requirements: 1.1, 2.1, 2.2, 7.1_

 - [x] 2.2 Create SupportTicket Pydantic schemas
  - Create `backend/app/schemas/support_ticket.py`
  - Define IssueType enum (bug, feature_request)
  - Define IssueStatus enum (open, closed)
  - Define SupportTicketCreate schema with Field validation (title max 100, description max 2000)
  - Define SupportTicketUpdate schema (all fields optional)
  - Define SupportTicketPublic schema (response model)
  - Define SupportTicketPublicWithUser schema (includes user_email, user_full_name, resolved_by_email)
  - Define SupportTicketsPublic schema for pagination (data: list, count: int)
  - Follow the pattern from `backend/app/schemas/post.py`
  - _Requirements: 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 6.1_

 - [x] 2.3 Commit backend models and schemas

### 3. Repository Layer
- [x] 3. Repository Layer
 - [x] 3.1 Create SupportTicketRepository class
  - Create `backend/app/repositories/support_ticket_repository.py`
  - Extend BaseRepository[SupportTicket] (follow pattern from PostRepository)
  - Implement get_by_user_id() method with optional status filter and pagination
  - Implement get_all() method with filters (status, issue_type) and pagination
  - Implement count_by_user_id() method with optional status filter
  - Implement count_all() method with optional filters
  - Use SQLModel select() with where(), order_by(), offset(), limit()
  - _Requirements: 1.1, 3.1, 3.2, 4.1, 8.1, 9.1_

 - [x] 3.2 Commit repository layer

### 4. Service Layer
- [ ] 4. Service Layer
 - [x] 4.1 Create SupportTicketService class
  - Create `backend/app/services/support_ticket_service.py`
  - Initialize with session and SupportTicketRepository
  - Implement create_support_ticket() method (creates SupportTicket with status='open')
  - Implement get_user_support_tickets() method with pagination (returns tuple[list[SupportTicket], int])
  - Implement get_all_support_tickets_admin() method with filters and pagination
  - Implement get_support_ticket_by_id() method
  - Implement update_support_ticket() method (updates title/description, sets updated_at)
  - Implement resolve_support_ticket() method (sets status='closed', resolved_at=now, resolved_by_user_id)
  - Implement reopen_support_ticket() method (sets status='open', clears resolved_at and resolved_by_user_id)
  - Implement delete_support_ticket() method
  - Implement can_user_access_support_ticket() helper (returns True if owner or superuser)
  - Follow the pattern from `backend/app/services/post_service.py`
  - _Requirements: 1.1, 1.4, 3.1, 4.1, 5.1, 5.2, 5.3, 8.1, 8.2, 10.3_

 - [x] 4.2 Write property test for ticket ownership validation
  - Create `backend/tests/services/test_support_ticket_service.py`
  - **Property 1: SupportTicket ownership validation**
  - **Validates: Requirements 8.1, 8.2**
  - Generate random tickets and users
  - Test that non-admin users can only access their own tickets via can_user_access_support_ticket()
  - Test that admins can access all tickets
  - Use pytest with hypothesis for property-based testing
  - Run minimum 100 iterations

 - [x] 4.3 Write property test for status transitions
  - Add to `backend/tests/services/test_support_ticket_service.py`
  - **Property 2: Status transition validity**
  - **Validates: Requirements 5.1, 5.3**
  - Generate random open tickets
  - Test that resolve_support_ticket() sets resolved_at (not None) and resolved_by_user_id
  - **Property 3: Status transition reversal**
  - **Validates: Requirements 5.2, 5.3**
  - Test that reopen_support_ticket() clears resolved_at (sets to None) and resolved_by_user_id (sets to None)
  - Run minimum 100 iterations

 - [x] 4.4 Commit service layer and tests

### 5. API Routes
- [x] 5. API Routes
 - [x] 5.1 Create ticket API routes file
  - Create `backend/app/api/routes/support-tickets.py`
  - Set up APIRouter with prefix="/support-tickets" and tags=["issues"]
  - Import dependencies (SessionDep, CurrentUser, get_current_active_superuser)
  - Follow the pattern from `backend/app/api/routes/posts.py`
  - _Requirements: 1.1_

 - [x] 5.2 Implement user ticket endpoints
  - POST /support-tickets - Create new ticket (authenticated users)
  - GET /support-tickets/me - Get current user's tickets with query params (status, skip, limit)
  - GET /support-tickets/{support_ticket_id} - Get single ticket (check ownership with can_user_access_support_ticket)
  - PATCH /support-tickets/{support_ticket_id} - Update ticket (owner only, check user_id match)
  - DELETE /support-tickets/{support_ticket_id} - Delete ticket (owner or admin)
  - Add proper error handling (400 validation, 403 forbidden, 404 not found)
  - Return appropriate response models (SupportTicketPublic, SupportTicketsPublic, Message)
  - _Requirements: 1.1, 1.4, 3.1, 3.3, 8.1, 8.2, 8.3, 10.1, 10.2, 10.3_

 - [x] 5.3 Implement admin ticket endpoints
  - GET /support-tickets/admin/all - Get all tickets with filters (superuser only, use get_current_active_superuser dependency)
  - PATCH /support-tickets/{support_ticket_id}/resolve - Mark ticket as resolved (superuser only)
  - PATCH /support-tickets/{support_ticket_id}/reopen - Reopen closed ticket (superuser only)
  - Return SupportTicketPublicWithUser for admin endpoints (includes user details)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.4, 5.5_

 - [x] 5.4 Write property test for validation constraints
  - Create `backend/tests/api/test_support_tickets_api.py`
  - **Property 4: Title length constraint**
  - **Validates: Requirements 2.1, 1.5**
  - Generate random titles of various lengths
  - Test that POST /support-tickets with title > 100 chars returns 422 validation error
  - **Property 5: Description length constraint**
  - **Validates: Requirements 2.2**
  - Test that POST /support-tickets with description > 2000 chars returns 422 validation error
  - **Property 6: Required field validation**
  - **Validates: Requirements 2.3, 2.4, 2.5**
  - Test that POST /support-tickets with missing required fields returns 422 validation error
  - Use pytest with hypothesis
  - Run minimum 100 iterations

 - [x] 5.5 Register ticket routes in main API router
  - Update `backend/app/api/main.py`
  - Import tickets router: `from app.api.routes import issues`
  - Add to api_router: `api_router.include_router(issues.router)`
  - _Requirements: 1.1_

 - [x] 5.6 Git Commit API routes and tests changes

### 6. Backend Checkpoint
- [x] 6. Backend Checkpoint
 - [ ] 6.1 Ensure all backend tests pass
  - Run all property-based tests (pytest backend/tests/services/test_support_ticket_service.py backend/tests/api/test_support_tickets_api.py)
  - Verify all properties pass with 100+ iterations
  - Test API endpoints manually via Swagger UI at http://localhost:8000/docs
  - Verify database migration applied successfully
  - Fix any failing tests before proceeding to frontend

---

## Frontend Implementation

### 7. Generate OpenAPI Client
- [x] 7. Generate OpenAPI Client
 - [x] 7.1 Generate TypeScript client from OpenAPI spec
  - Run `npm run generate-client` in frontend directory
  - Verify new SupportTicketsService is generated in `frontend/src/client/`
  - Check `frontend/src/client/schemas.gen.ts` for SupportTicket types (SupportTicketPublic, SupportTicketCreate, etc.)
  - Verify IssueType and IssueStatus enums are generated
  - _Requirements: 1.1_

 - [x] 7.2 Git Commit generated OpenAPI client
 
### 8. Create SupportTicket Dialog Component
- [x] 8. Create SupportTicket Dialog Component
 - [x] 8.1 Create CreateSupportTicketDialog component
  - Create `frontend/src/components/SupportTickets/CreateSupportTicketDialog.tsx`
  - Implement dialog with form using shadcn/ui Dialog, Form components
  - Add ticket type selector (Bug/Feature Request) using Select or RadioGroup
  - Add title input with max 100 chars and character counter
  - Add description textarea with max 2000 chars and character counter
  - Add Zod schema validation matching backend constraints
  - Implement form submission with SupportTicketsService.createIssue()
  - Add loading state during submission
  - Show success toast on creation using useToast
  - Handle errors and display error messages
  - Close dialog and invalidate queries on success
  - _Requirements: 1.3, 2.1, 2.2, 2.3, 2.4, 2.5_

 - [x] 8.2 Git Commit create dialog component related changes

### 9. Create SupportTicket List Components
- [x] 9. Create SupportTicket List Components
 - [x] 9.1 Create SupportTicketListTable component
  - Create `frontend/src/components/SupportTickets/SupportTicketListTable.tsx`
  - Display tickets in table format using shadcn/ui Table or DataTable
  - Columns: SupportTicket # (auto-generated from index), Type badge, Title, Status badge, Created date, Actions
  - Add Badge component for ticket type (Bug/Feature Request with different colors)
  - Add Badge component for status (Open/Closed with different colors)
  - Format dates using date-fns or similar
  - Add "View Details" button for each ticket (opens SupportTicketDetailDialog)
  - Add "Delete" button with confirmation using AlertDialog
  - Handle empty state (no tickets) with appropriate message
  - Implement pagination controls if count > limit
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 10.1, 10.2_

 - [x] 9.2 Create SupportTicketDetailDialog component
  - Create `frontend/src/components/SupportTickets/SupportTicketDetailDialog.tsx`
  - Display full ticket details in a Dialog
  - Show: Title (heading), Full description, Type badge, Status badge
  - Show timestamps: Created date, Updated date, Resolved date (if status is closed)
  - Format dates in readable format
  - Add close button
  - Make description scrollable if long
  - _Requirements: 3.3, 7.4_

 - [x] 9.3 Git Commit list components related changes

### 10. Create User Issues Page
- [x] 10. Create User Issues Page
 - [x] 10.1 Create SupportTicketsPage route component
  - Create `frontend/src/routes/_layout/support-tickets.tsx`
  - Use createFileRoute from @tanstack/react-router
  - Implement tab navigation (All, Open, Closed) using shadcn/ui Tabs
  - Fetch user's tickets using useSuspenseQuery with SupportTicketsService.getMyIssues()
  - Implement status filtering based on active tab (pass status param to API)
  - Add "Report New Ticket" button that opens CreateSupportTicketDialog
  - Integrate SupportTicketListTable component to display issues
  - Integrate SupportTicketDetailDialog component (controlled by state)
  - Use React Query for data fetching and caching
  - Implement query invalidation after create/delete using queryClient.invalidateQueries
  - Add Suspense boundary with loading fallback
  - Follow the pattern from `frontend/src/routes/_layout/admin.tsx`
  - _Requirements: 1.1, 1.2, 3.1, 9.1, 9.2, 9.3_

 - [x] 10.2 Git Commit user tickets page related changes

### 11. Create Admin Issues Panel
- [x] 11. Create Admin Issues Panel
 - [x] 11.1 Create AdminSupportTicketsPanel component
  - Create `frontend/src/components/Admin/AdminSupportTicketsPanel.tsx`
  - Fetch all tickets using useSuspenseQuery with SupportTicketsService.getAdminAllIssues()
  - Display tickets in table with columns: SupportTicket #, Submitter (email/name), Type, Title, Status, Created date, Actions
  - Sort by creation date (oldest first) - handle in query or component
  - Add filter controls using Select components (status: All/Open/Closed, type: All/Bug/Feature)
  - Add "Mark Resolved" button for open tickets (calls SupportTicketsService.resolveSupportTicket)
  - Add "Reopen" button for closed tickets (calls SupportTicketsService.reopenSupportTicket)
  - Add "Delete" button with AlertDialog confirmation
  - Implement pagination if needed
  - Show ticket statistics at top: Total open bugs, Total open feature requests (calculate from data)
  - Invalidate queries after resolve/reopen/delete actions
  - _Requirements: 4.1, 4.2, 4.3, 5.1, 5.2, 5.4, 5.5, 6.3, 6.5_

 - [x] 11.2 Integrate AdminSupportTicketsPanel into Admin page
  - Update `frontend/src/routes/_layout/admin.tsx`
  - Add new section for "Issue Management" below or above Users section
  - Add heading "Issue Management" or "User Issues"
  - Integrate AdminSupportTicketsPanel component with Suspense boundary
  - Ensure proper authorization (page already requires superuser)
  - _Requirements: 4.1, 4.4, 4.5_

 - [x] 11.3 Git Commit admin panel components related changes

### 12. Add Navigation
- [x] 12. Add Navigation
 - [x] 12.1 Add "Report Ticket" to main navigation
  - Update `frontend/src/components/Sidebar/AppSidebar.tsx`
  - Import appropriate icon from lucide-react (e.g., Bug, MessageSquareWarning, or AlertCircle)
  - Add new item to baseItems array: `{ icon: Bug, title: "Report Ticket", path: "/support-tickets" }`
  - Place after "Update Family" and before "Admin" in the menu
  - _Requirements: 1.1_

 - [x] 12.2 Git Commit navigation changes related changes

### 13. Frontend Checkpoint
- [x] 13. Frontend Checkpoint
 - [x] 13.1 Ensure all frontend functionality works
  - Manually test user ticket flow: create issue, view in list, view details, delete issue
  - Command to deep restart components "docker compose down && docker rmi backend:latest && docker rmi frontend:latest && docker compose build --no-cache && docker compose up -d "
  - Test tab filtering (All, Open, Closed)
  - Test character counters in create dialog
  - Test form validation (empty fields, too long title/description)
  - Manually test admin ticket flow: view all tickets, filter by status/type, resolve issue, reopen issue, delete issue
  - Verify ticket statistics display correctly
  - Test responsive design on mobile and desktop
  - Verify pagination works if applicable
  - Check that navigation link appears and works

---

## Final Integration

### 14. End-to-End Verification
- [x] 14. End-to-End Verification
 - [x] 14.1 Perform complete system test
  - Test complete user flow: register → login → create ticket → view tickets → delete issue
  - Test complete admin flow: login as admin → view all tickets → resolve ticket → reopen ticket → delete issue
  - Test authorization: verify non-admin cannot access admin endpoints (403 error)
  - Test edge cases: empty states, long text, special characters in title/description
  - Verify all timestamps display correctly
  - Verify ticket counts and statistics are accurate
  - Test with multiple users to ensure isolation (users only see their own issues)
  - _Requirements: 1.1, 1.4, 4.1, 5.1, 8.1_

 - [x] 14.2 Final git commit for end-to-end verification

---

## Summary

This implementation plan creates a complete ticket tracking system with:

**Backend (Tasks 1-6):**
- Database schema with proper constraints and indexes
- Repository layer for data access
- Service layer with business logic and authorization
- RESTful API with 8 endpoints
- Property-based testing for correctness properties

**Frontend (Tasks 7-13):**
- User interface for reporting and viewing issues
- Admin panel for managing all tickets
- Form validation with character counters
- Filtering, sorting, and pagination
- Responsive design

**Integration (Task 14):**
- End-to-end verification

The system follows the existing application architecture and patterns, ensuring consistency and maintainability.

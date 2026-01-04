# Design Document: Person Life Events

## Overview

This design describes the implementation of a Life Events feature that allows users to record and manage significant milestones in their lives. The feature follows the existing patterns in the codebase (similar to Items, PersonAddress) and includes a multi-step wizard UI similar to AddFamilyMemberDialog.

The implementation spans:
- Backend: Database model, schemas, repository, service, and API routes
- Frontend: Page component, multi-step dialog, list display with CRUD actions

## Architecture

The system follows a layered architecture:

1. Frontend Layer: React components with TanStack Query for data fetching
2. API Layer: FastAPI routes handling HTTP requests
3. Service Layer: Business logic and validation
4. Repository Layer: Database access using SQLModel
5. Database Layer: PostgreSQL with person_life_event table

Data Flow:
- User interacts with Life Events Page or Dialog
- Frontend calls LifeEventsService (auto-generated client)
- Backend routes delegate to LifeEventService
- Service uses LifeEventRepository for database operations
- Events are stored in person_life_event table with FKs to person and address tables

## Components and Interfaces

### Backend Components

#### 1. Database Model: PersonLifeEvent

Location: backend/app/db_models/person/person_life_event.py

Fields:
- id: UUID (primary key)
- person_id: UUID (FK to person.id, indexed)
- event_type: str (max 50 chars, enum value)
- title: str (max 100 chars)
- description: str or None (max 500 chars)
- event_year: int (required)
- event_month: int or None (1-12)
- event_date: int or None (1-31)
- country_id: UUID or None (FK to address_country.id)
- state_id: UUID or None (FK to address_state.id)
- district_id: UUID or None (FK to address_district.id)
- sub_district_id: UUID or None (FK to address_sub_district.id)
- locality_id: UUID or None (FK to address_locality.id)
- address_details: str or None (max 30 chars)
- created_at: datetime
- updated_at: datetime

#### 2. Event Type Enum

Location: backend/app/schemas/person/life_event.py

Values: birth, marriage, death, purchase, sale, achievement, education, career, health, travel, other

#### 3. Schemas

Location: backend/app/schemas/person/life_event.py

- LifeEventBase: Shared properties
- LifeEventCreate: For creating events (extends Base)
- LifeEventUpdate: For updating events (all fields optional)
- LifeEventPublic: Response schema with id, person_id, timestamps
- LifeEventsPublic: List response with data array and count

#### 4. Repository

Location: backend/app/repositories/person/life_event_repository.py

Methods:
- get_by_person(person_id, skip, limit): Get events sorted by date DESC
- count_by_person(person_id): Count events for a person

#### 5. Service

Location: backend/app/services/person/life_event_service.py

Methods:
- get_life_events(person_id, skip, limit): Returns tuple of events list and count
- get_life_event_by_id(event_id): Returns event or None
- create_life_event(data, person_id): Creates and returns new event
- update_life_event(event, data): Updates and returns event
- delete_life_event(event): Deletes event
- user_can_access_event(user, event): Authorization check
- validate_date(year, month, date): Date validation

#### 6. API Routes

Location: backend/app/api/routes/life_events.py

Endpoints:
- GET /api/v1/life-events/me - Get current user's life events
- POST /api/v1/life-events/ - Create a new life event
- GET /api/v1/life-events/{id} - Get a specific life event
- PUT /api/v1/life-events/{id} - Update a life event
- DELETE /api/v1/life-events/{id} - Delete a life event

### Frontend Components

#### 1. Life Events Page

Location: frontend/src/routes/_layout/life-events.tsx

- Displays page header with "Add Life Event" button
- Shows list of events using DataTable or custom list component
- Handles empty state

#### 2. Add/Edit Life Event Dialog

Location: frontend/src/components/LifeEvents/AddLifeEventDialog.tsx

Multi-step wizard with 3 steps:
- Step 1 - Event Details: Event type, title, description, date fields
- Step 2 - Location: Address fields (pre-populated from person's address)
- Step 3 - Confirmation: Summary and submit

#### 3. Event Actions Menu

Location: frontend/src/components/LifeEvents/LifeEventActionsMenu.tsx

- Edit action: Opens edit dialog
- Delete action: Shows confirmation dialog

#### 4. Sidebar Update

Location: frontend/src/components/Sidebar/AppSidebar.tsx

Add new sidebar item with Calendar icon, title "Life Events", path "/life-events"

## Data Models

### Database Schema (SQL)

Table: person_life_event
- id UUID PRIMARY KEY
- person_id UUID NOT NULL (FK to person, ON DELETE CASCADE)
- event_type VARCHAR(50) NOT NULL
- title VARCHAR(100) NOT NULL
- description VARCHAR(500)
- event_year INTEGER NOT NULL
- event_month INTEGER (CHECK 1-12)
- event_date INTEGER (CHECK 1-31)
- country_id UUID (FK to address_country)
- state_id UUID (FK to address_state)
- district_id UUID (FK to address_district)
- sub_district_id UUID (FK to address_sub_district)
- locality_id UUID (FK to address_locality)
- address_details VARCHAR(30)
- created_at TIMESTAMP DEFAULT NOW()
- updated_at TIMESTAMP DEFAULT NOW()

Indexes:
- idx_person_life_event_person_id ON person_id
- idx_person_life_event_year ON event_year DESC

## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system - essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Events filtered by person ownership

*For any* authenticated user with a person record, retrieving life events SHALL return only events where person_id matches the user's person ID.

**Validates: Requirements 1.1, 3.4, 4.4**

### Property 2: Events sorted by date descending

*For any* list of life events returned by the API, the events SHALL be sorted by (year DESC, month DESC NULLS LAST, date DESC NULLS LAST).

**Validates: Requirements 1.2**

### Property 3: Event type validation

*For any* life event creation or update request, the event_type field SHALL be one of the predefined enum values (birth, marriage, death, purchase, sale, achievement, education, career, health, travel, other).

**Validates: Requirements 2.4, 6.1**

### Property 4: Field length validation

*For any* life event creation or update request:
- title length SHALL NOT exceed 100 characters
- description length SHALL NOT exceed 500 characters
- address_details length SHALL NOT exceed 30 characters

**Validates: Requirements 2.5, 2.9, 2.12**

### Property 5: Year required validation

*For any* life event creation request, the event_year field SHALL be required and present.

**Validates: Requirements 2.6**

### Property 6: Date consistency validation

*For any* life event with event_date provided, the date SHALL be valid for the given month and year (e.g., no Feb 30, no Apr 31).

**Validates: Requirements 2.8**

### Property 7: Create operation persistence

*For any* valid life event creation request, the created event SHALL be retrievable with all provided field values intact.

**Validates: Requirements 2.14**

### Property 8: Update operation persistence

*For any* valid life event update request, the updated event SHALL reflect all changed field values while preserving unchanged fields.

**Validates: Requirements 3.2, 3.3**

### Property 9: Delete operation removes event

*For any* life event deletion, the event SHALL no longer be retrievable after deletion.

**Validates: Requirements 4.2**

## Error Handling

Error responses:
- 404 "Life event not found" - Event not found
- 403 "Not enough permissions" - Permission denied (not owner)
- 422 "Invalid event type" - Invalid event type
- 422 "Title must be 100 characters or less" - Title too long
- 422 "Description must be 500 characters or less" - Description too long
- 422 "Invalid date for the given month/year" - Invalid date
- 422 "Field {field_name} is required" - Missing required field
- 400 "User must have a person record to manage life events" - User has no person record

## Testing Strategy

### Unit Tests

- Repository methods (CRUD operations, sorting)
- Service validation logic (date validation, field lengths)
- Schema validation

### Property-Based Tests

Using hypothesis library for Python backend tests:

1. Property 1: Generate random events for multiple persons, verify filtering
2. Property 2: Generate events with various date combinations, verify sort order
3. Property 3: Generate random strings, verify only valid enum values accepted
4. Property 4: Generate strings of various lengths, verify length constraints
5. Property 5: Attempt creation without year, verify rejection
6. Property 6: Generate date combinations, verify invalid dates rejected
7. Property 7: Create events with random valid data, verify retrieval
8. Property 8: Update events with partial data, verify persistence
9. Property 9: Delete events, verify non-retrievable

### Integration Tests

- Full API flow: create, read, update, delete
- Authorization: verify users cannot access other users' events
- Address pre-population from person's default address

### Frontend Tests

- Component rendering tests
- Multi-step wizard navigation
- Form validation
- Empty state display

# Implementation Plan: Person Life Events

## Overview

This plan implements the Life Events feature following the existing codebase patterns. Tasks are ordered to build incrementally: database model first, then backend API, then frontend components.

## Tasks

- [x] 1. Create database model and migration
  - [x] 1.1 Create PersonLifeEvent database model
    - Create file backend/app/db_models/person/person_life_event.py
    - Define all fields: id, person_id, event_type, title, description, event_year, event_month, event_date, address fields, timestamps
    - Add foreign key constraints to person and address tables
    - _Requirements: 2.4, 2.5, 2.6, 2.7, 2.9, 2.12_
  - [x] 1.2 Export model in db_models/person/__init__.py
    - Add PersonLifeEvent to the exports
  - [x] 1.3 Create Alembic migration
    - Generate migration for person_life_event table
    - Add indexes on person_id and event_year
    - _Requirements: 1.2_

- [x] 2. Create schemas
  - [x] 2.1 Create LifeEventType enum and schemas
    - Create file backend/app/schemas/person/life_event.py
    - Define LifeEventType enum with all event types
    - Define LifeEventBase, LifeEventCreate, LifeEventUpdate, LifeEventPublic, LifeEventsPublic
    - _Requirements: 2.4, 2.5, 2.6, 2.7, 2.9, 2.12, 6.1_
  - [x] 2.2 Export schemas in schemas/person/__init__.py

- [x] 3. Create repository
  - [x] 3.1 Create LifeEventRepository
    - Create file backend/app/repositories/person/life_event_repository.py
    - Implement get_by_person with sorting (year DESC, month DESC NULLS LAST, date DESC NULLS LAST)
    - Implement count_by_person
    - _Requirements: 1.1, 1.2_
  - [x] 3.2 Export repository in repositories/person/__init__.py

- [x] 4. Create service
  - [x] 4.1 Create LifeEventService
    - Create file backend/app/services/person/life_event_service.py
    - Implement get_life_events, get_life_event_by_id, create_life_event, update_life_event, delete_life_event
    - Implement user_can_access_event authorization check
    - Implement validate_date for date consistency validation
    - _Requirements: 1.1, 2.8, 2.14, 3.2, 3.3, 3.4, 4.2, 4.4_
  - [x] 4.2 Export service in services/person/__init__.py

- [x] 5. Create API routes
  - [x] 5.1 Create life_events router
    - Create file backend/app/api/routes/life_events.py
    - Implement GET /me endpoint for listing user's events
    - Implement POST / endpoint for creating events
    - Implement GET /{id} endpoint for getting single event
    - Implement PUT /{id} endpoint for updating events
    - Implement DELETE /{id} endpoint for deleting events
    - _Requirements: 1.1, 2.14, 3.3, 4.2_
  - [x] 5.2 Register router in api/main.py
    - Add life_events router with prefix /life-events

- [x] 6. Checkpoint - Backend complete
  - Ensure all tests pass, ask the user if questions arise.
  - Run backend tests to verify API functionality

- [x] 7. Generate frontend client
  - [x] 7.1 Regenerate OpenAPI client
    - Run client generation script to create LifeEventsService
    - Verify types are generated correctly

- [x] 8. Create frontend page and routing
  - [x] 8.1 Create Life Events page
    - Create file frontend/src/routes/_layout/life-events.tsx
    - Implement page with header, Add button, and events list
    - Handle empty state
    - Use Suspense for loading state
    - _Requirements: 1.1, 1.3, 1.4_
  - [x] 8.2 Add sidebar navigation
    - Update frontend/src/components/Sidebar/AppSidebar.tsx
    - Add Life Events item with Calendar icon
    - _Requirements: 5.1, 5.2_

- [x] 9. Create Add Life Event dialog
  - [x] 9.1 Create EventDetailsStep component
    - Create file frontend/src/components/LifeEvents/EventDetailsStep.tsx
    - Implement event type dropdown, title input, description textarea
    - Implement year (required), month, date fields with validation
    - _Requirements: 2.4, 2.5, 2.6, 2.7, 2.8, 2.9_
  - [x] 9.2 Create LocationStep component
    - Create file frontend/src/components/LifeEvents/LocationStep.tsx
    - Implement cascading address dropdowns (country, state, district, sub-district, locality)
    - Pre-populate with person's default address
    - Implement address_details text field (max 30 chars)
    - _Requirements: 2.10, 2.11, 2.12_
  - [x] 9.3 Create ConfirmationStep component
    - Create file frontend/src/components/LifeEvents/ConfirmationStep.tsx
    - Display summary of all entered data
    - Implement submit functionality
    - _Requirements: 2.13, 2.14, 2.15_
  - [x] 9.4 Create AddLifeEventDialog component
    - Create file frontend/src/components/LifeEvents/AddLifeEventDialog.tsx
    - Implement multi-step wizard with progress indicator
    - Handle step navigation (next, back)
    - Wire up create mutation
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 10. Create Edit and Delete functionality
  - [x] 10.1 Create LifeEventActionsMenu component
    - Create file frontend/src/components/LifeEvents/LifeEventActionsMenu.tsx
    - Implement Edit action that opens dialog in edit mode
    - Implement Delete action with confirmation dialog
    - _Requirements: 3.1, 4.1, 4.3_
  - [x] 10.2 Update AddLifeEventDialog for edit mode
    - Accept optional event prop for edit mode
    - Pre-populate form with existing data
    - Use update mutation instead of create
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 11. Create list display component
  - [x] 11.1 Create columns definition or list component
    - Create file frontend/src/components/LifeEvents/columns.tsx or LifeEventsList.tsx
    - Display event type, title, year, location summary
    - Include actions column with LifeEventActionsMenu
    - _Requirements: 1.4_

- [x] 12. Checkpoint - Frontend complete
  - Ensure all tests pass, ask the user if questions arise.
  - Test full flow: navigate, create, edit, delete events

- [ ] 13. Write property tests for backend
  - [ ] 13.1 Write property test for events filtering by person
    - **Property 1: Events filtered by person ownership**
    - **Validates: Requirements 1.1, 3.4, 4.4**
  - [ ] 13.2 Write property test for events sorting
    - **Property 2: Events sorted by date descending**
    - **Validates: Requirements 1.2**
  - [ ] 13.3 Write property test for event type validation
    - **Property 3: Event type validation**
    - **Validates: Requirements 2.4, 6.1**
  - [ ] 13.4 Write property test for field length validation
    - **Property 4: Field length validation**
    - **Validates: Requirements 2.5, 2.9, 2.12**
  - [ ] 13.5 Write property test for date consistency
    - **Property 6: Date consistency validation**
    - **Validates: Requirements 2.8**

- [ ] 14. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.
  - Verify complete feature functionality

## Notes

- Tasks marked with * are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- The frontend client is auto-generated from OpenAPI spec after backend is complete

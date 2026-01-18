# Implementation Plan: Rishte Person Search Wizard

## Overview

This implementation plan creates a user-friendly multi-step wizard for selecting persons in the Rishte feature. The wizard replaces UUID-based input with a search-based approach using name, address, and religion criteria. All components are self-contained within the Rishte folder.

## Tasks

- [x] 1. Update Types and Interfaces
  - [x] 1.1 Add new TypeScript interfaces to types.ts
    - Add `SelectedPerson`, `BasicInfoFormData`, `AddressFormData`, `ReligionFormData`
    - Add `PersonSearchCriteria`, `WizardStep` enum
    - Add component props interfaces
    - _Requirements: 1.1, 1.2_

- [x] 2. Implement Person Selection Button
  - [x] 2.1 Create RishtePersonButton component
    - Create `src/components/Rishte/RishtePersonButton.tsx`
    - Display "Select Person A/B" button when no person selected
    - Display selected person card with name and clear button when selected
    - Use UserPlus icon for unselected state
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  - [ ]* 2.2 Write property test for selected person display
    - **Property 2: Selected Person Display**
    - **Validates: Requirements 2.3**

- [x] 3. Implement Basic Info Step (Step 1)
  - [x] 3.1 Create RishteBasicInfoStep component
    - Create `src/components/Rishte/RishteBasicInfoStep.tsx`
    - Add form with first name (required), last name (required), gender (optional), birth year range (optional)
    - Integrate with genders API for dropdown
    - Add validation using zod schema
    - Add "Next" button
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_
  - [ ]* 3.2 Write property test for name validation
    - **Property 3: Name Field Validation**
    - **Validates: Requirements 3.2, 3.3, 3.7**

- [x] 4. Implement Address Step (Step 2)
  - [x] 4.1 Create RishteAddressStep component
    - Create `src/components/Rishte/RishteAddressStep.tsx`
    - Add cascading dropdowns for Country, State, District, Sub-District, Locality
    - Implement cascade logic to reset child dropdowns on parent change
    - Accept default values from props
    - Add "Back" and "Next" buttons
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_
  - [ ]* 4.2 Write property test for address default population
    - **Property 4: Address Default Population**
    - **Validates: Requirements 4.2, 9.3**
  - [ ]* 4.3 Write property test for cascading dropdown reset
    - **Property 6: Cascading Dropdown Reset**
    - **Validates: Requirements 4.6, 5.5**

- [x] 5. Checkpoint - Steps 1-2 complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Religion Step (Step 3)
  - [x] 6.1 Create RishteReligionStep component
    - Create `src/components/Rishte/RishteReligionStep.tsx`
    - Add cascading dropdowns for Religion, Category, Sub-Category
    - Implement cascade logic to reset child dropdowns on parent change
    - Accept default values from props
    - Add "Back" and "Search" buttons
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
  - [ ]* 6.2 Write property test for religion default population
    - **Property 5: Religion Default Population**
    - **Validates: Requirements 5.2, 9.4**

- [x] 7. Implement Results Step (Step 4)
  - [x] 7.1 Create RishteResultsStep component
    - Create `src/components/Rishte/RishteResultsStep.tsx`
    - Call person search API with collected criteria
    - Display loading indicator during search
    - Display person cards in scrollable grid
    - Each card shows name, birth year, address, religion with "Select" button
    - Handle empty results with message
    - Add pagination for > 20 results
    - Add "Back" button
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_
  - [ ]* 7.2 Write property test for person result card content
    - **Property 8: Person Result Card Content**
    - **Validates: Requirements 6.4**

- [x] 8. Checkpoint - All steps complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement Main Wizard Dialog
  - [x] 9.1 Create RishtePersonSearchDialog component
    - Create `src/components/Rishte/RishtePersonSearchDialog.tsx`
    - Manage wizard state (currentStep, form data for each step)
    - Display progress indicator (Step X of 4)
    - Display title based on person label ("Select Person A" or "Select Person B")
    - Fetch active person's address and religion on mount
    - Pass defaults to Address and Religion steps
    - Handle step navigation (next, back)
    - Close dialog and call onPersonSelect when person is selected
    - Reset to Step 1 when opened
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 9.1, 9.2, 9.5, 9.6_
  - [ ]* 9.2 Write property test for wizard progress indicator
    - **Property 7: Wizard Progress Indicator**
    - **Validates: Requirements 8.2**

- [x] 10. Update Rishte Page
  - [x] 10.1 Update rishte.tsx to use new components
    - Replace PersonSelector components with RishtePersonButton components
    - Add state for selectedPersonA and selectedPersonB
    - Add state for which wizard is open (personA or personB)
    - Integrate RishtePersonSearchDialog
    - Update Find Relationship button to use selected person IDs
    - _Requirements: 2.1, 7.1, 7.2, 7.3, 7.4_
  - [ ]* 10.2 Write property test for Find button enabled state
    - **Property 1: Find Button Enabled State**
    - **Validates: Requirements 7.1, 7.2, 7.3**

- [x] 11. Update Barrel Exports
  - [x] 11.1 Update index.ts with new exports
    - Export all new components from `src/components/Rishte/index.ts`
    - _Requirements: 1.1_

- [x] 12. Responsive Design
  - [x] 12.1 Add responsive styles
    - Stack Person buttons vertically on smaller screens
    - Make dialog responsive for tablet/desktop
    - Use responsive grid for results cards
    - _Requirements: 10.1, 10.2, 10.3_

- [x] 13. Final Checkpoint
  - Ensure all tests pass, ask the user if questions arise.
  - Verify the feature works end-to-end

## Notes

- Tasks marked with `*` are optional property-based tests
- All components are self-contained in `src/components/Rishte/` folder
- No imports from existing Family or Search components
- Uses existing PersonService.searchPersons() API for search
- Defaults are fetched from active person's profile via ActivePersonContext


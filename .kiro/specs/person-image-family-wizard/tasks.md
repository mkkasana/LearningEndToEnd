# Implementation Plan: Person Image Upload in Family Wizard & Display

## Overview

Frontend implementation for profile image upload in the Add Family Member wizard and image display across PersonCard, family list, and PersonDetailsPanel. Assumes the backend profile image API is already implemented.

## Tasks

- [ ] 1. Set up dependencies and utility functions
  - [ ] 1.1 Install `browser-image-compression` npm package
    - Run `npm install browser-image-compression` in the frontend directory
    - _Requirements: 1.4_
  - [ ] 1.2 Create `getPersonImageUrl` utility function
    - Create `frontend/src/utils/personImage.ts`
    - Implement URL resolution for main and thumbnail variants
    - Handle null/undefined keys returning undefined
    - Derive thumbnail key by replacing `.jpg` with `_thumb.jpg`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  - [ ]* 1.3 Write property tests for `getPersonImageUrl`
    - **Property 6: URL resolution correctness**
    - **Property 7: Thumbnail key derivation**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

- [ ] 2. Create reusable ImageUpload component
  - [ ] 2.1 Implement `ImageUpload` component
    - Create `frontend/src/components/Common/ImageUpload.tsx`
    - Implement click-to-select with hidden file input
    - Implement drag-and-drop with visual feedback
    - Validate file type (JPEG, PNG, WebP) and size (max 5 MB)
    - Compress with `browser-image-compression` (max 800x800, JPEG 80%)
    - Show circular preview with remove button when image selected
    - Show camera icon placeholder when no image selected
    - Add proper ARIA labels for accessibility
    - Call `onChange` with compressed File or null
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10_
  - [ ]* 2.2 Write unit tests for ImageUpload component
    - Test default render state (placeholder icon)
    - Test file type validation error display
    - Test file size validation error display
    - Test onChange callback is called with valid file
    - Test remove button clears the image
    - **Property 1: Invalid file type rejection**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10**

- [ ] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Integrate ImageUpload into Add Family Member wizard
  - [ ] 4.1 Update `AddFamilyMemberDialog` to manage image state
    - Add `imageFile` state (`File | null`) to the dialog
    - Pass `imageFile` and `onImageChange` to BasicInfoStep
    - Pass `imageFile` to ConfirmationStep
    - Reset `imageFile` on dialog close
    - _Requirements: 2.2, 2.6_
  - [ ] 4.2 Update `BasicInfoStep` to include ImageUpload
    - Add `imageFile` and `onImageChange` props
    - Render ImageUpload component above name fields with label "Profile Photo (Optional)"
    - _Requirements: 2.1, 2.7_
  - [ ] 4.3 Update `ConfirmationStep` to handle image upload
    - Add `imageFile` prop
    - Display image preview in the review summary when image is present
    - After person creation (Step 4), add Step 5: upload image via `POST /persons/{personId}/profile-image`
    - Wrap image upload in try/catch — show warning toast on failure but still complete
    - _Requirements: 2.3, 2.4, 2.5_
  - [ ]* 4.4 Write unit tests for wizard image integration
    - Test image state preservation across step navigation
    - Test ConfirmationStep shows image preview
    - Test graceful handling of image upload failure
    - **Property 2: Wizard image state preservation**
    - **Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6**

- [ ] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Display profile images in existing components
  - [ ] 6.1 Update `PersonCard` to show profile images
    - Import `getPersonImageUrl` utility
    - Set `AvatarImage src` to thumbnail URL from `person.profile_image_key`
    - Keep existing `AvatarFallback` with gender-based icon as fallback
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - [ ] 6.2 Update family list in `family.tsx` to show profile images
    - Add Avatar component to each family member card
    - Use thumbnail URL from `person.profile_image_key`
    - Show fallback icon when no image
    - _Requirements: 4.1, 4.2, 4.3_
  - [ ] 6.3 Update `PersonDetailsPanel` to show profile images
    - Display main image (400x400) at the top of the panel
    - Use `getPersonImageUrl` with `main` variant
    - Show large placeholder icon as fallback
    - _Requirements: 5.1, 5.2, 5.3_
  - [ ]* 6.4 Write unit tests for image display in components
    - Test PersonCard renders thumbnail when profile_image_key exists
    - Test PersonCard renders fallback when profile_image_key is null
    - Test PersonDetailsPanel renders main image
    - **Property 3: PersonCard conditional image display**
    - **Property 4: Family list conditional image display**
    - **Property 5: PersonDetailsPanel conditional image display**
    - **Validates: Requirements 3.1, 3.2, 4.1, 4.2, 5.1, 5.2**

- [ ] 7. Regenerate OpenAPI client and verify integration
  - [ ] 7.1 Regenerate frontend OpenAPI client
    - Run `npm run generate-client` to pick up `profile_image_key` in PersonPublic type
    - Verify the generated types include the new field
    - _Requirements: 3.1, 4.1, 5.1_

- [ ] 8. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests use fast-check for frontend property-based testing
- Unit tests use Vitest + React Testing Library
- Task 7.1 (regenerate client) requires the backend to be running with the new endpoints

# Implementation Plan: Profile Image Signup Flow

## Overview

Add an optional profile photo upload step to the complete-profile flow. This is frontend-only work: modify the ProgressIndicator type, update step determination logic, create a new ProfilePhotoStep component, and wire it into the complete-profile route.

## Tasks

- [x] 1. Update ProgressIndicator to support the new step
  - [x] 1.1 Add `"profile-photo"` to the `ProfileStep` type union in `frontend/src/components/Profile/ProgressIndicator.tsx`
    - Add the new type value between `"personal-info"` and `"address"`
    - Add a "Photo" step entry in the `steps` array between "Personal Information" and "Address Information"
    - The step's `complete` status should be driven by a new optional `hasProfileImage` prop on `ProgressIndicatorProps`
    - _Requirements: 1.2_

- [x] 2. Create ProfilePhotoStep component
  - [x] 2.1 Create `frontend/src/components/Profile/ProfilePhotoStep.tsx`
    - Accept `onComplete: () => void` prop
    - Render `ImageUpload` component inside a Card with header text
    - Add "Skip" button that calls `onComplete()` directly
    - Add "Upload & Continue" button that is disabled when no file is selected
    - On "Upload & Continue", send the file via `fetch()` to `POST ${import.meta.env.VITE_API_URL}/api/v1/person/me/profile-image` with Bearer token from `localStorage.getItem("access_token")`
    - Show loading state during upload (disable both buttons, show spinner on upload button)
    - On success, call `onComplete()`
    - On failure, show error toast and preserve the selected file
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 4.1, 6.1, 6.2_

- [x] 3. Update complete-profile route with new step logic
  - [x] 3.1 Modify `frontend/src/routes/complete-profile.tsx`
    - Import `ProfilePhotoStep` and `PersonService`
    - Add a `useQuery` for `PersonService.getMyPerson()` to get the person record (only when `profileStatus?.has_person` is true)
    - Modify `determineCurrentStep()` to accept a `hasProfileImage: boolean` parameter
    - Insert `"profile-photo"` step logic: when personal-info is complete, `has_address` is false, and `hasProfileImage` is false, return `"profile-photo"`
    - When `hasProfileImage` is true, skip to `"address"` as before
    - Add rendering block for `currentStep === "profile-photo"` that renders `ProfilePhotoStep` with `ProgressIndicator`
    - Pass `hasProfileImage` to `ProgressIndicator` for the photo step's complete state
    - _Requirements: 1.1, 1.3, 5.1, 5.2, 5.3_

- [x] 4. Checkpoint - Verify the flow works end-to-end
  - Ensure all tests pass, ask the user if questions arise.
  - Rebuild frontend Docker image and verify the complete-profile flow shows the photo step at the correct position
  - Verify skip works and upload works with the existing backend endpoint

- [ ]* 5. Write property tests for step determination
  - [ ]* 5.1 Write property test for step determination with profile image awareness
    - **Property 1: Step determination respects profile image state**
    - Use `fast-check` to generate random profile statuses with `has_person` true and `has_address` false
    - Vary `hasProfileImage` boolean — verify returns `"profile-photo"` when false, `"address"` when true
    - **Validates: Requirements 1.1, 4.2, 5.2, 5.3**

  - [ ]* 5.2 Write property test for photo step never blocking completion
    - **Property 2: Profile photo step never blocks completion**
    - Generate random statuses with `has_address` true — verify never returns `"profile-photo"`
    - **Validates: Requirements 4.2, 5.1**

  - [ ]* 5.3 Write property test for step ordering invariant
    - **Property 3: Step ordering invariant**
    - Generate random profile statuses — verify the returned step respects the ordering: personal-info < profile-photo < address < religion < marital-status < duplicate-check
    - **Validates: Requirements 1.1, 1.3**

- [ ]* 6. Write unit tests for ProfilePhotoStep component
  - [ ]* 6.1 Write unit tests for ProfilePhotoStep rendering and interactions
    - Test that ImageUpload component is rendered
    - Test "Skip" button calls onComplete without fetch
    - Test "Upload & Continue" is disabled when no file selected
    - Test successful upload calls onComplete
    - Test failed upload shows error and preserves file
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.3, 3.4, 4.1_

- [x] 7. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- No backend changes required — uses existing `POST /api/v1/person/me/profile-image` endpoint
- The `ImageUpload` component handles compression, validation, and preview internally
- Raw `fetch()` is used for the upload (same pattern as family wizard's ConfirmationStep) since the generated SDK doesn't have this endpoint typed yet

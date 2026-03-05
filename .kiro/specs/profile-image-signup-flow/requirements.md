# Requirements Document

## Introduction

Add an optional profile photo upload step to the complete-profile/signup flow. This feature allows new users to upload a profile photo during onboarding, reusing the existing `ImageUpload` component and the backend `POST /api/v1/person/me/profile-image` endpoint. The upload is entirely optional — users can skip it and proceed without a photo.

## Glossary

- **Complete_Profile_Flow**: The multi-step onboarding flow at `/complete-profile` that guides new users through profile setup (personal info, address, religion, marital status, verification).
- **ImageUpload_Component**: The existing reusable React component (`frontend/src/components/Common/ImageUpload.tsx`) that handles drag-and-drop, click-to-select, file validation (JPEG/PNG/WebP, max 5MB), client-side compression (800x800, JPEG 80%), and preview.
- **Profile_Image_Endpoint**: The existing backend endpoint `POST /api/v1/person/me/profile-image` that accepts a file upload and stores the profile image for the current user's person record.
- **ProgressIndicator**: The step progress bar component that displays the user's current position in the Complete_Profile_Flow.
- **Profile_Photo_Step**: The new step in the Complete_Profile_Flow where users can optionally upload a profile photo.

## Requirements

### Requirement 1: Profile Photo Step Placement

**User Story:** As a new user completing my profile, I want to see a profile photo upload step after my personal information is confirmed, so that I can add a photo while my profile details are fresh in my mind.

#### Acceptance Criteria

1. WHEN the Complete_Profile_Flow determines the current step, THE Complete_Profile_Flow SHALL place the Profile_Photo_Step after the personal-info step and before the address step.
2. THE ProgressIndicator SHALL display the Profile_Photo_Step as a labeled step between "Personal Information" and "Address Information" in the step indicator bar.
3. WHEN the personal-info step is complete and the user has not yet completed the address step, THE Complete_Profile_Flow SHALL display the Profile_Photo_Step.

### Requirement 2: Profile Photo Upload Interface

**User Story:** As a new user, I want to see a clear and inviting photo upload interface, so that I understand I can add a profile photo.

#### Acceptance Criteria

1. WHEN the Profile_Photo_Step is displayed, THE Complete_Profile_Flow SHALL render the existing ImageUpload_Component within a Card layout consistent with the other steps.
2. WHEN the Profile_Photo_Step is displayed, THE Complete_Profile_Flow SHALL show a "Skip" button that allows the user to proceed without uploading a photo.
3. WHEN the Profile_Photo_Step is displayed and the user has selected a photo, THE Complete_Profile_Flow SHALL show an "Upload & Continue" button to submit the photo and proceed.
4. WHEN no photo is selected, THE Complete_Profile_Flow SHALL disable the "Upload & Continue" button.

### Requirement 3: Profile Photo Upload Execution

**User Story:** As a new user, I want my selected photo to be uploaded to my profile when I confirm, so that my profile has a photo for other family members to see.

#### Acceptance Criteria

1. WHEN the user clicks "Upload & Continue" with a selected photo, THE Complete_Profile_Flow SHALL send the compressed image file to the Profile_Image_Endpoint using a multipart form data request with the authenticated user's token.
2. WHEN the upload request is in progress, THE Complete_Profile_Flow SHALL display a loading indicator and disable both the "Upload & Continue" and "Skip" buttons to prevent duplicate submissions.
3. WHEN the upload succeeds, THE Complete_Profile_Flow SHALL advance to the duplicate-check step by calling the profile status refetch.
4. IF the upload request fails, THEN THE Complete_Profile_Flow SHALL display an error toast message and keep the user on the Profile_Photo_Step with the selected photo preserved.

### Requirement 4: Skip Behavior

**User Story:** As a new user who does not want to upload a photo right now, I want to skip the photo step easily, so that I can complete my profile without delay.

#### Acceptance Criteria

1. WHEN the user clicks "Skip", THE Complete_Profile_Flow SHALL advance to the duplicate-check step without making any upload request.
2. WHEN the user skips the Profile_Photo_Step, THE Complete_Profile_Flow SHALL not mark the step as incomplete or block profile completion.

### Requirement 5: Step State Management

**User Story:** As a new user returning to the complete-profile flow, I want the flow to correctly determine whether I need the photo step, so that I am not asked to upload a photo again if I already have one or have passed that step.

#### Acceptance Criteria

1. WHEN the profile status indicates the personal-info step is complete and the address step is not yet complete, THE Complete_Profile_Flow SHALL check whether the user already has a profile image before showing the Profile_Photo_Step.
2. WHEN the user already has a profile_image_key on their person record, THE Complete_Profile_Flow SHALL skip the Profile_Photo_Step and proceed directly to the address step.
3. WHEN the user does not have a profile_image_key and has not yet completed the address step, THE Complete_Profile_Flow SHALL display the Profile_Photo_Step.

### Requirement 6: API URL Configuration

**User Story:** As a developer, I want the image upload request to use the correct API base URL, so that the request reaches the backend regardless of the frontend hosting configuration.

#### Acceptance Criteria

1. THE Complete_Profile_Flow SHALL use `import.meta.env.VITE_API_URL` as the base URL for the profile image upload fetch request.
2. THE Complete_Profile_Flow SHALL include the user's Bearer token in the Authorization header of the upload request.

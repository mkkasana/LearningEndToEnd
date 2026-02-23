# Requirements Document

## Introduction

This feature adds profile image upload capability to the Add Family Member wizard and displays person profile images throughout the frontend. It introduces a reusable image upload component with client-side preview and compression, integrates it into the existing 5-step wizard as an optional field in the BasicInfoStep, uploads the image after person creation in the ConfirmationStep, and displays profile images in PersonCard, family list cards, and the PersonDetailsPanel.

## Glossary

- **Image_Upload_Component**: A reusable React component that provides drag-and-drop and click-to-select image upload with client-side preview and compression.
- **Add_Family_Member_Wizard**: The existing 5-step dialog for adding family members (BasicInfoStep → AddressStep → ReligionStep → ConnectExistingPersonStep → ConfirmationStep).
- **PersonCard**: The card component used in the family tree view to display a person's name, years, and avatar.
- **Family_List_Card**: The card component used in the family page to display family member information.
- **PersonDetailsPanel**: The side panel that shows detailed information about a selected person in the family tree.
- **Client_Compression**: Browser-side image resizing and compression performed before uploading to reduce upload time and bandwidth.

## Requirements

### Requirement 1: Reusable Image Upload Component

**User Story:** As a developer, I want a reusable image upload component, so that I can add image upload capability to multiple flows without duplicating code.

#### Acceptance Criteria

1. THE Image_Upload_Component SHALL accept images via click-to-select file dialog
2. THE Image_Upload_Component SHALL accept images via drag-and-drop onto the upload area
3. WHEN an image is selected, THE Image_Upload_Component SHALL display a preview of the image within the upload area
4. WHEN an image is selected, THE Image_Upload_Component SHALL compress the image client-side to a maximum of 800x800 pixels and JPEG format at 80% quality before storing it in component state
5. IF the selected file is not a JPEG, PNG, or WebP image, THEN THE Image_Upload_Component SHALL display an error message "Please select a JPEG, PNG, or WebP image"
6. IF the selected file exceeds 5 MB before compression, THEN THE Image_Upload_Component SHALL display an error message "Image must be less than 5 MB"
7. WHEN a preview is displayed, THE Image_Upload_Component SHALL show a remove button to clear the selected image
8. THE Image_Upload_Component SHALL expose the compressed image file via an `onChange` callback prop
9. THE Image_Upload_Component SHALL display a circular preview area with a camera/upload icon when no image is selected
10. THE Image_Upload_Component SHALL be accessible with proper ARIA labels for the file input and drag-drop zone

### Requirement 2: Image Upload in Add Family Member Wizard

**User Story:** As a user, I want to optionally add a profile photo when creating a family member, so that I can visually identify family members in the tree.

#### Acceptance Criteria

1. WHEN the BasicInfoStep is displayed, THE Add_Family_Member_Wizard SHALL show the Image_Upload_Component above the name fields as an optional field
2. WHEN the user proceeds through wizard steps, THE Add_Family_Member_Wizard SHALL preserve the selected image data across step navigation (back and forward)
3. WHEN the user reaches the ConfirmationStep with an image selected, THE ConfirmationStep SHALL display the image preview in the review summary
4. WHEN the user confirms and the person is created successfully, THE ConfirmationStep SHALL upload the image to the backend via the profile image API endpoint
5. IF the image upload fails after person creation, THEN THE ConfirmationStep SHALL show a warning toast but still complete the family member creation successfully
6. WHEN no image is selected, THE Add_Family_Member_Wizard SHALL proceed normally without any image upload step
7. THE Image_Upload_Component in BasicInfoStep SHALL display a label "Profile Photo (Optional)"

### Requirement 3: Display Profile Images in PersonCard

**User Story:** As a user, I want to see profile photos on person cards in the family tree, so that I can visually identify family members at a glance.

#### Acceptance Criteria

1. WHEN a person has a `profile_image_key`, THE PersonCard SHALL display the person's thumbnail image in the Avatar component
2. WHEN a person does not have a `profile_image_key`, THE PersonCard SHALL display the existing gender-based fallback icon
3. THE PersonCard SHALL use the thumbnail URL (100x100) for the avatar to minimize bandwidth usage
4. WHEN the thumbnail image fails to load, THE PersonCard SHALL fall back to the gender-based icon

### Requirement 4: Display Profile Images in Family List

**User Story:** As a user, I want to see profile photos in the family member list, so that I can quickly identify family members.

#### Acceptance Criteria

1. WHEN a family member has a `profile_image_key`, THE Family_List_Card SHALL display the person's thumbnail image
2. WHEN a family member does not have a `profile_image_key`, THE Family_List_Card SHALL display a generic person icon or initials
3. THE Family_List_Card SHALL use the thumbnail URL for the avatar display

### Requirement 5: Display Profile Images in PersonDetailsPanel

**User Story:** As a user, I want to see a larger profile photo in the person details panel, so that I can view the photo clearly when inspecting a person's details.

#### Acceptance Criteria

1. WHEN a person has a `profile_image_key`, THE PersonDetailsPanel SHALL display the main image (400x400) prominently at the top of the panel
2. WHEN a person does not have a `profile_image_key`, THE PersonDetailsPanel SHALL display a large placeholder icon
3. WHEN the main image fails to load, THE PersonDetailsPanel SHALL fall back to the placeholder icon

### Requirement 6: Image URL Resolution

**User Story:** As a developer, I want a utility function to resolve image URLs from storage keys, so that all components use consistent URL generation.

#### Acceptance Criteria

1. THE utility function SHALL accept a `profile_image_key` and a variant (`main` or `thumbnail`) and return the full image URL
2. WHEN the environment is local, THE utility function SHALL return a URL relative to the backend API (e.g., `/api/v1/uploads/person-images/{key}`)
3. WHEN the environment is production, THE utility function SHALL return the CloudFront URL for the image
4. WHEN `profile_image_key` is null or undefined, THE utility function SHALL return undefined
5. THE utility function SHALL derive the thumbnail key by appending `_thumb` before the file extension (e.g., `abc.jpg` → `abc_thumb.jpg`)

# Requirements Document

## Introduction

Profile images are not rendering in several frontend views even though users have uploaded profile photos. The family-tree and family views already display images correctly, but five other views need to be updated. Some backend API response schemas are also missing the `profile_image_key` field, which must be added before the frontend can render images in those views.

## Glossary

- **Profile_Image_Key**: A nullable string field on person records storing the filename of the uploaded profile image (e.g., `a3f6516cba4e4ed78d9a16d97f6bf883.jpg`)
- **Thumbnail**: A smaller version of the profile image, derived by replacing `.jpg` with `_thumb.jpg` in the Profile_Image_Key
- **Image_URL_Utility**: The `getPersonImageUrl` function in `frontend/src/utils/personImage.ts` that converts a Profile_Image_Key to a full URL
- **RelativeCard**: The card component used in the `/relatives-network` view to display each relative
- **PersonSearchCard**: The card component used in the `/search` view to display each search result
- **PersonNode**: The React Flow node component used in the `/rishte` graph to display persons
- **MatchPersonNode**: The React Flow node component used in the `/find-partner` graph to display persons
- **User_Menu**: The sidebar footer component that displays the logged-in user's name and avatar
- **Avatar_Component**: The shadcn/ui Avatar component with AvatarImage and AvatarFallback sub-components
- **RelativeInfo_Schema**: The backend Pydantic schema for individual relatives in the relatives-network API response
- **PersonSearchResult_Schema**: The backend Pydantic schema for individual persons in the search API response
- **PersonNode_Schema**: The backend Pydantic schema for person nodes in the lineage-path API response
- **MatchGraphNode_Schema**: The backend Pydantic schema for person nodes in the partner-match API response

## Requirements

### Requirement 1: Add profile_image_key to Backend API Response Schemas

**User Story:** As a frontend developer, I want the backend API responses to include `profile_image_key` for person records, so that the frontend can render profile images in all views.

#### Acceptance Criteria

1. THE RelativeInfo_Schema SHALL include a nullable `profile_image_key` field of type `str | None` with a default of `None`
2. THE PersonSearchResult_Schema SHALL include a nullable `profile_image_key` field of type `str | None` with a default of `None`
3. THE PersonNode_Schema SHALL include a nullable `profile_image_key` field of type `str | None` with a default of `None`
4. THE MatchGraphNode_Schema SHALL include a nullable `profile_image_key` field of type `str | None` with a default of `None`
5. WHEN the backend services construct these response objects, THE services SHALL populate the `profile_image_key` field from the person database record

### Requirement 2: Display Profile Images in Relatives Network View

**User Story:** As a user, I want to see profile image thumbnails on person cards in the relatives network view, so that I can visually identify my relatives.

#### Acceptance Criteria

1. WHEN a relative has a Profile_Image_Key, THE RelativeCard SHALL display the Thumbnail as the avatar image using the Image_URL_Utility
2. WHEN a relative does not have a Profile_Image_Key, THE RelativeCard SHALL display the existing gender-based icon fallback
3. THE RelativeCard SHALL use the Avatar_Component with AvatarImage and AvatarFallback for graceful loading and error handling

### Requirement 3: Display Profile Images in Search Results View

**User Story:** As a user, I want to see profile image thumbnails on person cards in the search results, so that I can visually identify persons I am searching for.

#### Acceptance Criteria

1. WHEN a search result person has a Profile_Image_Key, THE PersonSearchCard SHALL display the Thumbnail as the avatar image using the Image_URL_Utility
2. WHEN a search result person does not have a Profile_Image_Key, THE PersonSearchCard SHALL display the existing gender-based icon fallback
3. THE PersonSearchCard SHALL use the Avatar_Component with AvatarImage and AvatarFallback for graceful loading and error handling

### Requirement 4: Display Profile Images in Rishte Graph View

**User Story:** As a user, I want to see profile image thumbnails on person nodes in the rishte relationship graph, so that I can visually identify persons in the lineage path.

#### Acceptance Criteria

1. WHEN a person node in the rishte graph has a Profile_Image_Key, THE PersonNode SHALL display the Thumbnail as the avatar image using the Image_URL_Utility
2. WHEN a person node does not have a Profile_Image_Key, THE PersonNode SHALL display the existing User icon fallback
3. THE PersonNode SHALL use the Avatar_Component with AvatarImage and AvatarFallback for graceful loading and error handling
4. THE PersonNodeData type SHALL include an optional `profileImageKey` field

### Requirement 5: Display Profile Images in Find Partner Graph View

**User Story:** As a user, I want to see profile image thumbnails on person nodes in the find partner graph, so that I can visually identify persons in the match path.

#### Acceptance Criteria

1. WHEN a person node in the find partner graph has a Profile_Image_Key, THE MatchPersonNode SHALL display the Thumbnail as the avatar image using the Image_URL_Utility
2. WHEN a person node does not have a Profile_Image_Key, THE MatchPersonNode SHALL display the existing User icon fallback
3. THE MatchPersonNode SHALL use the Avatar_Component with AvatarImage and AvatarFallback for graceful loading and error handling
4. THE MatchPersonNodeData type SHALL include an optional `profileImageKey` field

### Requirement 6: Display Profile Image in User Menu

**User Story:** As a user, I want to see my profile image avatar in the sidebar user menu, so that I have a personalized experience.

#### Acceptance Criteria

1. WHEN the logged-in user has an associated person record with a Profile_Image_Key, THE User_Menu SHALL display the Thumbnail as the avatar image using the Image_URL_Utility
2. WHEN the logged-in user does not have a Profile_Image_Key, THE User_Menu SHALL display the existing initials-based fallback
3. THE User_Menu SHALL use the Avatar_Component with AvatarImage and AvatarFallback for graceful loading and error handling

### Requirement 7: Backend Unit Tests for Schema Changes

**User Story:** As a developer, I want unit tests covering the new `profile_image_key` field in API response schemas, so that I can verify the field is correctly populated.

#### Acceptance Criteria

1. WHEN a person has a profile_image_key set, THE backend unit tests SHALL verify the API response includes the correct profile_image_key value
2. WHEN a person does not have a profile_image_key, THE backend unit tests SHALL verify the API response includes `null` for profile_image_key

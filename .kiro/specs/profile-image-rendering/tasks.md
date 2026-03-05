# Implementation Plan: Profile Image Rendering

## Overview

Add `profile_image_key` to four backend API response schemas and their service methods, then update five frontend components to render profile image thumbnails using the existing `getPersonImageUrl` utility and `Avatar` component pattern from the family-tree `PersonCard`.

## Tasks

- [x] 1. Add profile_image_key to backend schemas and services
  - [x] 1.1 Add `profile_image_key: str | None = Field(default=None, description="Storage key for the person's profile image")` to `RelativeInfo` in `backend/app/schemas/relatives_network/relatives_network_schemas.py`
    - _Requirements: 1.1_
  - [x] 1.2 Add `profile_image_key` to `PersonSearchResult` in `backend/app/schemas/person/person_search.py`
    - _Requirements: 1.2_
  - [x] 1.3 Add `profile_image_key` to `PersonNode` in `backend/app/schemas/lineage_path/lineage_path_schemas.py`
    - _Requirements: 1.3_
  - [x] 1.4 Add `profile_image_key` to `MatchGraphNode` in `backend/app/schemas/partner_match/partner_match_schemas.py`
    - _Requirements: 1.4_
  - [x] 1.5 Update `RelativesNetworkService._enrich_relative_info` to pass `profile_image_key=person.profile_image_key` in both the normal and fallback `RelativeInfo` construction
    - _Requirements: 1.5_
  - [x] 1.6 Update `PersonSearchService.search_persons` to pass `profile_image_key=person.profile_image_key` in both `PersonSearchResult` construction sites (with and without name filter)
    - _Requirements: 1.5_
  - [x] 1.7 Update `LineagePathService._enrich_person_data` to pass `profile_image_key=person.profile_image_key` in both the normal and fallback `PersonNode` construction
    - _Requirements: 1.5_
  - [x] 1.8 Update `PartnerMatchService._enrich_node_data` to pass `profile_image_key=person.profile_image_key` in both the normal and fallback `MatchGraphNode` construction. Also update `_prune_graph` to copy `profile_image_key` when reconstructing pruned nodes.
    - _Requirements: 1.5_
  - [ ]* 1.9 Write backend unit tests for profile_image_key passthrough
    - Test `RelativesNetworkService._enrich_relative_info` returns correct `profile_image_key` for persons with and without images
    - Test `PersonSearchService.search_persons` includes `profile_image_key` in results
    - Test `LineagePathService._enrich_person_data` returns correct `profile_image_key`
    - Test `PartnerMatchService._enrich_node_data` returns correct `profile_image_key`
    - Test `PartnerMatchService._prune_graph` preserves `profile_image_key` on pruned nodes
    - **Property 2: Backend service profile_image_key passthrough**
    - **Validates: Requirements 1.5, 7.1, 7.2**

- [x] 2. Checkpoint - Backend changes complete
  - Ensure all tests pass, ask the user if questions arise.
  - Remind user to rebuild backend and regenerate OpenAPI client: `docker compose build --no-cache backend && docker compose up -d`, then `cd frontend && npm run generate-client`

- [x] 3. Update frontend components for relatives network view
  - [x] 3.1 Add `profile_image_key: string | null` to the `RelativeData` interface in `frontend/src/components/RelativesNetwork/RelativesResultsGrid.tsx` and pass it as a prop to `RelativeCard`
    - _Requirements: 2.1_
  - [x] 3.2 Update `RelativeCard` in `frontend/src/components/RelativesNetwork/RelativeCard.tsx`:
    - Add `profileImageKey?: string | null` to `RelativeCardProps`
    - Import `getPersonImageUrl` from `@/utils/personImage` and `AvatarImage` from `@/components/ui/avatar`
    - Add `<AvatarImage src={getPersonImageUrl(profileImageKey, 'thumbnail')} alt={displayName} />` inside the existing `<Avatar>`
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 4. Update frontend components for search view
  - [x] 4.1 Update `PersonSearchCard` in `frontend/src/components/Search/PersonSearchCard.tsx`:
    - Import `getPersonImageUrl` from `@/utils/personImage`
    - Change `<AvatarImage src={undefined} alt="" />` to `<AvatarImage src={getPersonImageUrl(person.profile_image_key, 'thumbnail')} alt={fullName} />`
    - The `PersonSearchResult` type from the generated client will already have `profile_image_key` after client regeneration
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 5. Update frontend components for rishte graph view
  - [x] 5.1 Add `profileImageKey?: string | null` to `PersonNodeData` interface in `frontend/src/components/Rishte/types.ts`
    - _Requirements: 4.4_
  - [x] 5.2 Update `createNodes` in `frontend/src/components/Rishte/utils/pathTransformer.ts` to pass `profileImageKey: person.profile_image_key ?? null` in the node data
    - _Requirements: 4.1_
  - [x] 5.3 Update `PersonNode` in `frontend/src/components/Rishte/PersonNode.tsx`:
    - Import `getPersonImageUrl` from `@/utils/personImage` and `AvatarImage` from `@/components/ui/avatar`
    - Destructure `profileImageKey` from `data`
    - Add `<AvatarImage src={getPersonImageUrl(profileImageKey, 'thumbnail')} alt={displayName} />` inside the existing `<Avatar>`
    - _Requirements: 4.1, 4.2, 4.3_

- [x] 6. Update frontend components for find partner graph view
  - [x] 6.1 Add `profileImageKey?: string | null` to `MatchPersonNodeData` interface in `frontend/src/components/FindPartner/types.ts`
    - _Requirements: 5.4_
  - [x] 6.2 Update node creation in `frontend/src/components/FindPartner/utils/matchGraphTransformer.ts` to pass `profileImageKey: person.profile_image_key ?? null` in the node data
    - _Requirements: 5.1_
  - [x] 6.3 Update `MatchPersonNode` in `frontend/src/components/FindPartner/MatchPersonNode.tsx`:
    - Import `getPersonImageUrl` from `@/utils/personImage` and `AvatarImage` from `@/components/ui/avatar`
    - Destructure `profileImageKey` from `data`
    - Add `<AvatarImage src={getPersonImageUrl(profileImageKey, 'thumbnail')} alt={displayName} />` inside the existing `<Avatar>`
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 7. Update user menu sidebar
  - [x] 7.1 Update `AppSidebar` in `frontend/src/components/Sidebar/AppSidebar.tsx` to read `activePerson` from `useActivePersonContext()` and pass `profileImageKey={activePerson?.profile_image_key}` to the `User` component
    - _Requirements: 6.1_
  - [x] 7.2 Update `User` component in `frontend/src/components/Sidebar/User.tsx`:
    - Accept `profileImageKey?: string | null` prop
    - Import `getPersonImageUrl` from `@/utils/personImage` and `AvatarImage` from `@/components/ui/avatar`
    - Update the `UserInfo` sub-component to accept `profileImageKey` and render `<AvatarImage src={getPersonImageUrl(profileImageKey, 'thumbnail')} alt={fullName || "User"} />` inside the `<Avatar>`
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 8. Checkpoint - Frontend changes complete
  - Ensure all tests pass, ask the user if questions arise.
  - Remind user to rebuild frontend: `docker compose build --no-cache frontend && docker compose up -d`

- [ ]* 9. Write property test for getPersonImageUrl
  - **Property 1: Thumbnail URL generation correctness**
  - Using fast-check, generate random strings ending in `.jpg` and verify `getPersonImageUrl(key, 'thumbnail')` produces a URL with `_thumb.jpg` suffix and correct base URL prefix
  - Also test that `getPersonImageUrl(null)` and `getPersonImageUrl(undefined)` return `undefined`
  - **Validates: Requirements 2.1, 3.1, 4.1, 5.1, 6.1**

- [x] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- After backend changes (task 1), user must rebuild backend and regenerate the OpenAPI client before frontend tasks
- After frontend changes (tasks 3-7), user must rebuild the frontend Docker image
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases

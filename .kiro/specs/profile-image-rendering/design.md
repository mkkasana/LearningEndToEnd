# Design Document: Profile Image Rendering

## Overview

This feature adds profile image rendering to five views that currently show only placeholder icons/initials despite users having uploaded profile photos. The work spans two layers:

1. **Backend**: Four API response schemas (`RelativeInfo`, `PersonSearchResult`, `PersonNode`, `MatchGraphNode`) are missing the `profile_image_key` field. The corresponding service methods that construct these responses need to populate the field from the Person DB record.

2. **Frontend**: Five components need to use the existing `getPersonImageUrl` utility to render thumbnail images via the `Avatar`/`AvatarImage`/`AvatarFallback` pattern already established in the family-tree `PersonCard`.

The family-tree `PersonCard` component serves as the reference implementation — it already correctly renders profile images using `getPersonImageUrl` with the `thumbnail` variant.

## Architecture

The data flow for profile images follows this path:

```mermaid
graph LR
    DB[Person DB<br/>profile_image_key] --> Service[Backend Service<br/>_enrich methods]
    Service --> Schema[Response Schema<br/>profile_image_key field]
    Schema --> API[API Response<br/>JSON]
    API --> FE[Frontend Component]
    FE --> Util[getPersonImageUrl<br/>utility]
    Util --> URL[Image URL<br/>thumbnail]
    URL --> Avatar[Avatar Component<br/>AvatarImage + Fallback]
```

No new APIs, database changes, or new components are needed. This is purely about threading existing data through existing layers.

## Components and Interfaces

### Backend Schema Changes

Four Pydantic schemas need a new nullable field:

| Schema | File | Current Fields |
|--------|------|---------------|
| `RelativeInfo` | `backend/app/schemas/relatives_network/relatives_network_schemas.py` | person_id, first_name, last_name, gender_id, birth_year, death_year, district_name, locality_name, depth |
| `PersonSearchResult` | `backend/app/schemas/person/person_search.py` | person_id, first_name, middle_name, last_name, date_of_birth, gender_id, name_match_score |
| `PersonNode` | `backend/app/schemas/lineage_path/lineage_path_schemas.py` | person_id, first_name, last_name, birth_year, death_year, address, religion, from_person, to_person |
| `MatchGraphNode` | `backend/app/schemas/partner_match/partner_match_schemas.py` | person_id, first_name, last_name, birth_year, death_year, address, religion, is_match, depth, from_person, to_persons |

Each gets:
```python
profile_image_key: str | None = Field(default=None, description="Storage key for the person's profile image")
```

### Backend Service Changes

Four service methods construct the above schemas and need to pass `profile_image_key` from the Person record:

| Service | Method | File |
|---------|--------|------|
| `RelativesNetworkService` | `_enrich_relative_info` | `backend/app/services/relatives_network/relatives_network_service.py` |
| `PersonSearchService` | `search_persons` (two construction sites) | `backend/app/services/person/person_search_service.py` |
| `LineagePathService` | `_enrich_person_data` | `backend/app/services/lineage_path/lineage_path_service.py` |
| `PartnerMatchService` | `_enrich_node_data` + `_prune_graph` | `backend/app/services/partner_match/partner_match_service.py` |

The Person DB model already has `profile_image_key` as a column, so each service just needs to read `person.profile_image_key` and pass it to the schema constructor.

Note: `PartnerMatchService._prune_graph` manually reconstructs `MatchGraphNode` objects when pruning — it must also copy `profile_image_key` to the pruned nodes.

### Frontend Type Changes

Two TypeScript interfaces need a new optional field for the graph node data:

| Interface | File |
|-----------|------|
| `PersonNodeData` | `frontend/src/components/Rishte/types.ts` |
| `MatchPersonNodeData` | `frontend/src/components/FindPartner/types.ts` |

Each gets:
```typescript
profileImageKey?: string | null
```

### Frontend Transform Function Changes

Two transformer functions map API response data to React Flow node data and need to pass through `profile_image_key`:

| Function | File |
|----------|------|
| `createNodes` (in `transformApiResponse`) | `frontend/src/components/Rishte/utils/pathTransformer.ts` |
| `transformMatchPath` (node creation) | `frontend/src/components/FindPartner/utils/matchGraphTransformer.ts` |

### Frontend Component Changes

Five components need to render profile images:

| Component | File | Data Source for `profile_image_key` |
|-----------|------|-------------------------------------|
| `RelativeCard` | `frontend/src/components/RelativesNetwork/RelativeCard.tsx` | New prop `profileImageKey` passed from `RelativesResultsGrid` |
| `PersonSearchCard` | `frontend/src/components/Search/PersonSearchCard.tsx` | `person.profile_image_key` from `PersonSearchResult` API type |
| `PersonNode` | `frontend/src/components/Rishte/PersonNode.tsx` | `data.profileImageKey` from `PersonNodeData` |
| `MatchPersonNode` | `frontend/src/components/FindPartner/MatchPersonNode.tsx` | `data.profileImageKey` from `MatchPersonNodeData` |
| `User` (sidebar) | `frontend/src/components/Sidebar/User.tsx` | `activePerson.profile_image_key` from `ActivePersonContext` |

Each component follows the same pattern established in `PersonCard`:
```tsx
import { getPersonImageUrl } from "@/utils/personImage"
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar"

<Avatar>
  <AvatarImage
    src={getPersonImageUrl(profileImageKey, 'thumbnail')}
    alt={displayName}
  />
  <AvatarFallback>
    {/* existing fallback (icon or initials) */}
  </AvatarFallback>
</Avatar>
```

### Data Flow for RelativeCard (special case)

The `RelativeCard` receives individual props (not a typed API object), so the data flow requires changes at multiple levels:

1. Backend `RelativeInfo` schema → adds `profile_image_key`
2. Frontend `RelativeData` interface in `RelativesResultsGrid.tsx` → adds `profile_image_key`
3. `RelativesResultsGrid` → passes `profileImageKey` prop to `RelativeCard`
4. `RelativeCard` → accepts new `profileImageKey` prop and renders image

### Data Flow for User Sidebar

The sidebar `User` component receives the `currentUser` object (which is a `UserPublic` — no `profile_image_key`). To display the user's profile image, the component needs access to the user's person record. The `ActivePersonContext` already provides `activePerson` (a `PersonPublic` with `profile_image_key`). The `User` component needs to accept an optional `profileImageKey` prop, and `AppSidebar` needs to read it from the context and pass it down.

## Data Models

No new data models are needed. The existing `Person` DB model already has `profile_image_key: str | None`. The changes are purely about exposing this existing field through API response schemas and rendering it in frontend components.

### Existing Image URL Utility

```typescript
// frontend/src/utils/personImage.ts
export function getPersonImageUrl(
  profileImageKey: string | null | undefined,
  variant: "main" | "thumbnail" = "thumbnail",
): string | undefined {
  if (!profileImageKey) return undefined
  const key = variant === "thumbnail"
    ? profileImageKey.replace(/\.jpg$/, "_thumb.jpg")
    : profileImageKey
  const baseUrl = import.meta.env.VITE_API_URL || ""
  return `${baseUrl}/api/v1/uploads/person-images/${key}`
}
```

This utility returns `undefined` when no key is provided, which causes `AvatarImage` to not render and `AvatarFallback` to show instead — exactly the desired behavior.


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Thumbnail URL generation correctness

*For any* valid `profile_image_key` string ending in `.jpg`, calling `getPersonImageUrl(key, 'thumbnail')` should return a URL where the filename portion has `.jpg` replaced with `_thumb.jpg`, and the URL is prefixed with the correct API base URL.

**Validates: Requirements 2.1, 3.1, 4.1, 5.1, 6.1**

### Property 2: Backend service profile_image_key passthrough

*For any* Person record in the database, when a backend service constructs a response schema object (RelativeInfo, PersonSearchResult, PersonNode, or MatchGraphNode) for that person, the `profile_image_key` field in the response object should equal the `profile_image_key` field on the Person DB record.

**Validates: Requirements 1.5**

## Error Handling

Error handling is minimal for this feature since it leverages existing patterns:

1. **Missing profile_image_key (null)**: `getPersonImageUrl` returns `undefined`, causing `AvatarImage` to not render and `AvatarFallback` to display the existing fallback (gender icon or initials). No error state needed.

2. **Image load failure (broken URL, deleted file)**: The `AvatarImage` component from shadcn/ui handles this natively — if the image fails to load, `AvatarFallback` renders automatically. No additional error handling needed.

3. **Backend person not found**: The existing `_enrich_*` methods already handle this case by returning "Unknown" person data with null fields. Adding `profile_image_key=None` to these fallback objects maintains consistency.

## Testing Strategy

### Unit Tests (Backend - pytest)

For each of the four backend services, write unit tests verifying:
- When a person has `profile_image_key` set, the response schema includes the correct value
- When a person has `profile_image_key=None`, the response schema includes `None`

These are specific example tests, not property tests, since they validate concrete integration points.

### Unit Tests (Frontend - component tests)

For each of the five frontend components, verify:
- When `profileImageKey` is provided, the `AvatarImage` src matches the expected thumbnail URL
- When `profileImageKey` is null/undefined, the fallback renders

### Property-Based Tests

Property-based testing library: **fast-check** (TypeScript)

**Property 1 test**: Generate random strings ending in `.jpg` and verify `getPersonImageUrl` produces correct thumbnail URLs. Minimum 100 iterations. Tag: `Feature: profile-image-rendering, Property 1: Thumbnail URL generation correctness`

**Property 2 test**: Generate random Person mock objects with random `profile_image_key` values (including null) and verify the backend service methods pass the value through unchanged. Minimum 100 iterations. Tag: `Feature: profile-image-rendering, Property 2: Backend service profile_image_key passthrough`

Each correctness property is implemented by a single property-based test. Unit tests complement these by covering specific edge cases and component integration points.

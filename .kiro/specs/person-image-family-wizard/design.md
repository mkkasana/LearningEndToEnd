# Design Document: Person Image Upload in Family Wizard & Display

## Overview

This design adds profile image upload to the Add Family Member wizard and displays person images across the frontend. It introduces a reusable `ImageUpload` component with client-side compression using the `browser-image-compression` library, integrates it into the existing wizard flow, and updates PersonCard, family list, and PersonDetailsPanel to show profile images.

The design assumes the backend profile image API endpoints (from the `person-profile-image-backend` spec) are already implemented and available.

## Architecture

```mermaid
graph TD
    A[ImageUpload Component] -->|File selected| B[browser-image-compression]
    B -->|Compressed blob| A
    A -->|onChange callback| C[BasicInfoStep]
    C -->|imageFile in state| D[AddFamilyMemberDialog]
    D -->|Pass through steps| E[ConfirmationStep]
    E -->|1. Create person| F[PersonService API]
    E -->|2. Upload image| G[POST /persons/{id}/profile-image]
    
    H[getPersonImageUrl utility] -->|thumbnail URL| I[PersonCard Avatar]
    H -->|thumbnail URL| J[Family List Card]
    H -->|main URL| K[PersonDetailsPanel]
    
    L[PersonPublic.profile_image_key] --> H
```

Flow:
1. User selects an image in BasicInfoStep via the ImageUpload component
2. Image is compressed client-side (max 800x800, JPEG 80%)
3. Compressed file is stored in the wizard's state and passed through steps
4. On confirmation, person is created first, then image is uploaded as a separate API call
5. If image upload fails, person creation still succeeds (graceful degradation)
6. All display components use `getPersonImageUrl()` to resolve storage keys to URLs

## Components and Interfaces

### ImageUpload Component

Location: `frontend/src/components/Common/ImageUpload.tsx`

A reusable component that handles file selection, validation, client-side compression, and preview display.

```typescript
interface ImageUploadProps {
  value?: File | null
  onChange: (file: File | null) => void
  label?: string
  maxSizeMB?: number
  className?: string
}
```

Behavior:
- Renders a circular drop zone with a camera icon when empty
- On file select (click or drag-drop): validates type and size, compresses with `browser-image-compression`, calls `onChange` with compressed File
- Shows circular preview with a remove (X) button overlay when image is selected
- Displays inline error messages for invalid files
- Uses `useRef` for the hidden file input, triggered by clicking the drop zone
- Drag-and-drop uses `onDragOver`, `onDragLeave`, `onDrop` handlers with visual feedback (border highlight)

Client-side compression config:
```typescript
const options = {
  maxSizeMB: 1,
  maxWidthOrHeight: 800,
  useWebWorker: true,
  fileType: 'image/jpeg',
}
```

### AddFamilyMemberDialog State Update

Location: `frontend/src/components/Family/AddFamilyMemberDialog.tsx`

Add `imageFile` to the dialog's state:
```typescript
const [imageFile, setImageFile] = useState<File | null>(null)
```

Pass `imageFile` and `setImageFile` (or `onImageChange`) to BasicInfoStep and pass `imageFile` to ConfirmationStep.

On `handleClose`, reset `imageFile` to null.

### BasicInfoStep Update

Location: `frontend/src/components/Family/BasicInfoStep.tsx`

Add the ImageUpload component above the name fields:
```tsx
<ImageUpload
  value={imageFile}
  onChange={onImageChange}
  label="Profile Photo (Optional)"
/>
```

New props:
```typescript
interface BasicInfoStepProps {
  onComplete: (data: any) => void
  initialData?: any
  imageFile?: File | null
  onImageChange?: (file: File | null) => void
}
```

The image is NOT part of the form schema (not validated by zod) — it's managed separately via props to avoid serialization issues.

### ConfirmationStep Update

Location: `frontend/src/components/Family/ConfirmationStep.tsx`

New prop:
```typescript
interface ConfirmationStepProps {
  // ... existing props
  imageFile?: File | null
}
```

Changes to the mutation flow:
1. Steps 1-4 remain the same (create person, address, religion, relationship)
2. Add Step 5: If `imageFile` is not null, upload via `POST /persons/{personId}/profile-image`
3. Wrap Step 5 in try/catch — if it fails, show a warning toast but still call `onFinish()`

Display the image preview in the review summary if `imageFile` is present.

### Image Upload API Call

The upload uses `fetch` with `FormData` since the generated OpenAPI client may not handle multipart uploads well:

```typescript
async function uploadPersonImage(personId: string, file: File, token: string) {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await fetch(`/api/v1/persons/${personId}/profile-image`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData,
  })
  
  if (!response.ok) throw new Error('Image upload failed')
  return response.json()
}
```

### getPersonImageUrl Utility

Location: `frontend/src/utils/personImage.ts`

```typescript
export function getPersonImageUrl(
  profileImageKey: string | null | undefined,
  variant: 'main' | 'thumbnail' = 'thumbnail'
): string | undefined {
  if (!profileImageKey) return undefined
  
  const key = variant === 'thumbnail'
    ? profileImageKey.replace(/\.jpg$/, '_thumb.jpg')
    : profileImageKey
  
  // In local dev, images are served by the backend
  // In production, they come from CloudFront
  const baseUrl = import.meta.env.VITE_API_URL || ''
  return `${baseUrl}/api/v1/uploads/person-images/${key}`
}
```

For production with CloudFront, the `VITE_API_URL` would be the CloudFront distribution URL, so the path would resolve correctly since CloudFront routes `/api/*` to the ALB. Alternatively, a `VITE_IMAGES_URL` env var could be added for a dedicated images CDN, but the current CloudFront setup already handles this.

### PersonCard Update

Location: `frontend/src/components/FamilyTree/PersonCard.tsx`

Change the Avatar to use the profile image:
```tsx
import { getPersonImageUrl } from "@/utils/personImage"

// Inside the component:
const thumbnailUrl = getPersonImageUrl(person.profile_image_key, 'thumbnail')

<Avatar>
  <AvatarImage src={thumbnailUrl} alt={displayName} />
  <AvatarFallback className={getGenderAvatarClass(person.gender_id)}>
    <User className="size-1/2" />
  </AvatarFallback>
</Avatar>
```

The `AvatarFallback` already handles the case when `AvatarImage` fails to load (shadcn/ui behavior).

### Family List Card Update

Location: `frontend/src/routes/_layout/family.tsx`

Add an Avatar to each family member card in the grid:
```tsx
import { getPersonImageUrl } from "@/utils/personImage"

// Inside the card:
const thumbnailUrl = getPersonImageUrl(person.profile_image_key, 'thumbnail')

<Avatar className="h-10 w-10">
  <AvatarImage src={thumbnailUrl} alt={`${person.first_name} ${person.last_name}`} />
  <AvatarFallback>
    <User className="h-5 w-5" />
  </AvatarFallback>
</Avatar>
```

### PersonDetailsPanel Update

Location: `frontend/src/components/FamilyTree/PersonDetailsPanel.tsx`

Display the main (larger) image at the top of the panel:
```tsx
const mainUrl = getPersonImageUrl(person.profile_image_key, 'main')

<Avatar className="h-24 w-24">
  <AvatarImage src={mainUrl} alt={displayName} />
  <AvatarFallback>
    <User className="h-12 w-12" />
  </AvatarFallback>
</Avatar>
```

## Data Models

### Frontend State

The image file is managed as React state (`File | null`) in the AddFamilyMemberDialog, not as part of the form data. This avoids serialization issues with zod and react-hook-form.

### PersonPublic Type Update

After regenerating the OpenAPI client (once the backend is deployed), the `PersonPublic` type will include:
```typescript
profile_image_key?: string | null
```

This field is used by `getPersonImageUrl()` to resolve image URLs.

### New Dependency

Add `browser-image-compression` to frontend dependencies:
```bash
npm install browser-image-compression
```

This library handles client-side image resizing and compression in a web worker, keeping the main thread responsive.


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Invalid file type rejection

*For any* file with a MIME type not in the set {image/jpeg, image/png, image/webp}, the ImageUpload component should display an error message and not call the onChange callback with a file.

**Validates: Requirements 1.5**

### Property 2: Wizard image state preservation

*For any* image file selected in BasicInfoStep, navigating forward to AddressStep and then back to BasicInfoStep should preserve the selected image (the preview should still be visible and the file reference should be the same).

**Validates: Requirements 2.2**

### Property 3: PersonCard conditional image display

*For any* PersonDetails object, if `profile_image_key` is non-null, the PersonCard Avatar should render an img element with a src matching the thumbnail URL pattern; if `profile_image_key` is null, the Avatar should render the gender-based fallback icon.

**Validates: Requirements 3.1, 3.2**

### Property 4: Family list conditional image display

*For any* family member object, if `profile_image_key` is non-null, the family list card should render an Avatar with a thumbnail image src; if null, it should render a fallback icon.

**Validates: Requirements 4.1, 4.2**

### Property 5: PersonDetailsPanel conditional image display

*For any* PersonDetails object, if `profile_image_key` is non-null, the PersonDetailsPanel should render the main image URL; if null, it should render a placeholder icon.

**Validates: Requirements 5.1, 5.2**

### Property 6: URL resolution correctness

*For any* non-null `profile_image_key` string and any variant (`main` or `thumbnail`), `getPersonImageUrl` should return a string containing the key (or derived thumbnail key) and the API base URL. For null/undefined keys, it should return undefined.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 7: Thumbnail key derivation

*For any* filename string ending in `.jpg`, the thumbnail variant should be derived by replacing `.jpg` with `_thumb.jpg`. The original key should be recoverable by reversing this transformation.

**Validates: Requirements 6.5**

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Invalid file type selected | Inline error message in ImageUpload component, file not accepted |
| File exceeds 5 MB | Inline error message in ImageUpload component, file not accepted |
| Client-side compression fails | Show error toast, allow user to try a different image |
| Image upload API fails after person creation | Warning toast "Profile photo could not be uploaded, but the family member was added successfully. You can add a photo later." Person creation is not rolled back. |
| Image URL fails to load (broken image) | AvatarFallback renders the gender-based icon (handled by shadcn/ui Avatar) |
| Network error during upload | Standard error toast from the mutation error handler |

## Testing Strategy

### Dual Testing Approach

**Unit Tests** (Vitest + React Testing Library):
- ImageUpload component: renders default state, handles file selection, shows preview, shows error for invalid files, calls onChange
- BasicInfoStep: renders ImageUpload component, passes image data through
- ConfirmationStep: shows image preview, calls upload API after person creation, handles upload failure gracefully
- PersonCard: renders thumbnail when profile_image_key exists, renders fallback when null
- Family list: renders avatars with/without images
- PersonDetailsPanel: renders main image when key exists
- getPersonImageUrl: returns correct URLs for all variants and environments

**Property-Based Tests** (fast-check):
- Use `fast-check` library for property-based testing in the frontend
- Custom arbitraries for generating random profile_image_key strings (UUID-based .jpg filenames)
- Each property test runs minimum 100 iterations
- Each test tagged with: `Feature: person-image-family-wizard, Property {N}: {title}`

**Test File Locations**:
- `frontend/src/components/Common/ImageUpload.test.tsx`
- `frontend/src/utils/personImage.test.ts`
- `frontend/src/components/FamilyTree/PersonCard.test.tsx` (update existing)
- `frontend/src/components/FamilyTree/PersonDetailsPanel.test.tsx` (update existing)

# Project Settings

This is a FastAPI + React full-stack project for personal/family management.

## Disabled Global Steering

The `amazon-builder-steering` rules do not apply to this project. This is a personal learning project, not an Amazon internal project.

## Project Stack

- Backend: Python, FastAPI, SQLModel, PostgreSQL
- Frontend: React, TypeScript, TanStack Query, Vite
- Testing: pytest (backend), Playwright (frontend E2E)

# Project build and restart components

## Useful project specifc commands

* To stop frontend component: `docker compose down frontend`
* To stop backend component: `docker compose down backend`
* To stop all component: `docker compose down`
* To remove old fronend component docker images: `docker rmi frontend:lasted`
* To remove old backend component docker images: `docker rmi backend:lasted`
* To build docker for frontend : `docker compose build --no-cache frontend`
* To build docker for backend : `docker compose build --no-cache backend`
* To start all component : `docker compose up -d`
* Commands to fresh restart components: "docker compose down && docker rmi frontend:latest backend:latest && docker compose build --no-cache && docker compose up -d"

* Command to regenerate the open api client: `npm run generate-client`
* To build the backend including test cases, Run command "hatch run build-all" in side the backend folder.
## Note
* When new changes are made, Always make sure to rebuild image to sync changes in docker comtainer.
* For testing you can username: testfamily@family.com and password: qweqweqwe
* If new endpoint is introduced or edited any, To make those available to user you need to rebuild backend image and restart the server other wise those wont be synced automatically. 

## Coding best practises
* For any new code written in backend should have Unit tests
* Have proper logging so user can just debug things easily from logs it self.

## Backend Schema to Frontend Type Sync

When modifying backend Pydantic schemas or adding new API endpoints, follow these steps to make changes available to the frontend:

1. **Modify backend code** - Edit files in `backend/app/schemas/`, `backend/app/api/routes/`, or `backend/app/services/`
2. **Rebuild & restart backend** - `docker compose build --no-cache backend && docker compose up -d`
3. **Wait for backend to be ready** - The backend must be running and accessible at `http://localhost:8000`
4. **Regenerate OpenAPI client** - Run `npm run generate-client` in the `frontend/` folder
   - This command does TWO things:
     1. Fetches the latest OpenAPI spec from `http://localhost:8000/api/v1/openapi.json`
     2. Generates TypeScript types and SDK methods
   - Generated files: `frontend/src/client/types.gen.ts`, `frontend/src/client/sdk.gen.ts`, `frontend/src/client/schemas.gen.ts`
5. **Update frontend code** - Use the new types/methods from the generated client
6. **Rebuild frontend** - `docker compose build --no-cache frontend && docker compose up -d`

### OpenAPI Client Generation Scripts

| Command | Description |
|---------|-------------|
| `npm run generate-client` | Fetches latest spec from backend AND generates client (recommended) |
| `npm run generate-client:local` | Only generates client from existing `openapi.json` file (use if backend is down) |

**Important Notes:**
- The backend MUST be running when you run `npm run generate-client`
- If you get a connection error, ensure the backend is up: `docker compose ps`
- The `openapi.json` file in the frontend folder is a cached copy of the spec
- Always use `generate-client` (not `generate-client:local`) to ensure you have the latest API

## Database Migrations

This project uses two PostgreSQL databases:
- `app` - Main application database
- `app_test` - Test database (used by pytest)

### Running Migrations

When creating new Alembic migrations that modify the database schema:

1. **Apply to main database** (usually done automatically by Docker):
   ```bash
   cd backend
   source .venv/bin/activate && alembic upgrade head
   ```

2. **Apply to test database** (required for backend tests to pass):
   ```bash
   cd backend
   source .venv/bin/activate && POSTGRES_DB=app_test alembic upgrade head
   ```

### Important Notes
- After completing a spec that includes database migrations, always apply migrations to BOTH databases
- The test database (`app_test`) is configured via `POSTGRES_TEST_DB` in `.env`
- Backend tests will fail if the test database schema is out of sync with the models
- Migration files are located in `backend/app/alembic/versions/`


## Colima (Docker Runtime)

This project uses Colima as the Docker runtime on macOS instead of Docker Desktop.

### DNS Issues
Colima's VM can lose DNS resolution, causing `npm install` and `uv sync` to time out during Docker builds. Fix by restarting with explicit DNS:
```bash
colima stop
colima start --dns 8.8.8.8 --dns 1.1.1.1
```

### I/O Errors / Corrupted Storage
If you see `input/output error` during builds or `docker system prune`, the Colima VM disk is corrupted. Fix:
```bash
colima stop
colima delete
colima start --dns 8.8.8.8 --dns 1.1.1.1
```

### BuildKit Cache Issues
If builds fail with corrupted wheel/package errors (e.g., "Metadata field not found"), clear the BuildKit cache:
```bash
docker builder prune -f
```

## Frontend API Calls

The frontend runs on nginx at `localhost:5173` which does NOT proxy `/api` requests to the backend. The backend runs separately at `localhost:8000`.

- The generated OpenAPI client uses `VITE_API_URL` (set to `http://localhost:8000` at build time) so its calls reach the backend correctly.
- Any raw `fetch()` calls in frontend code MUST use `import.meta.env.VITE_API_URL` as the base URL, not relative paths. Relative paths like `/api/v1/...` will hit nginx and silently fail.

Example:
```typescript
const apiBase = import.meta.env.VITE_API_URL || ""
const response = await fetch(`${apiBase}/api/v1/some-endpoint`, { ... })
```

## Backend Response Schemas

When adding a new field to the Person DB model, remember to add it to ALL response schemas that return person data, not just `PersonPublic`. Key schemas to check:
- `PersonPublic` in `backend/app/schemas/person/person.py`
- `PersonDetails` in `backend/app/schemas/person/person_relationship.py`
- `PersonCompleteDetailsResponse` in `backend/app/schemas/person/person_complete_details.py`

Also update any service code that manually constructs these response objects (e.g., `PersonCompleteDetailsResponse(...)` in `person_service.py`).


## Image Storage — Production Readiness

The backend has a storage abstraction (`backend/app/services/storage/`) that switches based on `settings.ENVIRONMENT`:
- `"local"` → `LocalStorage` — saves to `backend/uploads/person-images/`, served via FastAPI static files
- Any other value → `S3Storage` — uploads to S3, serves via CloudFront

### Backend Config Needed for Prod
Set these environment variables:
- `ENVIRONMENT` = `"production"` (or anything other than `"local"`)
- `S3_IMAGES_BUCKET` = your S3 bucket name
- `CLOUDFRONT_IMAGES_URL` = your CloudFront distribution URL (e.g., `https://d1234.cloudfront.net`)

### Frontend Config for Prod
The `getPersonImageUrl` utility (`frontend/src/utils/personImage.ts`) supports both local and production URLs:
- If `VITE_IMAGES_URL` is set, uses `{VITE_IMAGES_URL}/person-images/{key}` (CloudFront)
- Otherwise falls back to `{VITE_API_URL}/api/v1/uploads/person-images/{key}` (local dev)

### How Image Keys Work
- `profile_image_key` stores just the filename (e.g., `a3f6516cba4e4ed78d9a16d97f6bf883.jpg`)
- Thumbnail is derived by replacing `.jpg` with `_thumb.jpg`
- Both main and thumbnail are uploaded to storage on creation
- The storage backend's `get_url()` builds the full URL (local path or CloudFront URL)

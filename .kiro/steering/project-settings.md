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

When modifying backend Pydantic schemas that are used in API responses, follow these steps to make changes available to the frontend:

1. **Modify backend schema** - Edit files in `backend/app/schemas/`
2. **Update backend service** - Populate new fields in the service layer
3. **Rebuild & restart backend** - `docker compose build --no-cache backend && docker compose up -d`
4. **Regenerate OpenAPI client** - Run `npm run generate-client` in the `frontend/` folder
   - This fetches the OpenAPI spec from the running backend and generates TypeScript types
   - Generated files: `frontend/src/client/types.gen.ts`, `frontend/src/client/schemas.gen.ts`
5. **Update frontend code** - Use the new fields from the generated types
6. **Rebuild frontend** - `docker compose build --no-cache frontend && docker compose up -d`

**Important:** The backend must be running when you run `npm run generate-client` because it fetches the OpenAPI spec from `http://localhost/api/v1/openapi.json`.
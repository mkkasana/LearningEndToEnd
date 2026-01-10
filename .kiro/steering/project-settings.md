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
* Commands to fresh restart components: "docker compose down && docker rmi frontend:lasted backend:lasted && docker compose build --no-cache && docker compose up -d"

* Command to regenerate the open api client: `npm run generate-client`
## Note
* When new changes are made, Always make sure to rebuild image to sync changes in docker comtainer.
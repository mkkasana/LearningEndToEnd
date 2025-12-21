# LearningEndToEnd - Frontend

The frontend is built with [Vite](https://vitejs.dev/), [React](https://reactjs.org/), [TypeScript](https://www.typescriptlang.org/), [TanStack Query](https://tanstack.com/query), [TanStack Router](https://tanstack.com/router) and [Tailwind CSS](https://tailwindcss.com/).

## Requirements

* **Node.js 20.19+ or 22.12+** (Node 24 recommended)
* **npm** (comes with Node.js)

## Quick Start

### 1. Install Node.js

The project requires Node.js version 24 (specified in `.nvmrc`).

If you're using `mise`:

```bash
cd frontend
mise use node@24
```

If you're using `nvm`:

```bash
cd frontend
nvm install
nvm use
```

If you're using `fnm`:

```bash
cd frontend
fnm install
fnm use
```

Verify your Node.js version:

```bash
node --version  # Should show v24.x.x or v22.12+
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start Development Server

```bash
npm run dev
```

Then open your browser at http://localhost:5173/.

## Building the Frontend

### Build with Quality Checks (Recommended)

This runs linting, type checking, and builds the production bundle:

```bash
bash scripts/build.sh
```

### Build Output

The build creates optimized static files in `dist/`:
- `dist/index.html` - Entry point
- `dist/assets/` - JavaScript, CSS, and static assets

Total size: ~864KB (optimized and minified)

### Manual Build Steps

If you prefer to run each step individually:

```bash
# Install dependencies
npm install

# Run linter and auto-fix issues
npm run lint

# Build for production (TypeScript check + Vite build)
npm run build

# Preview production build locally
npm run preview
```

## Available Scripts

```bash
npm run dev              # Start development server (http://localhost:5173)
npm run build            # Build for production (TypeScript + Vite)
npm run lint             # Lint and format code with Biome
npm run preview          # Preview production build locally
npm run generate-client  # Generate API client from OpenAPI spec
```

## Development Workflow

The recommended workflow is to use the local development server (not Docker) for fast iteration with hot module replacement (HMR).

```bash
npm run dev
```

This provides:
- ⚡ Instant hot module replacement
- 🔍 Better error messages
- 🚀 Faster development cycle

Once you're happy with your changes, build the production version to test performance and bundle size.

## Docker Build

To build a production Docker image:

```bash
docker build -t learning-end-to-end-frontend:latest .
```

The Dockerfile uses a multi-stage build:
1. **Build stage**: Compiles TypeScript and bundles with Vite
2. **Production stage**: Serves static files with Nginx

## Configuration

### Environment Variables

The frontend uses environment variables prefixed with `VITE_`:

- `VITE_API_URL` - Backend API URL (default: `http://localhost:8000`)

Set these in `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

For production builds, pass as build arguments:

```bash
docker build --build-arg VITE_API_URL=https://api.yourdomain.com -t frontend .
```

### Using a Remote API

To connect to a remote backend API, update `frontend/.env`:

```env
VITE_API_URL=https://api.my-domain.example.com
```

## Generate API Client

The frontend uses an auto-generated TypeScript client based on the backend's OpenAPI specification.

### Automatically (Recommended)

From the project root:

```bash
bash scripts/generate-client.sh
```

This script:
1. Starts the backend
2. Downloads the OpenAPI spec
3. Generates the TypeScript client
4. Updates `frontend/src/client/`

### Manually

1. Start the backend:
```bash
docker compose up -d backend
```

2. Download the OpenAPI spec:
```bash
curl http://localhost:8000/api/v1/openapi.json -o frontend/openapi.json
```

3. Generate the client:
```bash
cd frontend
npm run generate-client
```

4. Commit the changes

**Note:** Regenerate the client whenever the backend API changes.

## Code Structure

The frontend code is structured as follows:

* `frontend/src` - The main frontend code.
* `frontend/src/assets` - Static assets.
* `frontend/src/client` - The generated OpenAPI client.
* `frontend/src/components` -  The different components of the frontend.
* `frontend/src/hooks` - Custom hooks.
* `frontend/src/routes` - The different routes of the frontend which include the pages.

## End-to-End Testing with Playwright

The frontend includes initial end-to-end tests using Playwright. To run the tests, you need to have the Docker Compose stack running. Start the stack with the following command:

```bash
docker compose up -d --wait backend
```

Then, you can run the tests with the following command:

```bash
npx playwright test
```

You can also run your tests in UI mode to see the browser and interact with it running:

```bash
npx playwright test --ui
```

To stop and remove the Docker Compose stack and clean the data created in tests, use the following command:

```bash
docker compose down -v
```

To update the tests, navigate to the tests directory and modify the existing test files or add new ones as needed.

For more information on writing and running Playwright tests, refer to the official [Playwright documentation](https://playwright.dev/docs/intro).

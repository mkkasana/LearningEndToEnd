# LearningEndToEnd - Backend

## Requirements

* [Docker](https://www.docker.com/) (for running tests with database).
* [uv](https://docs.astral.sh/uv/) for Python package and environment management.
* [hatch](https://hatch.pypa.io/) for building packages (optional, can use `python -m build`).

## Quick Start

### Install Dependencies

From `./backend/` directory:

```bash
uv sync
```

### Activate Virtual Environment

```bash
source .venv/bin/activate
```

Make sure your editor is using the correct Python virtual environment, with the interpreter at `backend/.venv/bin/python`.

## Building the Package

### Build with Quality Checks (Recommended)

This runs type checking, linting, format checking, and builds the package:

```bash
bash scripts/build.sh
```

**Note:** The build script skips unit tests by default since they require a PostgreSQL database. See the "Running Tests" section below if you want to include tests in the build.

### Build Output

The build creates two artifacts in `dist/`:
- `app-0.1.0-py3-none-any.whl` - Wheel package
- `app-0.1.0.tar.gz` - Source distribution

### Manual Build Steps

If you prefer to run each step individually:

```bash
# Type checking
mypy app

# Linting
ruff check app

# Format checking
ruff format app --check

# Build package
hatch build
```

### Build with Tests

To include unit tests in the build process, you need a running PostgreSQL database:

1. Start the database with Docker Compose:
```bash
cd ..  # Go to project root
docker compose up -d db
cd backend
```

2. Edit `scripts/build.sh` and uncomment the test lines:
```bash
# Uncomment these lines in scripts/build.sh:
coverage run -m pytest tests/
coverage report --fail-under=80
coverage html --title "coverage"
```

3. Run the build:
```bash
bash scripts/build.sh
```

## Architecture

This backend follows a **Clean Architecture** pattern with clear separation of concerns:

```
api/          → HTTP routes (thin controllers)
services/     → Business logic
repositories/ → Data access layer
schemas/      → API contracts (DTOs)
models/       → Database entities
```

### 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete architecture overview
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick start guide and templates
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migration from legacy structure
- **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)** - Visual diagrams
- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - What changed and why
- **[documentation/LOGGING.md](documentation/LOGGING.md)** - Comprehensive logging guide
- **[documentation/LOGGING_QUICK_REFERENCE.md](documentation/LOGGING_QUICK_REFERENCE.md)** - Logging quick reference

### Adding New Features

Follow the 5-step pattern:

1. **Model** (`models/`) - Database entity
2. **Schemas** (`schemas/`) - API contracts
3. **Repository** (`repositories/`) - Data access
4. **Service** (`services/`) - Business logic
5. **Routes** (`api/routes/`) - HTTP endpoints

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for templates and examples.

## Development

### Logging

The backend includes comprehensive logging with automatic sensitive data masking and request tracing.

**View logs:**
```bash
# All logs
docker compose logs -f backend

# Only errors
docker compose logs backend | grep ERROR

# Specific user activity
docker compose logs backend | grep "user@example.com"
```

**Features:**
- ✅ Automatic sensitive data masking (passwords, tokens, secrets)
- ✅ Request/response logging with unique request IDs
- ✅ Performance monitoring (execution time tracking)
- ✅ User context in authenticated requests
- ✅ Environment-based log levels (DEBUG/INFO/WARNING)

See [documentation/LOGGING.md](documentation/LOGGING.md) for complete guide.

### Current Structure

**New Architecture (Recommended):**
- Models: `./backend/app/models/`
- Schemas: `./backend/app/schemas/`
- Repositories: `./backend/app/repositories/`
- Services: `./backend/app/services/`
- API Routes: `./backend/app/api/routes/`

**Legacy Files (Backward Compatible):**
- `./backend/app/models.py` - Now imports from new structure
- `./backend/app/crud.py` - Still available for compatibility

New features should use the new architecture. See documentation above for details.

## VS Code

There are already configurations in place to run the backend through the VS Code debugger, so that you can use breakpoints, pause and explore variables, etc.

The setup is also already configured so you can run the tests through the VS Code Python tests tab.

## Docker Compose Override

During development, you can change Docker Compose settings that will only affect the local development environment in the file `docker-compose.override.yml`.

The changes to that file only affect the local development environment, not the production environment. So, you can add "temporary" changes that help the development workflow.

For example, the directory with the backend code is synchronized in the Docker container, copying the code you change live to the directory inside the container. That allows you to test your changes right away, without having to build the Docker image again. It should only be done during development, for production, you should build the Docker image with a recent version of the backend code. But during development, it allows you to iterate very fast.

There is also a command override that runs `fastapi run --reload` instead of the default `fastapi run`. It starts a single server process (instead of multiple, as would be for production) and reloads the process whenever the code changes. Have in mind that if you have a syntax error and save the Python file, it will break and exit, and the container will stop. After that, you can restart the container by fixing the error and running again:

```console
$ docker compose watch
```

There is also a commented out `command` override, you can uncomment it and comment the default one. It makes the backend container run a process that does "nothing", but keeps the container alive. That allows you to get inside your running container and execute commands inside, for example a Python interpreter to test installed dependencies, or start the development server that reloads when it detects changes.

To get inside the container with a `bash` session you can start the stack with:

```console
$ docker compose watch
```

and then in another terminal, `exec` inside the running container:

```console
$ docker compose exec backend bash
```

You should see an output like:

```console
root@7f2607af31c3:/app#
```

that means that you are in a `bash` session inside your container, as a `root` user, under the `/app` directory, this directory has another directory called "app" inside, that's where your code lives inside the container: `/app/app`.

There you can use the `fastapi run --reload` command to run the debug live reloading server.

```console
$ fastapi run --reload app/main.py
```

...it will look like:

```console
root@7f2607af31c3:/app# fastapi run --reload app/main.py
```

and then hit enter. That runs the live reloading server that auto reloads when it detects code changes.

Nevertheless, if it doesn't detect a change but a syntax error, it will just stop with an error. But as the container is still alive and you are in a Bash session, you can quickly restart it after fixing the error, running the same command ("up arrow" and "Enter").

...this previous detail is what makes it useful to have the container alive doing nothing and then, in a Bash session, make it run the live reload server.

## Running Tests

**Important:** Tests require a PostgreSQL database to run.

### Option 1: Using Docker Compose (Recommended)

Start the full stack with Docker Compose following the guide in [../development.md](../development.md).

```bash
# From project root
docker compose up -d

# Run tests inside the container
docker compose exec backend bash scripts/tests-start.sh
```

### Option 2: Local Testing

If your stack is already up and you just want to run the tests:

```bash
bash ./scripts/test.sh
```

The tests run with Pytest, modify and add tests to `./backend/tests/`.

### Test with Specific Options

To stop on first error:

```bash
docker compose exec backend bash scripts/tests-start.sh -x
```

### Test Coverage

When the tests are run, a file `htmlcov/index.html` is generated, you can open it in your browser to see the coverage of the tests.

## Code Quality

### Linting

```bash
bash scripts/lint.sh
```

This runs:
- `mypy` for type checking
- `ruff check` for linting
- `ruff format --check` for format checking

### Auto-formatting

```bash
bash scripts/format.sh
```

This automatically fixes linting issues and formats code with `ruff`.

## Docker Compose

Start the local development environment with Docker Compose following the guide in [../development.md](../development.md).

## Migrations

As during local development your app directory is mounted as a volume inside the container, you can also run the migrations with `alembic` commands inside the container and the migration code will be in your app directory (instead of being only inside the container). So you can add it to your git repository.

Make sure you create a "revision" of your models and that you "upgrade" your database with that revision every time you change them. As this is what will update the tables in your database. Otherwise, your application will have errors.

* Start an interactive session in the backend container:

```console
$ docker compose exec backend bash
```

* Alembic is already configured to import your SQLModel models from `./backend/app/models.py`.

* After changing a model (for example, adding a column), inside the container, create a revision, e.g.:

```console
$ alembic revision --autogenerate -m "Add column last_name to User model"
```

* Commit to the git repository the files generated in the alembic directory.

* After creating the revision, run the migration in the database (this is what will actually change the database):

```console
$ alembic upgrade head
```

If you don't want to use migrations at all, uncomment the lines in the file at `./backend/app/core/db.py` that end in:

```python
SQLModel.metadata.create_all(engine)
```

and comment the line in the file `scripts/prestart.sh` that contains:

```console
$ alembic upgrade head
```

If you don't want to start with the default models and want to remove them / modify them, from the beginning, without having any previous revision, you can remove the revision files (`.py` Python files) under `./backend/app/alembic/versions/`. And then create a first migration as described above.

## Email Templates

The email templates are in `./backend/app/email-templates/`. Here, there are two directories: `build` and `src`. The `src` directory contains the source files that are used to build the final email templates. The `build` directory contains the final email templates that are used by the application.

Before continuing, ensure you have the [MJML extension](https://marketplace.visualstudio.com/items?itemName=attilabuti.vscode-mjml) installed in your VS Code.

Once you have the MJML extension installed, you can create a new email template in the `src` directory. After creating the new email template and with the `.mjml` file open in your editor, open the command palette with `Ctrl+Shift+P` and search for `MJML: Export to HTML`. This will convert the `.mjml` file to a `.html` file and now you can save it in the build directory.

# Backend Project Structure

## Overview

This document describes the organized structure of the backend project following clean architecture principles.

## Directory Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── address/          # Address-related routes
│   │   │   │   ├── __init__.py
│   │   │   │   └── metadata.py   # Countries & states endpoints
│   │   │   ├── auth.py           # Authentication routes
│   │   │   ├── items.py          # Items CRUD routes
│   │   │   ├── users.py          # Users CRUD routes
│   │   │   ├── utils.py          # Utility routes
│   │   │   └── private.py        # Private/dev routes
│   │   ├── deps.py               # Dependency injection
│   │   └── main.py               # API router aggregation
│   ├── core/
│   │   ├── config.py             # Configuration
│   │   ├── db.py                 # Database setup
│   │   └── security.py           # Security utilities
│   ├── db_models/                # SQLModel database models
│   │   ├── user.py
│   │   ├── item.py
│   │   ├── country.py
│   │   └── state.py
│   ├── schemas/                  # Pydantic schemas (API contracts)
│   │   ├── user.py
│   │   ├── item.py
│   │   ├── country.py
│   │   └── state.py
│   ├── repositories/             # Data access layer
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── item_repository.py
│   │   ├── country_repository.py
│   │   └── state_repository.py
│   ├── services/                 # Business logic layer
│   │   ├── user_service.py
│   │   ├── item_service.py
│   │   ├── auth_service.py
│   │   ├── country_service.py
│   │   └── state_service.py
│   ├── alembic/                  # Database migrations
│   │   └── versions/
│   │       ├── e2412789c190_initialize_models.py
│   │       ├── 9c0a54914c78_add_max_length_for_string_varchar_.py
│   │       ├── d98dd8ec85a3_edit_replace_id_integers_in_all_models_.py
│   │       ├── 1a31ce608336_add_cascade_delete_relationships.py
│   │       ├── f3a1b2c4d5e6_add_country_table.py
│   │       └── a1b2c3d4e5f6_add_state_table.py
│   └── main.py                   # FastAPI application entry
├── init_seed/                    # Initial data seeding scripts
│   ├── README.md
│   ├── seed_countries.py
│   └── seed_states.py
├── tests/
│   ├── api/                      # API unit tests
│   ├── crud/                     # CRUD operation tests
│   └── integration_scripts/      # Manual integration test scripts
│       ├── README.md
│       └── test_countries_api.sh
├── documentation/                # Project documentation
│   ├── address/
│   │   ├── ADDRESS_METADATA_API.md
│   │   ├── country/
│   │   │   ├── COUNTRIES_API_GUIDE.md
│   │   │   ├── COUNTRIES_API_FLOW.md
│   │   │   ├── COUNTRIES_API_CRUD_TEST_RESULTS.md
│   │   │   └── COUNTRIES_API_QUICK_REFERENCE.md
│   │   └── state/
│   │       └── STATES_API_TEST_RESULTS.md
│   ├── DATABASE_WORKFLOW.md
│   ├── ARCHITECTURE.md
│   └── ...
├── scripts/                      # Build and utility scripts
│   ├── build.sh
│   ├── format.sh
│   ├── lint.sh
│   └── test.sh
├── alembic.ini                   # Alembic configuration
├── pyproject.toml                # Python dependencies
└── Dockerfile                    # Docker configuration
```

## Architecture Layers

### 1. Routes Layer (`app/api/routes/`)

**Purpose:** HTTP endpoint definitions

**Organization:**
- Group related routes in subfolders (e.g., `address/`)
- Each file handles a specific domain
- Keep routes thin - delegate to services

**Example:**
```python
# app/api/routes/address/metadata.py
@router.get("/countries")
def get_countries(session: SessionDep):
    service = CountryService(session)
    return service.get_countries()
```

### 2. Services Layer (`app/services/`)

**Purpose:** Business logic

**Responsibilities:**
- Validate business rules
- Orchestrate repository calls
- Transform data between layers
- Handle complex operations

**Example:**
```python
# app/services/country_service.py
class CountryService:
    def get_countries(self):
        countries = self.country_repo.get_active_countries()
        return [CountryPublic(...) for country in countries]
```

### 3. Repository Layer (`app/repositories/`)

**Purpose:** Data access

**Responsibilities:**
- Database queries
- CRUD operations
- No business logic
- Return database models

**Example:**
```python
# app/repositories/country_repository.py
class CountryRepository(BaseRepository[Country]):
    def get_active_countries(self):
        return self.session.exec(
            select(Country).where(Country.is_active == True)
        ).all()
```

### 4. Models Layer (`app/db_models/`)

**Purpose:** Database table definitions

**Characteristics:**
- SQLModel classes
- Table structure
- Relationships
- Constraints

**Example:**
```python
# app/db_models/country.py
class Country(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
```

### 5. Schemas Layer (`app/schemas/`)

**Purpose:** API contracts (request/response)

**Types:**
- `*Create` - POST request body
- `*Update` - PATCH request body
- `*Public` - GET response
- `*DetailPublic` - Detailed response

**Example:**
```python
# app/schemas/country.py
class CountryCreate(SQLModel):
    name: str
    code: str

class CountryPublic(SQLModel):
    countryId: uuid.UUID
    countryName: str
```

## Naming Conventions

### Files
- Snake case: `country_service.py`
- Descriptive: `user_repository.py`
- Suffix indicates purpose: `*_service.py`, `*_repository.py`

### Classes
- Pascal case: `CountryService`
- Singular: `Country` not `Countries`
- Descriptive: `CountryRepository`

### Functions
- Snake case: `get_countries()`
- Verb-noun: `create_country()`, `update_user()`
- Clear intent: `get_active_countries()`

### Routes
- Kebab case: `/address/countries`
- Plural for collections: `/countries`
- Singular for resources: `/country/{id}`
- Nested for relationships: `/country/{id}/states`

## Best Practices

### Route Organization

✅ **DO:**
```
routes/
├── address/
│   └── metadata.py    # Countries & states
├── auth.py            # Authentication
└── users.py           # User management
```

❌ **DON'T:**
```
routes/
├── metadata.py        # Too generic
├── route1.py          # Non-descriptive
└── all_routes.py      # Too broad
```

### Service Layer

✅ **DO:**
- Keep business logic in services
- Services call repositories
- Services transform data
- Services validate business rules

❌ **DON'T:**
- Put business logic in routes
- Access database directly from routes
- Mix concerns

### Repository Layer

✅ **DO:**
- Simple database queries
- Return database models
- Extend BaseRepository
- Specific query methods

❌ **DON'T:**
- Business logic in repositories
- Transform to API schemas
- Complex orchestration

## Adding New Features

### 1. Create Database Model

```python
# app/db_models/city.py
class City(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    state_id: uuid.UUID = Field(foreign_key="state.id")
```

### 2. Create Migration

```bash
alembic revision -m "add_city_table"
# Edit the generated migration file
alembic upgrade head
```

### 3. Create Schemas

```python
# app/schemas/city.py
class CityCreate(SQLModel):
    name: str
    state_id: uuid.UUID

class CityPublic(SQLModel):
    cityId: uuid.UUID
    cityName: str
```

### 4. Create Repository

```python
# app/repositories/city_repository.py
class CityRepository(BaseRepository[City]):
    def get_by_state(self, state_id: UUID):
        return self.session.exec(
            select(City).where(City.state_id == state_id)
        ).all()
```

### 5. Create Service

```python
# app/services/city_service.py
class CityService:
    def __init__(self, session: Session):
        self.city_repo = CityRepository(session)
    
    def get_cities_by_state(self, state_id: UUID):
        cities = self.city_repo.get_by_state(state_id)
        return [CityPublic(...) for city in cities]
```

### 6. Create Routes

```python
# app/api/routes/address/metadata.py
@router.get("/state/{state_id}/cities")
def get_cities(session: SessionDep, state_id: uuid.UUID):
    service = CityService(session)
    return service.get_cities_by_state(state_id)
```

### 7. Create Seed Script (Optional)

```python
# init_seed/seed_cities.py
def seed_cities():
    # Populate initial city data
    pass
```

### 8. Document

```markdown
# documentation/address/CITIES_API.md
## GET /metadata/address/state/{state_id}/cities
...
```

### 9. Test

```bash
# Rebuild and test
docker-compose down
docker-compose up -d --build

# Test endpoint
curl http://localhost:8000/api/v1/metadata/address/state/{id}/cities
```

## Testing Strategy

### Unit Tests (`tests/api/`, `tests/crud/`)
- Test individual functions
- Mock dependencies
- Fast execution

### Integration Tests (`tests/integration_scripts/`)
- Test end-to-end flows
- Real database
- Manual execution during development

### Automated Tests
- Run with `pytest`
- CI/CD integration
- Coverage reports

## Documentation Standards

### API Documentation
- Location: `documentation/<domain>/`
- Include: endpoints, schemas, examples
- Format: Markdown

### Code Documentation
- Docstrings for classes and functions
- Type hints everywhere
- Clear variable names

### README Files
- Each major directory has README
- Explains purpose and usage
- Examples included

## Migration Management

### Creating Migrations
```bash
alembic revision -m "descriptive_name"
```

### Applying Migrations
```bash
alembic upgrade head
```

### Rollback
```bash
alembic downgrade -1
```

### Best Practices
- One logical change per migration
- Test before committing
- Write reversible migrations
- Document breaking changes

## Seed Data Management

### Location
`init_seed/` directory

### Naming
`seed_<entity>.py`

### Requirements
- Idempotent (can run multiple times)
- Check if data exists
- Document dependencies

### Execution Order
1. Countries
2. States
3. Cities (if added)

## Summary

This structure provides:
- ✅ Clear separation of concerns
- ✅ Easy to navigate
- ✅ Scalable architecture
- ✅ Testable components
- ✅ Maintainable codebase
- ✅ Well-documented

Follow these patterns when adding new features to maintain consistency and quality.

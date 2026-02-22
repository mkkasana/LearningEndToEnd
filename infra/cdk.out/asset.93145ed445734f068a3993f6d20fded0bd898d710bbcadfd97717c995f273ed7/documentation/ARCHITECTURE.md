# Backend Architecture

Complete guide to the backend's clean architecture implementation.

## Overview

This backend follows **Clean Architecture** with domain-driven organization and clear separation of concerns across layers.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (Routes)                    │
│              HTTP Request/Response Handling              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Service Layer                           │
│              Business Logic & Orchestration              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│               Repository Layer                           │
│              Data Access & Persistence                   │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                  Database (PostgreSQL)                   │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
backend/app/
├── api/                          # Presentation Layer
│   ├── routes/                   # API endpoints
│   │   ├── address/             # Address domain
│   │   │   └── metadata.py      # Countries, states, etc.
│   │   ├── auth.py              # Authentication
│   │   ├── users.py             # User management
│   │   └── items.py             # Item management
│   ├── deps.py                   # FastAPI dependencies
│   └── main.py                   # API router configuration
│
├── services/                     # Business Logic Layer
│   ├── address/                 # Address domain services
│   │   ├── country_service.py
│   │   ├── state_service.py
│   │   └── ...
│   ├── auth_service.py
│   ├── user_service.py
│   └── item_service.py
│
├── repositories/                 # Data Access Layer
│   ├── address/                 # Address domain repositories
│   │   ├── country_repository.py
│   │   ├── state_repository.py
│   │   └── ...
│   ├── base.py                  # Base repository (CRUD)
│   ├── user_repository.py
│   └── item_repository.py
│
├── db_models/                    # Database Models (SQLModel)
│   ├── address/                 # Address domain models
│   │   ├── country.py
│   │   ├── state.py
│   │   └── ...
│   ├── user.py
│   └── item.py
│
├── schemas/                      # API Schemas (Pydantic)
│   ├── address/                 # Address domain schemas
│   │   ├── country.py
│   │   ├── state.py
│   │   └── ...
│   ├── auth.py
│   ├── user.py
│   ├── item.py
│   └── common.py
│
├── core/                         # Core Configuration
│   ├── config.py                # Settings
│   ├── db.py                    # Database setup
│   └── security.py              # Security utilities
│
└── utils/                        # Shared Utilities
    ├── email.py
    └── token.py
```

## Layer Responsibilities

### 1. API Layer (Routes)
**Purpose:** HTTP request/response handling

**Responsibilities:**
- Validate HTTP requests (Pydantic)
- Call service layer
- Return HTTP responses
- Handle authentication/authorization
- Map HTTP status codes

**Example:**
```python
@router.post("/countries", response_model=CountryDetailPublic)
def create_country(
    session: SessionDep,
    country_in: CountryCreate,
    current_user: CurrentUser = Depends(get_current_active_superuser)
) -> Any:
    country_service = CountryService(session)
    return country_service.create_country(country_in)
```

### 2. Service Layer
**Purpose:** Business logic and orchestration

**Responsibilities:**
- Implement business rules
- Orchestrate repository calls
- Handle transactions
- Transform data between layers
- Validate business constraints

**Example:**
```python
class CountryService:
    def __init__(self, session: Session):
        self.country_repo = CountryRepository(session)
    
    def create_country(self, country_create: CountryCreate) -> Country:
        # Business logic: check duplicates
        if self.country_repo.code_exists(country_create.code):
            raise ValueError("Country code already exists")
        
        # Create entity
        country = Country(**country_create.model_dump())
        country.code = country.code.upper()  # Business rule
        
        return self.country_repo.create(country)
```

### 3. Repository Layer
**Purpose:** Data access and persistence

**Responsibilities:**
- CRUD operations
- Database queries
- Data filtering
- No business logic

**Example:**
```python
class CountryRepository(BaseRepository[Country]):
    def get_active_countries(self) -> list[Country]:
        statement = select(Country).where(
            Country.is_active == True
        ).order_by(Country.name)
        return list(self.session.exec(statement).all())
    
    def code_exists(self, code: str) -> bool:
        statement = select(Country).where(Country.code == code.upper())
        return self.session.exec(statement).first() is not None
```

### 4. Database Models
**Purpose:** Database table definitions

**Example:**
```python
class Country(SQLModel, table=True):
    __tablename__ = "address_country"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True)
    code: str = Field(max_length=3, unique=True, index=True)
    is_active: bool = Field(default=True)
```

### 5. API Schemas
**Purpose:** API request/response contracts

**Example:**
```python
class CountryCreate(SQLModel):
    name: str = Field(max_length=255)
    code: str = Field(max_length=3)
    is_active: bool = True

class CountryPublic(SQLModel):
    countryId: uuid.UUID
    countryName: str
```

## Domain Organization

All layers are organized by domain for better cohesion:

```
address/          # Domain
├── api/routes/address/
├── services/address/
├── repositories/address/
├── db_models/address/
└── schemas/address/
```

**Benefits:**
- Easy to find related code
- Clear domain boundaries
- Simple to extract to microservices
- Better team collaboration

## Data Flow Example

```
1. HTTP Request
   POST /api/v1/metadata/address/countries
   Body: {"name": "India", "code": "IND"}
   
2. API Layer (routes/address/metadata.py)
   - Validates request with CountryCreate schema
   - Checks authentication
   - Calls service layer
   
3. Service Layer (services/address/country_service.py)
   - Checks business rules (duplicate code)
   - Transforms data (uppercase code)
   - Calls repository
   
4. Repository Layer (repositories/address/country_repository.py)
   - Executes SQL INSERT
   - Returns Country model
   
5. Service Layer
   - Returns Country to API layer
   
6. API Layer
   - Transforms to CountryDetailPublic schema
   - Returns HTTP 200 with JSON
```

## Design Patterns

### Dependency Injection
```python
# FastAPI handles DI automatically
def create_country(
    session: SessionDep,  # Injected
    country_in: CountryCreate,  # Validated
    current_user: CurrentUser = Depends(get_current_active_superuser)  # Injected
):
    service = CountryService(session)  # Manual DI
    return service.create_country(country_in)
```

### Repository Pattern
```python
class BaseRepository(Generic[T]):
    def create(self, entity: T) -> T: ...
    def get_by_id(self, id: UUID) -> T | None: ...
    def update(self, entity: T) -> T: ...
    def delete(self, entity: T) -> None: ...
```

### Service Pattern
```python
class CountryService:
    def __init__(self, session: Session):
        self.country_repo = CountryRepository(session)
    
    def create_country(self, country_create: CountryCreate) -> Country:
        # Business logic here
        pass
```

## Benefits

✅ **Separation of Concerns** - Each layer has a single responsibility
✅ **Testability** - Easy to unit test each layer independently
✅ **Maintainability** - Changes in one layer don't affect others
✅ **Scalability** - Easy to add new features/domains
✅ **Reusability** - Services and repositories can be reused
✅ **Domain-Driven** - Code organized by business domains
✅ **Type Safety** - Full type checking with Pydantic/SQLModel

## Quick Start

See [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for code templates and examples.

## Testing

- **Unit Tests:** Test each layer independently
- **Integration Tests:** Test full flow through all layers
- **E2E Tests:** Test via HTTP endpoints

See `tests/integration_scripts/` for examples.

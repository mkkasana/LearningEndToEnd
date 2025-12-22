# Backend Architecture

## Overview

This backend follows a **Clean Architecture** pattern with clear separation of concerns across multiple layers. This design promotes maintainability, testability, and scalability.

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
│   │   ├── auth.py              # Authentication routes
│   │   ├── users_new.py         # User management routes
│   │   └── items_new.py         # Item management routes
│   ├── deps.py                   # FastAPI dependencies
│   └── main.py                   # API router configuration
│
├── services/                     # Business Logic Layer
│   ├── auth_service.py          # Authentication logic
│   ├── user_service.py          # User business logic
│   └── item_service.py          # Item business logic
│
├── repositories/                 # Data Access Layer
│   ├── base.py                  # Base repository (CRUD)
│   ├── user_repository.py       # User data access
│   └── item_repository.py       # Item data access
│
├── schemas/                      # Data Transfer Objects
│   ├── auth.py                  # Auth DTOs
│   ├── user.py                  # User DTOs
│   ├── item.py                  # Item DTOs
│   └── common.py                # Shared DTOs
│
├── models/                       # Database Models
│   ├── user.py                  # User entity
│   └── item.py                  # Item entity
│
├── core/                         # Core utilities
│   ├── config.py                # Configuration
│   ├── db.py                    # Database setup
│   ├── security.py              # Security utilities
│   └── exceptions.py            # Custom exceptions
│
└── utils/                        # Shared utilities
    ├── email.py                 # Email utilities
    └── token.py                 # Token utilities
```

## Layer Responsibilities

### 1. API Layer (Routes)
**Purpose:** Handle HTTP requests and responses

**Responsibilities:**
- Receive and validate HTTP requests
- Call appropriate service methods
- Transform service responses to HTTP responses
- Handle HTTP-specific concerns (status codes, headers)
- Apply route-level dependencies (authentication, authorization)

**Rules:**
- ✅ Thin controllers - minimal logic
- ✅ Use Pydantic schemas for validation
- ✅ Inject services via dependency injection
- ❌ No direct database access
- ❌ No business logic

**Example:**
```python
@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, 
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    auth_service = AuthService(session)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise AuthenticationError("Incorrect email or password")
    
    return auth_service.create_access_token_for_user(user, expires_delta)
```

### 2. Service Layer
**Purpose:** Implement business logic and orchestrate operations

**Responsibilities:**
- Implement business rules and validation
- Orchestrate multiple repository calls
- Handle transactions
- Transform data between layers
- Coordinate complex operations

**Rules:**
- ✅ Contains all business logic
- ✅ Uses repositories for data access
- ✅ Returns domain models
- ✅ Handles business exceptions
- ❌ No HTTP concerns
- ❌ No direct SQL queries

**Example:**
```python
class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
    
    def create_user(self, user_create: UserCreate) -> User:
        # Business logic: hash password
        user = User(
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
            is_active=user_create.is_active,
        )
        return self.user_repo.create(user)
```

### 3. Repository Layer
**Purpose:** Abstract data access and persistence

**Responsibilities:**
- CRUD operations
- Query building
- Database interactions
- Data mapping
- Transaction management (at operation level)

**Rules:**
- ✅ Only database operations
- ✅ Returns domain models
- ✅ Reusable queries
- ❌ No business logic
- ❌ No validation beyond data integrity

**Example:**
```python
class UserRepository(BaseRepository[User]):
    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
    
    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None
```

### 4. Schemas (DTOs)
**Purpose:** Define data contracts for API communication

**Responsibilities:**
- Request/response validation
- Data serialization
- API documentation
- Type safety

**Example:**
```python
class UserCreate(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = None
```

### 5. Models
**Purpose:** Define database entities

**Responsibilities:**
- Database table structure
- Relationships
- Constraints
- Database-level validation

**Example:**
```python
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")
```

## Data Flow Example: User Login

```
1. Client sends POST /api/v1/login/access-token
   ↓
2. API Route (auth.py)
   - Validates request (OAuth2PasswordRequestForm)
   - Creates AuthService instance
   ↓
3. AuthService.authenticate_user()
   - Calls UserRepository.get_by_email()
   - Verifies password hash
   - Returns User or None
   ↓
4. UserRepository.get_by_email()
   - Builds SQL query
   - Executes query
   - Returns User model
   ↓
5. AuthService.create_access_token_for_user()
   - Generates JWT token
   - Returns Token schema
   ↓
6. API Route returns Token to client
```

## Benefits of This Architecture

### 1. Separation of Concerns
- Each layer has a single, well-defined responsibility
- Changes in one layer don't affect others

### 2. Testability
- Services can be tested without HTTP layer
- Repositories can be mocked for service tests
- Each layer can be tested independently

### 3. Maintainability
- Clear structure makes code easy to navigate
- Business logic is centralized in services
- Data access is centralized in repositories

### 4. Scalability
- Easy to add new features following the same pattern
- Can swap implementations (e.g., different database)
- Can add caching, logging at appropriate layers

### 5. Reusability
- Services can be used by multiple routes
- Repositories can be used by multiple services
- Common operations in base repository

## Migration Status

### ✅ Completed
- Core structure (models, schemas, repositories, services)
- Authentication flow (auth.py)
- User management (users_new.py)
- Item management (items_new.py)
- Custom exceptions
- Utility modules (email, token)

### 🔄 In Progress
- Testing new routes alongside legacy routes
- New routes available at `/api/v1/v2/*` prefix

### 📋 TODO
- Replace legacy routes with new ones
- Remove old `crud.py` and `models.py`
- Update all imports across the codebase
- Add comprehensive tests for each layer
- Add API documentation

## Usage Guidelines

### Creating a New Feature

1. **Define the Model** (`models/`)
```python
class Product(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    price: float
```

2. **Define Schemas** (`schemas/`)
```python
class ProductCreate(SQLModel):
    name: str
    price: float

class ProductPublic(SQLModel):
    id: uuid.UUID
    name: str
    price: float
```

3. **Create Repository** (`repositories/`)
```python
class ProductRepository(BaseRepository[Product]):
    def get_by_name(self, name: str) -> Product | None:
        statement = select(Product).where(Product.name == name)
        return self.session.exec(statement).first()
```

4. **Create Service** (`services/`)
```python
class ProductService:
    def __init__(self, session: Session):
        self.product_repo = ProductRepository(session)
    
    def create_product(self, product_create: ProductCreate) -> Product:
        product = Product(**product_create.model_dump())
        return self.product_repo.create(product)
```

5. **Create Routes** (`api/routes/`)
```python
@router.post("/", response_model=ProductPublic)
def create_product(session: SessionDep, product_in: ProductCreate):
    service = ProductService(session)
    return service.create_product(product_in)
```

## Best Practices

1. **Always use services in routes** - Never call repositories directly
2. **Keep routes thin** - Move logic to services
3. **Use custom exceptions** - Defined in `core/exceptions.py`
4. **Type everything** - Use type hints everywhere
5. **Follow naming conventions**:
   - Services: `*Service`
   - Repositories: `*Repository`
   - Schemas: `*Create`, `*Update`, `*Public`
6. **One service per domain** - Don't create god services
7. **Inject dependencies** - Use FastAPI's dependency injection

## Testing Strategy

```
Unit Tests:
- Services (mock repositories)
- Repositories (use test database)
- Utilities

Integration Tests:
- API routes (test full stack)
- Database operations

End-to-End Tests:
- Full user flows
```

## Common Patterns

### Pattern 1: Check Existence Before Create
```python
def create_user(self, user_create: UserCreate) -> User:
    if self.user_repo.email_exists(user_create.email):
        raise EmailAlreadyExistsError()
    return self.user_repo.create(user)
```

### Pattern 2: Permission Check
```python
def user_can_access_item(self, user: User, item: Item) -> bool:
    return user.is_superuser or item.owner_id == user.id
```

### Pattern 3: Paginated List with Count
```python
def get_items(self, skip: int, limit: int) -> tuple[list[Item], int]:
    items = self.item_repo.get_all(skip=skip, limit=limit)
    count = self.item_repo.count()
    return items, count
```

## References

- [Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)

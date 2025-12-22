# Architecture Diagram

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser/App)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP Request
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                      API LAYER (Routes)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   auth.py    │  │ users_new.py │  │ items_new.py │          │
│  │              │  │              │  │              │          │
│  │ - login      │  │ - create     │  │ - create     │          │
│  │ - test_token │  │ - read       │  │ - read       │          │
│  │ - recover    │  │ - update     │  │ - update     │          │
│  │ - reset      │  │ - delete     │  │ - delete     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                │
│  Responsibilities:                                             │
│  • Validate HTTP requests (Pydantic)                           │
│  • Call service layer                                          │
│  • Return HTTP responses                                       │
│  • Handle authentication/authorization                         │
└────────────────────────────┬───────────────────────────────────┘
                             │ Service Call
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER (Business Logic)              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ AuthService  │  │ UserService  │  │ ItemService  │          │
│  │              │  │              │  │              │          │
│  │ - auth user  │  │ - create     │  │ - create     │          │
│  │ - create     │  │ - update     │  │ - update     │          │
│  │   token      │  │ - delete     │  │ - delete     │          │
│  │ - check      │  │ - validate   │  │ - check      │          │
│  │   active     │  │   email      │  │   permission │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                │
│  Responsibilities:                                             │
│  • Implement business rules                                    │
│  • Orchestrate repository calls                                │
│  • Handle transactions                                         │
│  • Transform data between layers                               │
└────────────────────────────┬───────────────────────────────────┘
                             │ Repository Call
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                 REPOSITORY LAYER (Data Access)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │     Base     │  │    User      │  │     Item     │          │
│  │  Repository  │  │  Repository  │  │  Repository  │          │
│  │              │  │              │  │              │          │
│  │ - get_by_id  │  │ - get_by_    │  │ - get_by_    │          │
│  │ - get_all    │  │   email      │  │   owner      │          │
│  │ - create     │  │ - email_     │  │ - count_by_  │          │
│  │ - update     │  │   exists     │  │   owner      │          │
│  │ - delete     │  │ - get_active │  │ - delete_by_ │          │
│  │ - count      │  │              │  │   owner      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                │
│  Responsibilities:                                             │
│  • CRUD operations                                             │
│  • Query building (SQLModel)                                   │
│  • Database interactions                                       │
│  • Return domain models                                        │
└────────────────────────────┬───────────────────────────────────┘
                             │ SQL Query
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                       │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  user table  │  │  item table  │                            │
│  │              │  │              │                            │
│  │ - id         │  │ - id         │                            │
│  │ - email      │  │ - title      │                            │
│  │ - hashed_pwd │  │ - description│                            │
│  │ - is_active  │  │ - owner_id ──┼──┐                         │
│  │ - is_super   │  │              │  │                         │
│  │ - full_name  │  │              │  │                         │
│  └──────────────┘  └──────────────┘  │                         │
│         │                              │                       │
│         └──────────────────────────────┘                       │
│                  Relationship                                  │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow: User Login Example

```
1. POST /api/v1/login/access-token
   ├─ email: "admin@example.com"
   └─ password: "changethis"
          │
          ▼
2. auth.py (Route)
   ├─ Validate OAuth2PasswordRequestForm
   ├─ Create AuthService(session)
   └─ Call auth_service.authenticate_user()
          │
          ▼
3. AuthService (Business Logic)
   ├─ Call user_repo.get_by_email()
   ├─ Verify password hash
   ├─ Check if user is active
   └─ Call create_access_token_for_user()
          │
          ▼
4. UserRepository (Data Access)
   ├─ Build SQL: SELECT * FROM user WHERE email = ?
   ├─ Execute query
   └─ Return User model
          │
          ▼
5. PostgreSQL Database
   ├─ Execute query
   └─ Return row data
          │
          ▼
6. AuthService (Business Logic)
   ├─ Create JWT token
   └─ Return Token(access_token="eyJ...")
          │
          ▼
7. auth.py (Route)
   └─ Return HTTP 200 with Token JSON
          │
          ▼
8. CLIENT
   └─ Receive {"access_token": "eyJ...", "token_type": "bearer"}
```

## Component Interaction: Create User

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/v1/v2/users/
       │ {email, password, full_name}
       ▼
┌─────────────────────────────────────────┐
│  users_new.py (Route)                   │
│  ┌───────────────────────────────────┐  │
│  │ 1. Validate UserCreate schema     │  │
│  │ 2. Create UserService(session)    │  │
│  │ 3. Check email_exists()           │  │
│  │ 4. Call create_user()             │  │
│  │ 5. Send welcome email (optional)  │  │
│  │ 6. Return UserPublic              │  │
│  └───────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  UserService (Business Logic)           │
│  ┌───────────────────────────────────┐  │
│  │ 1. Hash password                  │  │
│  │ 2. Create User model              │  │
│  │ 3. Call user_repo.create()        │  │
│  │ 4. Return User                    │  │
│  └───────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  UserRepository (Data Access)           │
│  ┌───────────────────────────────────┐  │
│  │ 1. session.add(user)              │  │
│  │ 2. session.commit()               │  │
│  │ 3. session.refresh(user)          │  │
│  │ 4. Return User                    │  │
│  └───────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  PostgreSQL Database                    │
│  ┌───────────────────────────────────┐  │
│  │ INSERT INTO user                  │  │
│  │ VALUES (id, email, hashed_pwd...) │  │
│  │ RETURNING *                       │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## Dependency Flow

```
Routes
  ├─ Depends on: Services, Schemas, Exceptions
  └─ Does NOT depend on: Repositories, Models

Services
  ├─ Depends on: Repositories, Models, Schemas, Core utilities
  └─ Does NOT depend on: Routes

Repositories
  ├─ Depends on: Models, SQLModel
  └─ Does NOT depend on: Routes, Services, Schemas

Models
  ├─ Depends on: SQLModel
  └─ Does NOT depend on: Routes, Services, Repositories, Schemas

Schemas
  ├─ Depends on: Pydantic, SQLModel
  └─ Does NOT depend on: Routes, Services, Repositories, Models
```

## File Organization

```
backend/app/
│
├── api/                    # 🌐 HTTP Layer
│   ├── routes/
│   │   ├── auth.py        # Authentication endpoints
│   │   ├── users_new.py   # User CRUD endpoints
│   │   └── items_new.py   # Item CRUD endpoints
│   ├── deps.py            # FastAPI dependencies
│   └── main.py            # Router configuration
│
├── services/              # 💼 Business Logic Layer
│   ├── auth_service.py    # Auth business logic
│   ├── user_service.py    # User business logic
│   └── item_service.py    # Item business logic
│
├── repositories/          # 💾 Data Access Layer
│   ├── base.py           # Generic CRUD operations
│   ├── user_repository.py # User queries
│   └── item_repository.py # Item queries
│
├── schemas/               # 📋 API Contracts
│   ├── auth.py           # Token, Login DTOs
│   ├── user.py           # User DTOs
│   ├── item.py           # Item DTOs
│   └── common.py         # Shared DTOs
│
├── models/                # 🗄️ Database Entities
│   ├── user.py           # User table
│   └── item.py           # Item table
│
├── core/                  # ⚙️ Core Utilities
│   ├── config.py         # Settings
│   ├── db.py             # Database setup
│   ├── security.py       # Password, JWT
│   └── exceptions.py     # Custom exceptions
│
└── utils/                 # 🔧 Shared Utilities
    ├── email.py          # Email sending
    └── token.py          # Token generation
```

## Request/Response Flow with Types

```python
# 1. Client Request
POST /api/v1/login/access-token
Content-Type: application/x-www-form-urlencoded
username=admin@example.com&password=changethis

# 2. Route receives OAuth2PasswordRequestForm
@router.post("/login/access-token")
def login_access_token(
    session: SessionDep,                    # Injected
    form_data: OAuth2PasswordRequestForm    # Validated
) -> Token:                                 # Return type

# 3. Service receives primitives, returns Model
class AuthService:
    def authenticate_user(
        self, 
        email: str,           # Primitive
        password: str         # Primitive
    ) -> User | None:         # Domain Model

# 4. Repository receives/returns Models
class UserRepository:
    def get_by_email(
        self, 
        email: str            # Primitive
    ) -> User | None:         # Domain Model

# 5. Database returns raw data
SELECT * FROM user WHERE email = 'admin@example.com'
→ Returns row data

# 6. Repository converts to Model
→ User(id=uuid, email="admin@...", ...)

# 7. Service creates Token
→ Token(access_token="eyJ...", token_type="bearer")

# 8. Route returns JSON
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Error Handling Flow

```
Route
  │
  ├─ Validation Error (Pydantic)
  │  └─ HTTP 422 Unprocessable Entity
  │
  ├─ Custom Exception (from Service)
  │  ├─ AuthenticationError → HTTP 401
  │  ├─ PermissionDeniedError → HTTP 403
  │  ├─ ResourceNotFoundError → HTTP 404
  │  └─ EmailAlreadyExistsError → HTTP 409
  │
  └─ Unexpected Error
     └─ HTTP 500 Internal Server Error
```

## Testing Layers

```
┌─────────────────────────────────────────┐
│  E2E Tests (Full Stack)                 │
│  • Test via HTTP endpoints              │
│  • Use TestClient                       │
│  • Test complete user flows             │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Integration Tests (Service + Repo)     │
│  • Test service with real database      │
│  • Test repository queries              │
│  • Use test database                    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Unit Tests (Service only)              │
│  • Mock repositories                    │
│  • Test business logic                  │
│  • Fast execution                       │
└─────────────────────────────────────────┘
```

## Summary

This architecture provides:
- ✅ Clear separation of concerns
- ✅ Easy to test each layer
- ✅ Maintainable and scalable
- ✅ Type-safe throughout
- ✅ Follows SOLID principles
- ✅ Industry best practices

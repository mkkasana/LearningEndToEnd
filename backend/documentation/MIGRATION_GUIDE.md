# Migration Guide: Legacy to Clean Architecture

## Overview

This guide explains how the codebase has been refactored from a flat structure to a clean architecture with proper separation of concerns.

## What Changed?

### Before (Legacy Structure)
```
backend/app/
├── api/
│   └── routes/
│       ├── login.py      # Mixed: routes + business logic
│       ├── users.py      # Mixed: routes + DB queries
│       └── items.py      # Mixed: routes + DB queries
├── crud.py               # Flat CRUD operations
├── models.py             # Mixed: DB models + schemas
└── utils.py              # Mixed utilities
```

### After (Clean Architecture)
```
backend/app/
├── api/routes/           # Pure HTTP handling
├── services/             # Business logic
├── repositories/         # Data access
├── schemas/              # API contracts
├── models/               # DB entities
├── core/                 # Core utilities
└── utils/                # Shared utilities
```

## Import Changes

### Old Imports
```python
# Legacy imports
from app.models import User, UserCreate, UserPublic, Token
from app import crud

# Usage
user = crud.get_user_by_email(session, email)
user = crud.create_user(session, user_create)
```

### New Imports
```python
# New imports - Models
from app.models.user import User
from app.models.item import Item

# New imports - Schemas
from app.schemas.user import UserCreate, UserPublic
from app.schemas.auth import Token

# New imports - Services
from app.services.user_service import UserService
from app.services.auth_service import AuthService

# Usage
user_service = UserService(session)
user = user_service.get_user_by_email(email)
user = user_service.create_user(user_create)
```

## Code Migration Examples

### Example 1: Authentication

#### Before (login.py)
```python
@router.post("/login/access-token")
def login_access_token(session: SessionDep, form_data: OAuth2PasswordRequestForm) -> Token:
    user = crud.authenticate(
        session=session, 
        email=form_data.username, 
        password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )
```

#### After (auth.py)
```python
@router.post("/login/access-token")
def login_access_token(session: SessionDep, form_data: OAuth2PasswordRequestForm) -> Token:
    auth_service = AuthService(session)
    
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise AuthenticationError("Incorrect email or password")
    
    if not auth_service.is_user_active(user):
        raise InactiveUserError()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return auth_service.create_access_token_for_user(user, access_token_expires)
```

**Benefits:**
- Business logic moved to `AuthService`
- Custom exceptions for better error handling
- Clearer separation of concerns
- Easier to test

### Example 2: User Creation

#### Before (users.py)
```python
@router.post("/", response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user = crud.create_user(session=session, user_create=user_in)
    
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(...)
        send_email(...)
    
    return user
```

#### After (users_new.py)
```python
@router.post("/", response_model=UserPublic)
def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
    user_service = UserService(session)
    
    if user_service.email_exists(user_in.email):
        raise EmailAlreadyExistsError()
    
    user = user_service.create_user(user_in)
    
    if settings.emails_enabled and user_in.email:
        email_data = generate_new_account_email(...)
        send_email(...)
    
    return user
```

**Benefits:**
- Route is thinner and more readable
- Email checking logic in service
- Custom exception for email conflicts
- Service handles password hashing

### Example 3: Item Access Control

#### Before (items.py)
```python
@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    item = session.get(Item, id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return item
```

#### After (items_new.py)
```python
@router.get("/{id}", response_model=ItemPublic)
def read_item(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    item_service = ItemService(session)
    item = item_service.get_item_by_id(id)
    
    if not item:
        raise ResourceNotFoundError("Item")
    
    if not item_service.user_can_access_item(current_user, item):
        raise PermissionDeniedError()
    
    return item
```

**Benefits:**
- Permission logic in service (reusable)
- No direct database access in route
- Semantic custom exceptions
- Business rule centralized

## Service Layer Patterns

### Pattern 1: Simple CRUD
```python
class UserService:
    def __init__(self, session: Session):
        self.user_repo = UserRepository(session)
    
    def get_user_by_id(self, user_id: UUID) -> User | None:
        return self.user_repo.get_by_id(user_id)
```

### Pattern 2: Business Logic
```python
class UserService:
    def create_user(self, user_create: UserCreate) -> User:
        # Business logic: hash password
        user = User(
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
            is_active=user_create.is_active,
        )
        return self.user_repo.create(user)
```

### Pattern 3: Orchestration
```python
class UserService:
    def delete_user_with_items(self, user_id: UUID) -> None:
        # Orchestrate multiple operations
        item_service = ItemService(self.session)
        item_service.delete_items_by_owner(user_id)
        
        user = self.user_repo.get_by_id(user_id)
        self.user_repo.delete(user)
```

## Repository Layer Patterns

### Pattern 1: Basic Query
```python
class UserRepository(BaseRepository[User]):
    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
```

### Pattern 2: Complex Query
```python
class ItemRepository(BaseRepository[Item]):
    def get_by_owner(self, owner_id: UUID, skip: int = 0, limit: int = 100) -> list[Item]:
        statement = (
            select(Item)
            .where(Item.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.exec(statement).all())
```

### Pattern 3: Aggregation
```python
class ItemRepository(BaseRepository[Item]):
    def count_by_owner(self, owner_id: UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Item)
            .where(Item.owner_id == owner_id)
        )
        return self.session.exec(statement).one()
```

## Exception Handling

### Before
```python
if not user:
    raise HTTPException(status_code=404, detail="User not found")
if not user.is_active:
    raise HTTPException(status_code=400, detail="Inactive user")
```

### After
```python
from app.core.exceptions import (
    ResourceNotFoundError,
    InactiveUserError,
    PermissionDeniedError,
    EmailAlreadyExistsError,
)

if not user:
    raise ResourceNotFoundError("User")
if not user.is_active:
    raise InactiveUserError()
```

**Benefits:**
- Semantic exception names
- Consistent status codes
- Reusable across routes
- Better error messages

## Testing Changes

### Before
```python
def test_create_user():
    # Had to test through HTTP endpoint
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 200
```

### After
```python
def test_user_service_create():
    # Can test service directly
    user_service = UserService(session)
    user = user_service.create_user(user_create)
    assert user.email == user_create.email

def test_user_repository_get_by_email():
    # Can test repository directly
    user_repo = UserRepository(session)
    user = user_repo.get_by_email("test@example.com")
    assert user is not None
```

**Benefits:**
- Faster tests (no HTTP overhead)
- Test each layer independently
- Mock dependencies easily
- Better test coverage

## Backward Compatibility

### Current State
- ✅ Old routes still work (`/api/v1/users/`, `/api/v1/items/`)
- ✅ New routes available (`/api/v1/v2/users/`, `/api/v1/v2/items/`)
- ✅ Old `models.py` imports from new structure
- ✅ Old `crud.py` still available

### Migration Path
1. **Phase 1** ✅ - New structure created
2. **Phase 2** ✅ - New routes created with `/v2` prefix
3. **Phase 3** 🔄 - Test new routes
4. **Phase 4** 📋 - Replace old routes
5. **Phase 5** 📋 - Remove legacy files

## How to Use New Structure

### For New Features
Always use the new structure:
1. Create model in `models/`
2. Create schemas in `schemas/`
3. Create repository in `repositories/`
4. Create service in `services/`
5. Create routes in `api/routes/`

### For Existing Features
Two options:
1. **Keep using old routes** - They still work
2. **Migrate to new routes** - Use `/v2` prefix for now

## Common Migration Tasks

### Task 1: Add New Endpoint
```python
# 1. Define schema (if needed)
class ProductCreate(SQLModel):
    name: str
    price: float

# 2. Add service method
class ProductService:
    def create_product(self, product_create: ProductCreate) -> Product:
        product = Product(**product_create.model_dump())
        return self.product_repo.create(product)

# 3. Add route
@router.post("/products/", response_model=ProductPublic)
def create_product(session: SessionDep, product_in: ProductCreate):
    service = ProductService(session)
    return service.create_product(product_in)
```

### Task 2: Add Business Logic
```python
# Add to service, not route
class UserService:
    def can_delete_user(self, user: User, current_user: User) -> bool:
        # Business rule: can't delete yourself if superuser
        if user == current_user and current_user.is_superuser:
            return False
        return True
```

### Task 3: Add Complex Query
```python
# Add to repository
class UserRepository:
    def get_active_superusers(self) -> list[User]:
        statement = select(User).where(
            User.is_active == True,
            User.is_superuser == True
        )
        return list(self.session.exec(statement).all())
```

## Troubleshooting

### Import Errors
**Problem:** `ImportError: cannot import name 'User' from 'app.models'`

**Solution:** Update imports
```python
# Old
from app.models import User

# New
from app.models.user import User
# OR use the compatibility layer
from app.models import User  # Still works via __init__.py
```

### Circular Imports
**Problem:** Circular dependency between services

**Solution:** Import inside methods or use forward references
```python
def delete_user_with_items(self, user_id: UUID):
    from app.services.item_service import ItemService
    item_service = ItemService(self.session)
    # ...
```

## Questions?

- Check `ARCHITECTURE.md` for detailed architecture documentation
- Look at existing examples in `api/routes/auth.py`, `users_new.py`, `items_new.py`
- Review service implementations in `services/`
- Check repository patterns in `repositories/`

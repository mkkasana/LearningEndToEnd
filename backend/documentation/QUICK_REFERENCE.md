# Quick Reference Guide

## 🚀 Quick Start

### Adding a New Feature (5 Steps)

```python
# 1. Create Model (models/product.py)
class Product(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    price: float

# 2. Create Schemas (schemas/product.py)
class ProductCreate(SQLModel):
    name: str
    price: float

class ProductPublic(SQLModel):
    id: UUID
    name: str
    price: float

# 3. Create Repository (repositories/product_repository.py)
class ProductRepository(BaseRepository[Product]):
    def get_by_name(self, name: str) -> Product | None:
        statement = select(Product).where(Product.name == name)
        return self.session.exec(statement).first()

# 4. Create Service (services/product_service.py)
class ProductService:
    def __init__(self, session: Session):
        self.product_repo = ProductRepository(session)
    
    def create_product(self, product_create: ProductCreate) -> Product:
        product = Product(**product_create.model_dump())
        return self.product_repo.create(product)

# 5. Create Route (api/routes/products.py)
@router.post("/", response_model=ProductPublic)
def create_product(session: SessionDep, product_in: ProductCreate):
    service = ProductService(session)
    return service.create_product(product_in)
```

## 📁 File Templates

### Model Template
```python
# models/entity_name.py
import uuid
from sqlmodel import Field, Relationship, SQLModel

class EntityName(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # Add fields here
    
    # Add relationships here
    # related: list["Related"] = Relationship(back_populates="entity")
```

### Schema Template
```python
# schemas/entity_name.py
import uuid
from sqlmodel import SQLModel
from pydantic import Field

class EntityBase(SQLModel):
    """Shared properties"""
    field1: str
    field2: int | None = None

class EntityCreate(EntityBase):
    """Properties for creation"""
    pass

class EntityUpdate(EntityBase):
    """Properties for update (all optional)"""
    field1: str | None = None

class EntityPublic(EntityBase):
    """Properties to return via API"""
    id: uuid.UUID

class EntitiesPublic(SQLModel):
    """List response"""
    data: list[EntityPublic]
    count: int
```

### Repository Template
```python
# repositories/entity_repository.py
from sqlmodel import Session, select
from app.models.entity_name import EntityName
from app.repositories.base import BaseRepository

class EntityRepository(BaseRepository[EntityName]):
    def __init__(self, session: Session):
        super().__init__(EntityName, session)
    
    # Add custom queries here
    def get_by_field(self, field_value: str) -> EntityName | None:
        statement = select(EntityName).where(EntityName.field == field_value)
        return self.session.exec(statement).first()
```

### Service Template
```python
# services/entity_service.py
from uuid import UUID
from sqlmodel import Session
from app.models.entity_name import EntityName
from app.repositories.entity_repository import EntityRepository
from app.schemas.entity_name import EntityCreate, EntityUpdate

class EntityService:
    """Service for entity business logic"""
    
    def __init__(self, session: Session):
        self.session = session
        self.entity_repo = EntityRepository(session)
    
    def get_by_id(self, entity_id: UUID) -> EntityName | None:
        return self.entity_repo.get_by_id(entity_id)
    
    def get_all(self, skip: int = 0, limit: int = 100) -> tuple[list[EntityName], int]:
        entities = self.entity_repo.get_all(skip=skip, limit=limit)
        count = self.entity_repo.count()
        return entities, count
    
    def create(self, entity_create: EntityCreate) -> EntityName:
        entity = EntityName(**entity_create.model_dump())
        return self.entity_repo.create(entity)
    
    def update(self, entity: EntityName, entity_update: EntityUpdate) -> EntityName:
        update_data = entity_update.model_dump(exclude_unset=True)
        entity.sqlmodel_update(update_data)
        return self.entity_repo.update(entity)
    
    def delete(self, entity: EntityName) -> None:
        self.entity_repo.delete(entity)
```

### Route Template
```python
# api/routes/entities.py
import uuid
from typing import Any
from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep
from app.core.exceptions import ResourceNotFoundError
from app.schemas.common import Message
from app.schemas.entity_name import EntityCreate, EntityPublic, EntitiesPublic, EntityUpdate
from app.services.entity_service import EntityService

router = APIRouter(prefix="/entities", tags=["entities"])

@router.get("/", response_model=EntitiesPublic)
def read_entities(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """Retrieve entities"""
    service = EntityService(session)
    entities, count = service.get_all(skip=skip, limit=limit)
    return EntitiesPublic(data=entities, count=count)

@router.get("/{id}", response_model=EntityPublic)
def read_entity(session: SessionDep, id: uuid.UUID) -> Any:
    """Get entity by ID"""
    service = EntityService(session)
    entity = service.get_by_id(id)
    if not entity:
        raise ResourceNotFoundError("Entity")
    return entity

@router.post("/", response_model=EntityPublic)
def create_entity(session: SessionDep, entity_in: EntityCreate) -> Any:
    """Create new entity"""
    service = EntityService(session)
    return service.create(entity_in)

@router.put("/{id}", response_model=EntityPublic)
def update_entity(session: SessionDep, id: uuid.UUID, entity_in: EntityUpdate) -> Any:
    """Update an entity"""
    service = EntityService(session)
    entity = service.get_by_id(id)
    if not entity:
        raise ResourceNotFoundError("Entity")
    return service.update(entity, entity_in)

@router.delete("/{id}")
def delete_entity(session: SessionDep, id: uuid.UUID) -> Message:
    """Delete an entity"""
    service = EntityService(session)
    entity = service.get_by_id(id)
    if not entity:
        raise ResourceNotFoundError("Entity")
    service.delete(entity)
    return Message(message="Entity deleted successfully")
```

## 🎯 Common Patterns

### Pattern: Check Existence
```python
# In Service
def create_user(self, user_create: UserCreate) -> User:
    if self.user_repo.email_exists(user_create.email):
        raise EmailAlreadyExistsError()
    return self.user_repo.create(user)
```

### Pattern: Permission Check
```python
# In Service
def user_can_access(self, user: User, resource: Resource) -> bool:
    return user.is_superuser or resource.owner_id == user.id

# In Route
if not service.user_can_access(current_user, item):
    raise PermissionDeniedError()
```

### Pattern: Paginated List
```python
# In Repository
def get_all(self, skip: int = 0, limit: int = 100) -> list[Model]:
    statement = select(Model).offset(skip).limit(limit)
    return list(self.session.exec(statement).all())

def count(self) -> int:
    statement = select(func.count()).select_from(Model)
    return self.session.exec(statement).one()

# In Service
def get_items(self, skip: int, limit: int) -> tuple[list[Item], int]:
    items = self.item_repo.get_all(skip=skip, limit=limit)
    count = self.item_repo.count()
    return items, count

# In Route
@router.get("/", response_model=ItemsPublic)
def read_items(session: SessionDep, skip: int = 0, limit: int = 100):
    service = ItemService(session)
    items, count = service.get_items(skip=skip, limit=limit)
    return ItemsPublic(data=items, count=count)
```

### Pattern: Filtered Query
```python
# In Repository
def get_by_owner(self, owner_id: UUID) -> list[Item]:
    statement = select(Item).where(Item.owner_id == owner_id)
    return list(self.session.exec(statement).all())

# In Service
def get_user_items(self, user: User) -> list[Item]:
    if user.is_superuser:
        return self.item_repo.get_all()
    return self.item_repo.get_by_owner(user.id)
```

### Pattern: Cascade Delete
```python
# In Service
def delete_user_with_items(self, user_id: UUID) -> None:
    # Delete related items first
    item_service = ItemService(self.session)
    item_service.delete_items_by_owner(user_id)
    
    # Then delete user
    user = self.user_repo.get_by_id(user_id)
    self.user_repo.delete(user)
```

### Pattern: Update with Validation
```python
# In Service
def update_user(self, user: User, user_update: UserUpdate) -> User:
    # Validate email uniqueness if changing
    if user_update.email and user_update.email != user.email:
        if self.user_repo.email_exists(user_update.email):
            raise EmailAlreadyExistsError()
    
    # Handle password separately
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        password = update_data.pop("password")
        update_data["hashed_password"] = get_password_hash(password)
    
    user.sqlmodel_update(update_data)
    return self.user_repo.update(user)
```

## 🔧 Common Operations

### Get Single Record
```python
# Repository
def get_by_id(self, id: UUID) -> Model | None:
    return self.session.get(Model, id)

# Service
def get_by_id(self, id: UUID) -> Model | None:
    return self.repo.get_by_id(id)

# Route
entity = service.get_by_id(id)
if not entity:
    raise ResourceNotFoundError("Entity")
```

### Create Record
```python
# Repository
def create(self, obj: Model) -> Model:
    self.session.add(obj)
    self.session.commit()
    self.session.refresh(obj)
    return obj

# Service
def create(self, create_schema: CreateSchema) -> Model:
    obj = Model(**create_schema.model_dump())
    return self.repo.create(obj)

# Route
return service.create(create_schema)
```

### Update Record
```python
# Repository
def update(self, obj: Model) -> Model:
    self.session.add(obj)
    self.session.commit()
    self.session.refresh(obj)
    return obj

# Service
def update(self, obj: Model, update_schema: UpdateSchema) -> Model:
    update_data = update_schema.model_dump(exclude_unset=True)
    obj.sqlmodel_update(update_data)
    return self.repo.update(obj)

# Route
entity = service.get_by_id(id)
if not entity:
    raise ResourceNotFoundError("Entity")
return service.update(entity, update_schema)
```

### Delete Record
```python
# Repository
def delete(self, obj: Model) -> None:
    self.session.delete(obj)
    self.session.commit()

# Service
def delete(self, obj: Model) -> None:
    self.repo.delete(obj)

# Route
entity = service.get_by_id(id)
if not entity:
    raise ResourceNotFoundError("Entity")
service.delete(entity)
return Message(message="Entity deleted successfully")
```

## 🚨 Exception Usage

```python
from app.core.exceptions import (
    AuthenticationError,        # 401 - Invalid credentials
    InactiveUserError,          # 400 - User account inactive
    PermissionDeniedError,      # 403 - Insufficient permissions
    ResourceNotFoundError,      # 404 - Resource not found
    EmailAlreadyExistsError,    # 409 - Email conflict
)

# Usage examples
if not user:
    raise ResourceNotFoundError("User")

if not service.user_can_access(current_user, item):
    raise PermissionDeniedError()

if service.email_exists(email):
    raise EmailAlreadyExistsError()

if not user.is_active:
    raise InactiveUserError()

if not authenticated:
    raise AuthenticationError("Invalid credentials")
```

## 📝 Import Cheatsheet

```python
# Models
from app.models.user import User
from app.models.item import Item

# Schemas
from app.schemas.user import UserCreate, UserUpdate, UserPublic
from app.schemas.item import ItemCreate, ItemUpdate, ItemPublic
from app.schemas.auth import Token, TokenPayload
from app.schemas.common import Message

# Services
from app.services.user_service import UserService
from app.services.item_service import ItemService
from app.services.auth_service import AuthService

# Repositories
from app.repositories.user_repository import UserRepository
from app.repositories.item_repository import ItemRepository

# Dependencies
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser

# Exceptions
from app.core.exceptions import (
    AuthenticationError,
    InactiveUserError,
    PermissionDeniedError,
    ResourceNotFoundError,
    EmailAlreadyExistsError,
)

# Utilities
from app.utils import send_email, generate_password_reset_token
from app.core.security import get_password_hash, verify_password
```

## 🧪 Testing Examples

### Unit Test (Service)
```python
def test_user_service_create(session):
    user_service = UserService(session)
    user_create = UserCreate(
        email="test@example.com",
        password="password123",
        full_name="Test User"
    )
    user = user_service.create_user(user_create)
    
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.hashed_password != "password123"  # Should be hashed
```

### Unit Test (Repository)
```python
def test_user_repository_get_by_email(session):
    user_repo = UserRepository(session)
    
    # Create test user
    user = User(email="test@example.com", hashed_password="hashed")
    user_repo.create(user)
    
    # Test retrieval
    found_user = user_repo.get_by_email("test@example.com")
    assert found_user is not None
    assert found_user.email == "test@example.com"
```

### Integration Test (Route)
```python
def test_create_user_endpoint(client, superuser_token_headers):
    data = {
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
    response = client.post(
        "/api/v1/users/",
        headers=superuser_token_headers,
        json=data
    )
    assert response.status_code == 200
    content = response.json()
    assert content["email"] == "test@example.com"
```

## 💡 Best Practices

### ✅ DO
- Keep routes thin - only HTTP concerns
- Put business logic in services
- Use repositories for all database access
- Use custom exceptions for errors
- Type hint everything
- Use dependency injection
- Return domain models from services
- Validate at the route level (Pydantic)

### ❌ DON'T
- Put business logic in routes
- Access database directly from routes
- Use generic HTTPException everywhere
- Skip type hints
- Create god services (too many responsibilities)
- Mix concerns between layers
- Return schemas from repositories
- Validate in multiple places

## 🔍 Debugging Tips

### Check Layer by Layer
```python
# 1. Test Repository
user_repo = UserRepository(session)
user = user_repo.get_by_email("test@example.com")
print(user)  # Should return User or None

# 2. Test Service
user_service = UserService(session)
user = user_service.get_user_by_email("test@example.com")
print(user)  # Should return User or None

# 3. Test Route
response = client.get("/api/v1/users/me")
print(response.json())  # Should return user data
```

### Common Issues

**Import Error:**
```python
# Wrong
from app.models import User  # Old way

# Right
from app.models.user import User  # New way
# OR
from app.models import User  # Works via __init__.py
```

**Circular Import:**
```python
# Solution: Import inside function
def delete_user_with_items(self, user_id: UUID):
    from app.services.item_service import ItemService
    item_service = ItemService(self.session)
    # ...
```

## 📚 Further Reading

- `ARCHITECTURE.md` - Complete architecture documentation
- `MIGRATION_GUIDE.md` - Migration from old to new structure
- `ARCHITECTURE_DIAGRAM.md` - Visual diagrams
- `REFACTORING_SUMMARY.md` - What was changed and why

# Backend Project Guide

Quick reference for common development tasks.

## Project Structure

```
backend/app/
├── api/routes/          # HTTP endpoints (by domain)
├── services/            # Business logic (by domain)
├── repositories/        # Data access (by domain)
├── db_models/           # Database models (by domain)
├── schemas/             # API contracts (by domain)
├── core/                # Configuration & setup
└── utils/               # Shared utilities
```

## Adding a New Feature

### 1. Create Database Model

```python
# app/db_models/product.py
from sqlmodel import Field, SQLModel
import uuid

class Product(SQLModel, table=True):
    __tablename__ = "product"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    price: float
    is_active: bool = Field(default=True)
```

### 2. Create Migration

```bash
alembic revision --autogenerate -m "add_product_table"
alembic upgrade head
```

### 3. Create Schemas

```python
# app/schemas/product.py
from sqlmodel import SQLModel
import uuid

class ProductCreate(SQLModel):
    name: str
    price: float

class ProductUpdate(SQLModel):
    name: str | None = None
    price: float | None = None
    is_active: bool | None = None

class ProductPublic(SQLModel):
    productId: uuid.UUID
    productName: str
    price: float

class ProductDetailPublic(SQLModel):
    id: uuid.UUID
    name: str
    price: float
    is_active: bool
```

### 4. Create Repository

```python
# app/repositories/product_repository.py
from app.repositories.base import BaseRepository
from app.db_models.product import Product
from sqlmodel import select

class ProductRepository(BaseRepository[Product]):
    def get_active_products(self) -> list[Product]:
        statement = select(Product).where(
            Product.is_active == True
        ).order_by(Product.name)
        return list(self.session.exec(statement).all())
    
    def get_by_name(self, name: str) -> Product | None:
        statement = select(Product).where(Product.name == name)
        return self.session.exec(statement).first()
```

### 5. Create Service

```python
# app/services/product_service.py
from sqlmodel import Session
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate, ProductPublic
from app.db_models.product import Product

class ProductService:
    def __init__(self, session: Session):
        self.product_repo = ProductRepository(session)
    
    def get_products(self) -> list[ProductPublic]:
        products = self.product_repo.get_active_products()
        return [
            ProductPublic(
                productId=p.id,
                productName=p.name,
                price=p.price
            )
            for p in products
        ]
    
    def create_product(self, product_create: ProductCreate) -> Product:
        # Check if product exists
        if self.product_repo.get_by_name(product_create.name):
            raise ValueError("Product already exists")
        
        product = Product(**product_create.model_dump())
        return self.product_repo.create(product)
    
    def update_product(self, product: Product, product_update: ProductUpdate) -> Product:
        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)
        return self.product_repo.update(product)
    
    def delete_product(self, product: Product) -> None:
        self.product_repo.delete(product)
```

### 6. Create Routes

```python
# app/api/routes/products.py
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import SessionDep, get_current_active_superuser
from app.services.product_service import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, ProductPublic, ProductDetailPublic
import uuid

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
def get_products(session: SessionDep) -> Any:
    """Get all active products (public)."""
    service = ProductService(session)
    return service.get_products()

@router.get("/{product_id}", response_model=ProductDetailPublic)
def get_product(session: SessionDep, product_id: uuid.UUID) -> Any:
    """Get product by ID (public)."""
    service = ProductService(session)
    product = service.product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.post("/", response_model=ProductDetailPublic, dependencies=[Depends(get_current_active_superuser)])
def create_product(session: SessionDep, product_in: ProductCreate) -> Any:
    """Create product (admin only)."""
    service = ProductService(session)
    try:
        return service.create_product(product_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{product_id}", response_model=ProductDetailPublic, dependencies=[Depends(get_current_active_superuser)])
def update_product(session: SessionDep, product_id: uuid.UUID, product_in: ProductUpdate) -> Any:
    """Update product (admin only)."""
    service = ProductService(session)
    product = service.product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return service.update_product(product, product_in)

@router.delete("/{product_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_product(session: SessionDep, product_id: uuid.UUID) -> Any:
    """Delete product (admin only)."""
    service = ProductService(session)
    product = service.product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    service.delete_product(product)
    return {"message": "Product deleted successfully"}
```

### 7. Register Router

```python
# app/api/main.py
from app.api.routes import products

api_router.include_router(products.router)
```

## Common Tasks

### Run Migrations
```bash
cd backend
alembic upgrade head
```

### Create Migration
```bash
alembic revision --autogenerate -m "description"
```

### Run Tests
```bash
pytest
```

### Run Integration Tests
```bash
python3 tests/integration_scripts/test_address_full_integration.py
```

### Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

### Access API Docs
```
http://localhost:8000/docs
```

## Domain Organization

When adding a new domain (e.g., `payment`):

```
app/
├── api/routes/payment/
│   └── __init__.py
├── services/payment/
│   └── __init__.py
├── repositories/payment/
│   └── __init__.py
├── db_models/payment/
│   └── __init__.py
└── schemas/payment/
    └── __init__.py
```

## Best Practices

✅ **Keep layers separate** - Don't skip layers
✅ **Use type hints** - Full type safety
✅ **Validate in schemas** - Use Pydantic validation
✅ **Business logic in services** - Not in routes or repositories
✅ **Test each layer** - Unit and integration tests
✅ **Document APIs** - Use docstrings for Swagger
✅ **Handle errors** - Use appropriate HTTP status codes
✅ **Use dependencies** - Leverage FastAPI's DI system

## Security

- **Public endpoints:** No authentication
- **Protected endpoints:** Use `Depends(get_current_active_superuser)`
- **Passwords:** Always hash with bcrypt
- **Tokens:** JWT with expiration
- **Validation:** Always validate input with Pydantic

## More Information

- **Architecture:** See [ARCHITECTURE.md](./ARCHITECTURE.md)
- **Quick Reference:** See [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- **Address API:** See [address/README.md](./address/README.md)

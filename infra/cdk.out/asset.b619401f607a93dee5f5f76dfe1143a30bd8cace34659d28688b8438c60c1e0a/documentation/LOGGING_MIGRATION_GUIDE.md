# Logging Migration Guide

Step-by-step guide to add logging to existing backend code.

## Overview

This guide helps you add comprehensive logging to existing routes and services that don't have logging yet.

## Quick Checklist

For each file you're updating:

- [ ] Add logger import
- [ ] Add `@log_route` decorator to routes (if applicable)
- [ ] Add logging to service methods
- [ ] Log at decision points
- [ ] Include relevant context (IDs, names, etc.)
- [ ] Test the logs

## Step 1: Identify Files to Update

### Routes Without Logging

Check these route files:
```bash
# Find route files without log_route import
grep -L "log_route" backend/app/api/routes/*.py
grep -L "log_route" backend/app/api/routes/**/*.py
```

### Services Without Logging

Check these service files:
```bash
# Find service files without logging import
grep -L "import logging" backend/app/services/*.py
grep -L "import logging" backend/app/services/**/*.py
```

## Step 2: Update Route Files

### Before (No Logging)

```python
from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep
from app.schemas.item import ItemCreate, ItemPublic

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemPublic)
def create_item(
    session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
):
    """Create new item."""
    item_service = ItemService(session)
    item = item_service.create_item(item_in, current_user.id)
    return item
```

### After (With Logging)

```python
from fastapi import APIRouter
from app.api.deps import CurrentUser, SessionDep
from app.schemas.item import ItemCreate, ItemPublic
from app.utils.logging_decorator import log_route  # ADD THIS

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemPublic)
@log_route  # ADD THIS
def create_item(
    session: SessionDep, current_user: CurrentUser, item_in: ItemCreate
):
    """Create new item."""
    item_service = ItemService(session)
    item = item_service.create_item(item_in, current_user.id)
    return item
```

### Changes Made

1. Import the decorator: `from app.utils.logging_decorator import log_route`
2. Add decorator above function: `@log_route`

That's it! The decorator handles all request/response logging automatically.

## Step 3: Update Service Files

### Before (No Logging)

```python
from uuid import UUID
from sqlmodel import Session
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    def __init__(self, session: Session):
        self.session = session
        self.item_repo = ItemRepository(session)

    def create_item(self, item_create: ItemCreate, owner_id: UUID):
        """Create a new item."""
        item = Item(**item_create.model_dump(), owner_id=owner_id)
        return self.item_repo.create(item)

    def get_item_by_id(self, item_id: UUID):
        """Get item by ID."""
        return self.item_repo.get_by_id(item_id)

    def update_item(self, item, item_update: ItemUpdate):
        """Update an item."""
        update_data = item_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        return self.item_repo.update(item)

    def delete_item(self, item):
        """Delete an item."""
        self.item_repo.delete(item)
```

### After (With Logging)

```python
import logging  # ADD THIS
from uuid import UUID
from sqlmodel import Session
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate

logger = logging.getLogger(__name__)  # ADD THIS


class ItemService:
    def __init__(self, session: Session):
        self.session = session
        self.item_repo = ItemRepository(session)

    def create_item(self, item_create: ItemCreate, owner_id: UUID):
        """Create a new item."""
        logger.info(f"Creating item: {item_create.title}, owner_id={owner_id}")  # ADD THIS
        
        item = Item(**item_create.model_dump(), owner_id=owner_id)
        created_item = self.item_repo.create(item)
        
        logger.info(  # ADD THIS
            f"Item created successfully: {created_item.title} "
            f"(ID: {created_item.id})"
        )
        return created_item

    def get_item_by_id(self, item_id: UUID):
        """Get item by ID."""
        logger.debug(f"Fetching item by ID: {item_id}")  # ADD THIS
        
        item = self.item_repo.get_by_id(item_id)
        
        if item:  # ADD THIS
            logger.debug(f"Item found: {item.title} (ID: {item_id})")
        else:
            logger.debug(f"Item not found: ID {item_id}")
        
        return item

    def update_item(self, item, item_update: ItemUpdate):
        """Update an item."""
        logger.info(f"Updating item: {item.title} (ID: {item.id})")  # ADD THIS
        
        update_data = item_update.model_dump(exclude_unset=True)
        
        # Log what fields are being updated  # ADD THIS
        update_fields = list(update_data.keys())
        if update_fields:
            logger.debug(f"Updating fields for item {item.id}: {update_fields}")
        
        for key, value in update_data.items():
            setattr(item, key, value)
        
        updated_item = self.item_repo.update(item)
        
        logger.info(  # ADD THIS
            f"Item updated successfully: {updated_item.title} "
            f"(ID: {updated_item.id})"
        )
        return updated_item

    def delete_item(self, item):
        """Delete an item."""
        logger.warning(f"Deleting item: {item.title} (ID: {item.id})")  # ADD THIS
        
        self.item_repo.delete(item)
        
        logger.info(  # ADD THIS
            f"Item deleted successfully: {item.title} (ID: {item.id})"
        )
```

### Changes Made

1. Import logging: `import logging`
2. Create logger: `logger = logging.getLogger(__name__)`
3. Add logging at key points:
   - Operation start (INFO level)
   - Decision points (DEBUG/WARNING level)
   - Operation completion (INFO level)
   - Errors (ERROR level with `exc_info=True`)

## Step 4: Add Logging to Decision Points

### Before

```python
def create_item(self, item_create: ItemCreate, owner_id: UUID):
    if self.title_exists(item_create.title):
        raise ValueError("Title already exists")
    
    item = Item(**item_create.model_dump(), owner_id=owner_id)
    return self.item_repo.create(item)
```

### After

```python
def create_item(self, item_create: ItemCreate, owner_id: UUID):
    logger.info(f"Creating item: {item_create.title}, owner_id={owner_id}")
    
    # Decision point: Check if title exists
    if self.title_exists(item_create.title):
        logger.warning(
            f"Item creation failed: Title already exists: {item_create.title}"
        )
        raise ValueError("Title already exists")
    
    item = Item(**item_create.model_dump(), owner_id=owner_id)
    created_item = self.item_repo.create(item)
    
    logger.info(f"Item created successfully: {created_item.title} (ID: {created_item.id})")
    return created_item
```

## Step 5: Add Error Logging

### Before

```python
def process_item(self, item_id: UUID):
    item = self.get_item_by_id(item_id)
    result = self.do_complex_processing(item)
    return result
```

### After

```python
def process_item(self, item_id: UUID):
    logger.info(f"Processing item: {item_id}")
    
    try:
        item = self.get_item_by_id(item_id)
        result = self.do_complex_processing(item)
        logger.info(f"Item processed successfully: {item_id}")
        return result
    except Exception as e:
        logger.error(
            f"Item processing failed: {item_id}, error: {e}",
            exc_info=True  # Include stack trace
        )
        raise
```

## Step 6: Test Your Logging

### 1. Start the Backend

```bash
docker compose up backend
```

### 2. View Logs

```bash
docker compose logs -f backend
```

### 3. Make Test Requests

Use the Swagger UI at `http://localhost:8000/docs` or curl:

```bash
# Test create endpoint
curl -X POST "http://localhost:8000/api/v1/items/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Item", "description": "Test"}'
```

### 4. Verify Logs Appear

You should see logs like:

```
2025-12-29 10:30:45 - app.api.routes.items - INFO - create_item:42 - [a1b2c3d4] → POST /api/v1/items/ | User: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000)
2025-12-29 10:30:45 - app.services.item_service - INFO - create_item:23 - Creating item: Test Item, owner_id=123e4567-e89b-12d3-a456-426614174000
2025-12-29 10:30:45 - app.services.item_service - INFO - create_item:28 - Item created successfully: Test Item (ID: 456h7890-h12f-56h7-e890-860058518555)
2025-12-29 10:30:45 - app.api.routes.items - INFO - create_item:42 - [a1b2c3d4] ← POST /api/v1/items/ | Status: 200 | Time: 45.23ms
```

## Common Patterns

### Pattern 1: CRUD Operations

```python
# Create
logger.info(f"Creating {entity}: {name}")
# ... logic
logger.info(f"{entity} created: {name} (ID: {id})")

# Read
logger.debug(f"Fetching {entity} by ID: {id}")
# ... logic
if entity:
    logger.debug(f"{entity} found: {name} (ID: {id})")
else:
    logger.debug(f"{entity} not found: ID {id}")

# Update
logger.info(f"Updating {entity}: {name} (ID: {id})")
# ... logic
logger.info(f"{entity} updated: {name} (ID: {id})")

# Delete
logger.warning(f"Deleting {entity}: {name} (ID: {id})")
# ... logic
logger.info(f"{entity} deleted: {name} (ID: {id})")
```

### Pattern 2: Validation

```python
logger.debug(f"Validating {entity}: {name}")

if not self.is_valid(data):
    logger.warning(f"Validation failed for {entity}: {name}, reason: {reason}")
    raise ValidationError(reason)

logger.debug(f"Validation passed for {entity}: {name}")
```

### Pattern 3: Business Rules

```python
logger.debug(f"Checking business rule: {rule_name}")

if not self.rule_satisfied(data):
    logger.warning(f"Business rule violated: {rule_name}, entity: {entity_id}")
    raise BusinessRuleError(rule_name)

logger.debug(f"Business rule satisfied: {rule_name}")
```

## Files to Update (Priority Order)

### High Priority (User-Facing)
1. ✅ `app/api/routes/auth.py` - Already done
2. ✅ `app/api/routes/users.py` - Already done
3. ✅ `app/api/routes/person/person.py` - Already done
4. `app/api/routes/items.py`
5. `app/api/routes/posts.py`
6. `app/api/routes/support_tickets.py`

### Medium Priority (Services)
1. ✅ `app/services/auth_service.py` - Already done
2. ✅ `app/services/user_service.py` - Already done
3. ✅ `app/services/person/person_service.py` - Already done
4. `app/services/item_service.py`
5. `app/services/post_service.py`
6. `app/services/support_ticket_service.py`
7. `app/services/person/person_address_service.py`
8. `app/services/person/person_profession_service.py`

### Low Priority (Metadata)
1. `app/api/routes/address/metadata.py`
2. `app/api/routes/religion/metadata.py`
3. `app/services/address/*`
4. `app/services/religion/*`

## Automated Migration Script

You can use this script to add basic logging imports:

```bash
#!/bin/bash
# add_logging_imports.sh

# Add logging import to service files
for file in backend/app/services/**/*.py; do
    if ! grep -q "import logging" "$file"; then
        # Add import after other imports
        sed -i '1a import logging' "$file"
        # Add logger after class definition
        sed -i '/^class /a \    logger = logging.getLogger(__name__)' "$file"
        echo "Added logging to $file"
    fi
done
```

## Validation

After updating files, run:

```bash
# Check for syntax errors
cd backend
python -m py_compile app/services/your_service.py

# Run tests
pytest tests/test_logging.py

# Start backend and check logs
docker compose up backend
docker compose logs -f backend
```

## Troubleshooting

### Logs not appearing?

1. Check logger name: `logger = logging.getLogger(__name__)`
2. Check log level: Use INFO or WARNING in production
3. Check environment: DEBUG only works in local

### Too many logs?

1. Use DEBUG for detailed logs (only in local)
2. Use INFO for important operations
3. Use WARNING for issues

### Logs missing context?

1. Always include IDs: `(ID: {entity.id})`
2. Include operation name: `Creating item: {name}`
3. Include user context: `owner_id={owner_id}`

## Next Steps

1. Pick a file from the priority list
2. Follow the patterns in this guide
3. Test your changes
4. Move to the next file
5. Repeat until all files have logging

## Resources

- **[LOGGING.md](./LOGGING.md)** - Complete logging guide
- **[LOGGING_QUICK_REFERENCE.md](./LOGGING_QUICK_REFERENCE.md)** - Quick reference
- **[LOGGING_EXAMPLES.md](./LOGGING_EXAMPLES.md)** - Real-world examples

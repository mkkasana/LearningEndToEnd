# Logging Quick Reference

Quick reference for adding logging to your code.

## Import Logger

```python
import logging

logger = logging.getLogger(__name__)
```

## Log Levels

```python
logger.debug("Detailed debug information")      # Only in local
logger.info("General information")              # Default in staging
logger.warning("Warning message")               # Default in production
logger.error("Error message")                   # Always logged
logger.critical("Critical error")               # Always logged
```

## Route Logging (Automatic)

```python
from app.utils.logging_decorator import log_route

@router.post("/endpoint")
@log_route  # Add this decorator
def endpoint_function(session: SessionDep, current_user: CurrentUser):
    # Your code here
    pass
```

**Logs automatically:**
- Request method, path, query params
- Request body (masked)
- User info (if authenticated)
- Response status
- Execution time
- Request ID for tracing

## Service Logging (Manual)

### Basic Pattern

```python
def operation(self, data: DataCreate) -> Data:
    logger.info(f"Starting operation: {data.name}")
    
    # Your logic here
    
    logger.info(f"Operation completed: {data.name} (ID: {result.id})")
    return result
```

### With Decision Points

```python
def create_item(self, item_data: ItemCreate) -> Item:
    logger.info(f"Creating item: {item_data.name}")
    
    # Decision point: Check if exists
    if self.name_exists(item_data.name):
        logger.warning(f"Item creation failed: Name already exists: {item_data.name}")
        raise ValueError("Name already exists")
    
    # Decision point: Validate data
    if not self.is_valid(item_data):
        logger.warning(f"Item creation failed: Invalid data for {item_data.name}")
        raise ValueError("Invalid data")
    
    item = self.repo.create(item_data)
    logger.info(f"Item created successfully: {item.name} (ID: {item.id})")
    return item
```

### With Error Handling

```python
def risky_operation(self, data: Data) -> Result:
    logger.info(f"Starting risky operation: {data.id}")
    
    try:
        result = self.do_something(data)
        logger.info(f"Risky operation succeeded: {data.id}")
        return result
    except Exception as e:
        logger.error(f"Risky operation failed: {data.id}, error: {e}", exc_info=True)
        raise
```

## Common Patterns

### CRUD Operations

```python
# Create
logger.info(f"Creating {entity_type}: {name}")
# ... create logic
logger.info(f"{entity_type} created: {name} (ID: {id})")

# Read
logger.debug(f"Fetching {entity_type} by ID: {id}")
# ... fetch logic
if entity:
    logger.debug(f"{entity_type} found: {name} (ID: {id})")
else:
    logger.debug(f"{entity_type} not found: ID {id}")

# Update
logger.info(f"Updating {entity_type}: {name} (ID: {id})")
logger.debug(f"Updating fields: {list(update_data.keys())}")
# ... update logic
logger.info(f"{entity_type} updated: {name} (ID: {id})")

# Delete
logger.warning(f"Deleting {entity_type}: {name} (ID: {id})")
# ... delete logic
logger.info(f"{entity_type} deleted: {name} (ID: {id})")
```

### Authentication

```python
logger.debug(f"Attempting authentication for: {email}")

if not user:
    logger.warning(f"Authentication failed: User not found: {email}")
    return None

if not verify_password(password, user.hashed_password):
    logger.warning(f"Authentication failed: Invalid password: {email}")
    return None

logger.info(f"Authentication successful: {email} (ID: {user.id})")
return user
```

### Validation

```python
logger.debug(f"Validating {entity_type}: {name}")

if not self.is_valid(data):
    logger.warning(f"Validation failed for {entity_type}: {name}, reason: {reason}")
    raise ValidationError(reason)

logger.debug(f"Validation passed for {entity_type}: {name}")
```

### Business Rules

```python
logger.debug(f"Checking business rule: {rule_name}")

if not self.rule_satisfied(data):
    logger.warning(f"Business rule violated: {rule_name}, entity: {entity_id}")
    raise BusinessRuleError(rule_name)

logger.debug(f"Business rule satisfied: {rule_name}")
```

## What to Log

### ✅ DO Log

- Operation start/completion
- Decision points (if/else branches)
- Business rule violations
- Authentication attempts (success/failure)
- Data validation failures
- Important state changes
- User actions
- Performance issues
- Errors with context

### ❌ DON'T Log

- Passwords (automatically masked)
- Tokens (automatically masked)
- Secrets (automatically masked)
- Credit card numbers
- Social security numbers
- Excessive detail in tight loops
- Redundant information

## Log Format

```
%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s
```

**Example:**
```
2025-12-29 10:30:45 - app.services.user_service - INFO - create_user:45 - User created: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000)
```

## Include Context

Always include relevant IDs and context:

```python
# ✅ Good - includes context
logger.info(f"User created: {user.email} (ID: {user.id}), is_active={user.is_active}")

# ❌ Bad - no context
logger.info("User created")
```

## Sensitive Data

These fields are automatically masked:
- `password`, `hashed_password`
- `token`, `access_token`, `refresh_token`
- `secret`, `api_key`
- `authorization`, `cookie`, `session`
- `csrf_token`, `new_password`, `current_password`

## Request Tracing

Use request IDs to trace requests:

```
[a1b2c3d4] → POST /api/v1/users/signup
[a1b2c3d4] Creating new user: user@example.com
[a1b2c3d4] User created successfully
[a1b2c3d4] ← POST /api/v1/users/signup | Status: 200 | Time: 234.56ms
```

## Viewing Logs

```bash
# All logs
docker compose logs -f backend

# Only errors
docker compose logs backend | grep ERROR

# Specific user
docker compose logs backend | grep "user@example.com"

# Specific request
docker compose logs backend | grep "[a1b2c3d4]"

# Specific module
docker compose logs backend | grep "auth_service"
```

## Testing Logs

```python
def test_user_creation(caplog):
    caplog.set_level(logging.INFO)
    
    user_service.create_user(user_data)
    
    assert "User created successfully" in caplog.text
```

## Performance Tips

- Use f-strings (lazy evaluation)
- Avoid logging in tight loops
- Use DEBUG level for verbose logging
- Check log level before expensive operations:

```python
if logger.isEnabledFor(logging.DEBUG):
    expensive_debug_info = compute_expensive_info()
    logger.debug(f"Debug info: {expensive_debug_info}")
```

## Common Mistakes

### ❌ Don't do this:
```python
# String concatenation (always evaluated)
logger.debug("User: " + str(user.id) + " created")

# Logging in loops
for item in large_list:
    logger.debug(f"Processing {item}")  # Too many logs!

# No context
logger.info("Operation completed")

# Logging sensitive data directly
logger.debug(f"Password: {password}")
```

### ✅ Do this:
```python
# f-strings (lazy evaluation)
logger.debug(f"User: {user.id} created")

# Summary after loop
logger.info(f"Processed {len(large_list)} items")

# Include context
logger.info(f"Operation completed: {operation_name} (ID: {operation_id})")

# Let masking handle it
logger.debug(f"Login data: {login_data}")  # password will be masked
```

## Checklist

When adding logging to new code:

- [ ] Import logger: `logger = logging.getLogger(__name__)`
- [ ] Add `@log_route` to API routes
- [ ] Log operation start with context
- [ ] Log at decision points (if/else)
- [ ] Log operation completion with result
- [ ] Log errors with `exc_info=True`
- [ ] Include relevant IDs (user_id, entity_id, etc.)
- [ ] Use appropriate log level
- [ ] Don't log sensitive data directly
- [ ] Test logs in development

## More Information

- **Complete Guide**: `backend/documentation/LOGGING.md`
- **Examples**: `backend/documentation/LOGGING_EXAMPLES.md`
- **Quick Start**: `backend/documentation/logging/README.md`

# Logging Implementation Summary

Comprehensive logging system implemented for the Family Management backend.

## What Was Implemented

### 1. Core Logging Infrastructure

#### `app/core/logging_config.py`
- **Sensitive data masking** - Automatically masks passwords, tokens, secrets
- **Environment-based log levels** - DEBUG (local), INFO (staging), WARNING (production)
- **Structured logging format** - Timestamp, module, level, function, line number, message
- **Third-party library log control** - Configures uvicorn, sqlalchemy, fastapi log levels

#### `app/utils/logging_decorator.py`
- **`@log_route` decorator** - Automatic request/response logging for API routes
- **Request tracing** - Unique 8-character ID for each request
- **Performance monitoring** - Execution time tracking
- **User context** - Automatically logs authenticated user information
- **Sensitive data protection** - Masks request/response bodies
- **Error tracking** - Comprehensive error logging with stack traces

### 2. Application Integration

#### `app/main.py`
- Logging initialization on startup
- Application lifecycle logging
- CORS configuration logging
- Sentry integration logging

### 3. Service Layer Logging

#### `app/services/auth_service.py`
- Authentication attempt logging
- Success/failure logging with reasons
- Token creation logging
- Inactive user detection logging

#### `app/services/user_service.py`
- User CRUD operation logging
- Email existence checks
- Password updates
- Field-level update tracking
- User deletion warnings

#### `app/services/person/person_service.py`
- Person CRUD operation logging
- User-person relationship tracking
- Field-level update tracking
- Person deletion warnings

#### `app/services/person/person_relationship_service.py`
- Already had comprehensive logging
- Bidirectional relationship creation tracking
- Transaction logging
- Inverse relationship detection
- Error handling with rollback logging

### 4. Route Layer Logging

Added `@log_route` decorator to key routes:

#### Authentication Routes (`app/api/routes/auth.py`)
- `POST /login/access-token` - Login
- `POST /login/test-token` - Token validation
- `POST /password-recovery/{email}` - Password recovery
- `POST /reset-password/` - Password reset

#### User Routes (`app/api/routes/users.py`)
- `GET /users/` - List users
- `POST /users/` - Create user
- `PATCH /users/me` - Update own profile
- `POST /users/signup` - User registration

#### Person Routes (`app/api/routes/person/person.py`)
- `GET /person/me` - Get own person
- `POST /person/me` - Create own person
- `POST /person/family-member` - Create family member
- `POST /person/search-matches` - Search for matching persons
- `GET /person/me/relationships` - Get relationships
- `POST /person/me/relationships` - Create relationship

### 5. Documentation

#### `backend/documentation/LOGGING.md`
- Complete logging guide
- Best practices
- Configuration details
- Security considerations
- Troubleshooting guide

#### `backend/documentation/LOGGING_EXAMPLES.md`
- Real-world logging examples
- Authentication flow examples
- User registration examples
- Relationship management examples
- Error scenario examples
- Performance monitoring examples

#### `backend/documentation/logging/README.md`
- Quick start guide
- Feature overview
- Quick examples
- Production considerations

## Key Features

### 1. Sensitive Data Protection

Automatically masks these fields in logs:
- `password`, `hashed_password`
- `token`, `access_token`, `refresh_token`
- `secret`, `api_key`
- `authorization`, `cookie`, `session`
- `csrf_token`, `new_password`, `current_password`

### 2. Request Tracing

Each request gets a unique ID for tracing through logs:
```
[a1b2c3d4] → POST /api/v1/users/signup
[a1b2c3d4] Creating new user: user@example.com
[a1b2c3d4] User created successfully
[a1b2c3d4] ← POST /api/v1/users/signup | Status: 200 | Time: 234.56ms
```

### 3. Performance Monitoring

All requests log execution time:
```
[a1b2c3d4] ← POST /api/v1/person/search-matches | Status: 200 | Time: 2456.78ms
```

### 4. User Context

Authenticated requests automatically log user information:
```
[a1b2c3d4] → POST /api/v1/person/me | User: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000)
```

### 5. Business Logic Logging

Strategic logging at decision points:
```python
if self.email_exists(email):
    logger.warning(f"User creation failed: Email already exists: {email}")
    raise EmailAlreadyExistsError()
```

## Log Levels by Environment

- **Local**: `DEBUG` - Verbose logging for development
- **Staging**: `INFO` - Standard operational logging
- **Production**: `WARNING` - Only warnings and errors

## Usage Examples

### Adding Logging to a New Service

```python
import logging

logger = logging.getLogger(__name__)

class MyService:
    def create_item(self, item_data: ItemCreate) -> Item:
        logger.info(f"Creating item: {item_data.name}")
        
        if self.name_exists(item_data.name):
            logger.warning(f"Item creation failed: Name already exists")
            raise ValueError("Name already exists")
        
        item = self.repo.create(item_data)
        logger.info(f"Item created successfully: {item.name} (ID: {item.id})")
        return item
```

### Adding Logging to a New Route

```python
from app.utils.logging_decorator import log_route

@router.post("/items")
@log_route
def create_item(session: SessionDep, current_user: CurrentUser, item_in: ItemCreate):
    # Your code here
    pass
```

## Viewing Logs

### Development (Docker)
```bash
# View all logs
docker compose logs -f backend

# View only errors
docker compose logs backend | grep ERROR

# View specific user activity
docker compose logs backend | grep "user@example.com"

# View specific request
docker compose logs backend | grep "[a1b2c3d4]"
```

## Next Steps

To add logging to remaining routes and services:

1. **Import the decorator**:
   ```python
   from app.utils.logging_decorator import log_route
   ```

2. **Add to route functions**:
   ```python
   @router.post("/endpoint")
   @log_route
   def endpoint_function(...):
       pass
   ```

3. **Add to service methods**:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   def method(self, ...):
       logger.info("Operation starting")
       # ... business logic with logging at decision points
       logger.info("Operation completed")
   ```

## Files Modified

### New Files
- `app/core/logging_config.py` - Logging configuration
- `app/utils/logging_decorator.py` - Route logging decorator
- `backend/documentation/LOGGING.md` - Complete guide
- `backend/documentation/LOGGING_EXAMPLES.md` - Examples
- `backend/documentation/logging/README.md` - Quick start

### Modified Files
- `app/main.py` - Initialize logging
- `app/services/auth_service.py` - Add logging
- `app/services/user_service.py` - Add logging
- `app/services/person/person_service.py` - Add logging
- `app/api/routes/auth.py` - Add @log_route decorator
- `app/api/routes/users.py` - Add @log_route decorator
- `app/api/routes/person/person.py` - Add @log_route decorator

## Testing

To test the logging:

1. Start the backend:
   ```bash
   docker compose up backend
   ```

2. Make API requests and observe logs:
   ```bash
   docker compose logs -f backend
   ```

3. Try different operations:
   - Login (successful and failed)
   - User registration
   - Creating persons
   - Creating relationships
   - Search operations

## Security Considerations

✅ Passwords and tokens are automatically masked  
✅ Sensitive fields are never logged in plain text  
✅ User IDs are logged (not sensitive)  
✅ Email addresses are logged (for debugging)  
✅ Request bodies are masked before logging  
✅ Response bodies are masked in debug mode  

## Performance Impact

- Minimal overhead in production (WARNING level)
- DEBUG level only in local environment
- String formatting is lazy (only when level is enabled)
- No performance impact on critical paths

## Maintenance

- Log configuration is centralized in `logging_config.py`
- Sensitive fields list can be updated in one place
- Log format can be changed globally
- Environment-based levels are automatic

## Support

For questions or issues:
1. Check `backend/documentation/LOGGING.md`
2. Review `backend/documentation/LOGGING_EXAMPLES.md`
3. Contact the development team

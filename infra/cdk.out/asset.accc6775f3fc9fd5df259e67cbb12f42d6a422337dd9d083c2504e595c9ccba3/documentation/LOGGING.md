# Logging Guide

Complete guide to logging in the backend application.

## Overview

The application uses Python's built-in `logging` module with custom configuration for:
- **Sensitive data protection** - Automatically masks passwords, tokens, and other sensitive fields
- **Request/response logging** - Decorator for automatic API route logging
- **Business logic logging** - Strategic logging at decision points
- **Environment-based levels** - Different log levels for local/staging/production

## Log Levels by Environment

- **Local**: `DEBUG` - Verbose logging for development
- **Staging**: `INFO` - Standard operational logging
- **Production**: `WARNING` - Only warnings and errors

## Sensitive Data Protection

The logging system automatically masks sensitive fields to protect user privacy:

### Protected Fields
```python
SENSITIVE_FIELDS = {
    "password",
    "hashed_password",
    "token",
    "access_token",
    "refresh_token",
    "secret",
    "api_key",
    "authorization",
    "cookie",
    "session",
    "csrf_token",
    "new_password",
    "current_password",
    "confirm_password",
}
```

### Example
```python
# Input
{"email": "user@example.com", "password": "secret123"}

# Logged as
{"email": "user@example.com", "password": "***MASKED***"}
```

## Using the Route Logging Decorator

The `@log_route` decorator automatically logs:
- Request method, path, and query parameters
- Request body (with sensitive data masked)
- Response status code
- Execution time
- User information (if authenticated)
- Request ID for tracing

### Usage

```python
from app.utils.logging_decorator import log_route

@router.get("/example")
@log_route
def example_endpoint(session: SessionDep, current_user: CurrentUser):
    return {"message": "Hello"}
```

### Log Output

```
2025-12-29 10:30:45 - app.api.routes.example - INFO - example_endpoint:42 - [a1b2c3d4] → GET /api/v1/example | User: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000) | Query: {}
2025-12-29 10:30:45 - app.api.routes.example - INFO - example_endpoint:42 - [a1b2c3d4] ← GET /api/v1/example | Status: 200 | Time: 45.23ms
```

## Service Layer Logging

Add logging to services at key decision points:

### Example: Authentication Service

```python
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def authenticate_user(self, email: str, password: str) -> User | None:
        logger.debug(f"Attempting authentication for email: {email}")
        
        user = self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"Authentication failed: User not found for email: {email}")
            return None
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentication failed: Invalid password for email: {email}")
            return None
        
        logger.info(f"Authentication successful for user: {email} (ID: {user.id})")
        return user
```

## Logging Best Practices

### 1. Use Appropriate Log Levels

- **DEBUG**: Detailed information for debugging (e.g., "Fetching user by ID: 123")
- **INFO**: General informational messages (e.g., "User created successfully")
- **WARNING**: Warning messages (e.g., "User not found", "Invalid password")
- **ERROR**: Error messages (e.g., "Database connection failed")
- **CRITICAL**: Critical errors (e.g., "System shutdown")

### 2. Log at Decision Points

```python
def create_user(self, user_create: UserCreate) -> User:
    logger.info(f"Creating new user: {user_create.email}")
    
    # Decision point: Check if email exists
    if self.email_exists(user_create.email):
        logger.warning(f"User creation failed: Email already exists: {user_create.email}")
        raise EmailAlreadyExistsError()
    
    user = self.user_repo.create(user)
    logger.info(f"User created successfully: {user.email} (ID: {user.id})")
    return user
```

### 3. Include Context

Always include relevant IDs and context:

```python
# Good
logger.info(f"Updating person: {person.first_name} {person.last_name} (ID: {person.id})")

# Bad
logger.info("Updating person")
```

### 4. Log Exceptions

```python
try:
    result = some_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

### 5. Don't Log Sensitive Data Directly

```python
# Bad - logs password
logger.debug(f"User login: {email}, password: {password}")

# Good - no sensitive data
logger.debug(f"User login attempt: {email}")
```

## Request Tracing

Each request gets a unique 8-character request ID for tracing:

```
[a1b2c3d4] → GET /api/v1/users/me
[a1b2c3d4] Fetching user by ID: 123e4567-e89b-12d3-a456-426614174000
[a1b2c3d4] User found: user@example.com
[a1b2c3d4] ← GET /api/v1/users/me | Status: 200 | Time: 23.45ms
```

## Log Format

```
%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s
```

Example:
```
2025-12-29 10:30:45 - app.services.user_service - INFO - create_user:45 - User created successfully: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000)
```

## Adding Logging to New Code

### 1. Import Logger

```python
import logging

logger = logging.getLogger(__name__)
```

### 2. Add to Routes (Optional)

```python
from app.utils.logging_decorator import log_route

@router.post("/example")
@log_route
def example_endpoint(...):
    ...
```

### 3. Add to Services

```python
class ExampleService:
    def create_example(self, data: ExampleCreate) -> Example:
        logger.info(f"Creating example: {data.name}")
        
        # Business logic with logging at decision points
        if self.name_exists(data.name):
            logger.warning(f"Example creation failed: Name already exists: {data.name}")
            raise ValueError("Name already exists")
        
        example = self.repo.create(data)
        logger.info(f"Example created successfully: {example.name} (ID: {example.id})")
        return example
```

## Viewing Logs

### Development (Docker)
```bash
docker compose logs -f backend
```

### Production
Logs are sent to stdout and can be collected by your logging infrastructure (e.g., CloudWatch, Datadog, etc.)

## Configuration

Logging is configured in `app/core/logging_config.py`:

```python
from app.core.logging_config import setup_logging

# Call once at application startup
setup_logging()
```

This is automatically called in `app/main.py`.

## Testing Logs

In tests, you can capture logs:

```python
import logging

def test_user_creation(caplog):
    caplog.set_level(logging.INFO)
    
    # Your test code
    user_service.create_user(user_data)
    
    # Assert logs
    assert "User created successfully" in caplog.text
```

## Performance Considerations

- Log levels are checked before string formatting
- Use f-strings for better performance
- Avoid logging in tight loops
- Use DEBUG level for verbose logging (disabled in production)

## Security Notes

1. **Never log passwords or tokens** - The system masks them automatically, but avoid logging them directly
2. **Be careful with PII** - Consider what personal information you log
3. **Use appropriate log levels** - Don't log sensitive operations at DEBUG level in production
4. **Sanitize user input** - Don't log unsanitized user input that could contain injection attacks

## Troubleshooting

### Logs not appearing?

1. Check log level: `logger.setLevel(logging.DEBUG)`
2. Check environment: Local uses DEBUG, production uses WARNING
3. Check logger name: Use `logger = logging.getLogger(__name__)`

### Too many logs?

1. Increase log level for third-party libraries
2. Use DEBUG level only for your code
3. Filter logs by module name

### Need more context?

1. Add request ID to all related logs
2. Include relevant IDs (user_id, person_id, etc.)
3. Log at decision points, not just success/failure

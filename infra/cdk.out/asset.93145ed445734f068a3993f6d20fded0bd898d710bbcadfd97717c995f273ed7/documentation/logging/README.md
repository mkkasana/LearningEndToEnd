# Logging System

Comprehensive logging system for the Family Management backend with automatic sensitive data masking and request tracing.

## Quick Start

Logging is automatically configured when the application starts. No additional setup required!

### View Logs (Development)

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

## Features

✅ **Automatic Sensitive Data Masking** - Passwords, tokens, and secrets are automatically masked  
✅ **Request/Response Logging** - Decorator for automatic API route logging  
✅ **Request Tracing** - Unique ID for each request to trace through logs  
✅ **Business Logic Logging** - Strategic logging at decision points  
✅ **Environment-Based Levels** - DEBUG in local, INFO in staging, WARNING in production  
✅ **Performance Monitoring** - Execution time tracking for all requests  
✅ **User Context** - Automatically logs user information for authenticated requests  

## Documentation

- **[LOGGING.md](../LOGGING.md)** - Complete logging guide with best practices
- **[LOGGING_EXAMPLES.md](../LOGGING_EXAMPLES.md)** - Real-world logging examples

## Quick Examples

### Adding Logging to a Service

```python
import logging

logger = logging.getLogger(__name__)

class MyService:
    def create_item(self, item_data: ItemCreate) -> Item:
        logger.info(f"Creating item: {item_data.name}")
        
        if self.name_exists(item_data.name):
            logger.warning(f"Item creation failed: Name already exists: {item_data.name}")
            raise ValueError("Name already exists")
        
        item = self.repo.create(item_data)
        logger.info(f"Item created successfully: {item.name} (ID: {item.id})")
        return item
```

### Adding Logging to a Route

```python
from app.utils.logging_decorator import log_route

@router.post("/items")
@log_route
def create_item(session: SessionDep, current_user: CurrentUser, item_in: ItemCreate):
    # Your code here
    pass
```

### Log Output

```
2025-12-29 10:30:45 - app.api.routes.items - INFO - create_item:42 - [a1b2c3d4] → POST /api/v1/items | User: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000) | Query: {}
2025-12-29 10:30:45 - app.services.item_service - INFO - create_item:23 - Creating item: My Item
2025-12-29 10:30:45 - app.services.item_service - INFO - create_item:30 - Item created successfully: My Item (ID: 456h7890-h12f-56h7-e890-860058518555)
2025-12-29 10:30:45 - app.api.routes.items - INFO - create_item:42 - [a1b2c3d4] ← POST /api/v1/items | Status: 200 | Time: 45.23ms
```

## Sensitive Data Protection

The following fields are automatically masked in logs:

- `password`, `hashed_password`
- `token`, `access_token`, `refresh_token`
- `secret`, `api_key`
- `authorization`, `cookie`, `session`
- `csrf_token`
- `new_password`, `current_password`, `confirm_password`

### Example

```python
# Input
{"email": "user@example.com", "password": "secret123"}

# Logged as
{"email": "user@example.com", "password": "***MASKED***"}
```

## Log Levels

- **DEBUG**: Detailed information for debugging (only in local environment)
- **INFO**: General informational messages (default in staging)
- **WARNING**: Warning messages (default in production)
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

## Request Tracing

Each request gets a unique 8-character ID for tracing:

```
[a1b2c3d4] → POST /api/v1/users/signup
[a1b2c3d4] Creating new user: user@example.com
[a1b2c3d4] User created successfully
[a1b2c3d4] ← POST /api/v1/users/signup | Status: 200 | Time: 234.56ms
```

## Performance Monitoring

All requests log execution time:

```
[a1b2c3d4] ← POST /api/v1/person/search-matches | Status: 200 | Time: 2456.78ms
```

Use this to identify slow endpoints and optimize performance.

## Configuration

Logging is configured in `app/core/logging_config.py` and automatically initialized in `app/main.py`.

### Log Format

```
%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s
```

### Example

```
2025-12-29 10:30:45 - app.services.user_service - INFO - create_user:45 - User created successfully: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000)
```

## Best Practices

1. **Use appropriate log levels** - DEBUG for details, INFO for operations, WARNING for issues
2. **Include context** - Always include relevant IDs and user information
3. **Log at decision points** - Log when making important decisions
4. **Don't log sensitive data** - The system masks it, but avoid logging it directly
5. **Use request IDs** - Makes tracing requests through logs easier

## Troubleshooting

### Logs not appearing?

1. Check log level configuration
2. Verify logger name: `logger = logging.getLogger(__name__)`
3. Check environment variable

### Too many logs?

1. Increase log level in production
2. Filter by module name
3. Use log aggregation tools

### Need more context?

1. Add request ID to all related logs
2. Include relevant IDs (user_id, person_id, etc.)
3. Log at more decision points

## Production Considerations

- Logs are sent to stdout (can be collected by CloudWatch, Datadog, etc.)
- Sensitive data is automatically masked
- Log level is WARNING by default in production
- Consider log rotation and retention policies
- Use log aggregation for searching and analysis

## Support

For questions or issues with logging:
1. Check [LOGGING.md](../LOGGING.md) for detailed documentation
2. Review [LOGGING_EXAMPLES.md](../LOGGING_EXAMPLES.md) for examples
3. Contact the development team

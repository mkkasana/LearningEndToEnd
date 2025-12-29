# Logging Examples

Real-world examples of logging output from the application.

## Authentication Flow

### Successful Login

```
2025-12-29 10:30:45 - app.api.routes.auth - INFO - login_access_token:42 - [a1b2c3d4] → POST /api/v1/login/access-token | Query: {}
2025-12-29 10:30:45 - app.api.routes.auth - DEBUG - login_access_token:42 - [a1b2c3d4] Request body: {"username": "user@example.com", "password": "***MASKED***"}
2025-12-29 10:30:45 - app.services.auth_service - DEBUG - authenticate_user:23 - Attempting authentication for email: user@example.com
2025-12-29 10:30:45 - app.repositories.user_repository - DEBUG - get_by_email:45 - Fetching user by email: user@example.com
2025-12-29 10:30:45 - app.services.auth_service - INFO - authenticate_user:35 - Authentication successful for user: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000)
2025-12-29 10:30:45 - app.services.auth_service - DEBUG - create_access_token_for_user:42 - Creating access token for user: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000)
2025-12-29 10:30:45 - app.services.auth_service - INFO - create_access_token_for_user:45 - Access token created for user: user@example.com, expires in 8 days, 0:00:00
2025-12-29 10:30:45 - app.api.routes.auth - INFO - login_access_token:42 - [a1b2c3d4] ← POST /api/v1/login/access-token | Status: 200 | Time: 145.23ms
```

### Failed Login - Invalid Password

```
2025-12-29 10:31:12 - app.api.routes.auth - INFO - login_access_token:42 - [b2c3d4e5] → POST /api/v1/login/access-token | Query: {}
2025-12-29 10:31:12 - app.services.auth_service - DEBUG - authenticate_user:23 - Attempting authentication for email: user@example.com
2025-12-29 10:31:12 - app.services.auth_service - WARNING - authenticate_user:30 - Authentication failed: Invalid password for email: user@example.com
2025-12-29 10:31:12 - app.api.routes.auth - ERROR - login_access_token:42 - [b2c3d4e5] ✗ POST /api/v1/login/access-token | Error: AuthenticationError: Incorrect email or password | Time: 98.45ms
```

### Failed Login - User Not Found

```
2025-12-29 10:31:45 - app.api.routes.auth - INFO - login_access_token:42 - [c3d4e5f6] → POST /api/v1/login/access-token | Query: {}
2025-12-29 10:31:45 - app.services.auth_service - DEBUG - authenticate_user:23 - Attempting authentication for email: nonexistent@example.com
2025-12-29 10:31:45 - app.services.auth_service - WARNING - authenticate_user:27 - Authentication failed: User not found for email: nonexistent@example.com
2025-12-29 10:31:45 - app.api.routes.auth - ERROR - login_access_token:42 - [c3d4e5f6] ✗ POST /api/v1/login/access-token | Error: AuthenticationError: Incorrect email or password | Time: 45.67ms
```

## User Registration Flow

### Successful Registration

```
2025-12-29 10:35:20 - app.api.routes.users - INFO - register_user:156 - [d4e5f6g7] → POST /api/v1/users/signup | Query: {}
2025-12-29 10:35:20 - app.api.routes.users - DEBUG - register_user:156 - [d4e5f6g7] Request body: {"email": "newuser@example.com", "password": "***MASKED***", "first_name": "John", "last_name": "Doe", "gender": "MALE", "date_of_birth": "1990-01-15"}
2025-12-29 10:35:20 - app.services.user_service - DEBUG - email_exists:78 - Checking if email exists: newuser@example.com
2025-12-29 10:35:20 - app.services.user_service - DEBUG - email_exists:82 - Email does not exist: newuser@example.com
2025-12-29 10:35:20 - app.services.user_service - INFO - create_user:45 - Creating new user: newuser@example.com
2025-12-29 10:35:20 - app.services.user_service - INFO - create_user:54 - User created successfully: newuser@example.com (ID: 234f5678-f90c-23e4-b567-537725285111), is_superuser=False, is_active=True
2025-12-29 10:35:20 - app.services.person.person_service - INFO - create_person:28 - Creating person: John Doe, gender_id=789a0123-a01d-34f5-c678-648836396222, user_id=234f5678-f90c-23e4-b567-537725285111
2025-12-29 10:35:20 - app.services.person.person_service - INFO - create_person:32 - Person created successfully: John Doe (ID: 345g6789-g01e-45g6-d789-759947407333), is_primary=True
2025-12-29 10:35:20 - app.api.routes.users - INFO - register_user:156 - [d4e5f6g7] ← POST /api/v1/users/signup | Status: 200 | Time: 234.56ms
```

### Failed Registration - Email Already Exists

```
2025-12-29 10:36:15 - app.api.routes.users - INFO - register_user:156 - [e5f6g7h8] → POST /api/v1/users/signup | Query: {}
2025-12-29 10:36:15 - app.services.user_service - DEBUG - email_exists:78 - Checking if email exists: existing@example.com
2025-12-29 10:36:15 - app.services.user_service - DEBUG - email_exists:86 - Email already exists: existing@example.com
2025-12-29 10:36:15 - app.api.routes.users - ERROR - register_user:156 - [e5f6g7h8] ✗ POST /api/v1/users/signup | Error: HTTPException: The user with this email already exists in the system | Time: 23.45ms
```

## Person and Relationship Management

### Creating a Family Member

```
2025-12-29 10:40:30 - app.api.routes.person.person - INFO - create_family_member:112 - [f6g7h8i9] → POST /api/v1/person/family-member | User: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000) | Query: {}
2025-12-29 10:40:30 - app.api.routes.person.person - DEBUG - create_family_member:112 - [f6g7h8i9] Request body: {"first_name": "Jane", "last_name": "Doe", "gender_id": "890b1234-b12e-45g6-d789-759947407444", "date_of_birth": "1992-05-20", "user_id": null}
2025-12-29 10:40:30 - app.services.person.person_service - INFO - create_person:28 - Creating person: Jane Doe, gender_id=890b1234-b12e-45g6-d789-759947407444, user_id=None
2025-12-29 10:40:30 - app.services.person.person_service - INFO - create_person:32 - Person created successfully: Jane Doe (ID: 456h7890-h12f-56h7-e890-860058518555), is_primary=False
2025-12-29 10:40:30 - app.api.routes.person.person - INFO - create_family_member:112 - [f6g7h8i9] ← POST /api/v1/person/family-member | Status: 200 | Time: 89.12ms
```

### Creating a Bidirectional Relationship

```
2025-12-29 10:42:15 - app.api.routes.person.person - INFO - create_my_relationship:789 - [g7h8i9j0] → POST /api/v1/person/me/relationships | User: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000) | Query: {}
2025-12-29 10:42:15 - app.api.routes.person.person - DEBUG - create_my_relationship:789 - [g7h8i9j0] Request body: {"related_person_id": "456h7890-h12f-56h7-e890-860058518555", "relationship_type": "SISTER"}
2025-12-29 10:42:15 - app.services.person.person_relationship_service - INFO - create_relationship:45 - Creating relationship: person_id=345g6789-g01e-45g6-d789-759947407333, related_person_id=456h7890-h12f-56h7-e890-860058518555, type=SISTER
2025-12-29 10:42:15 - app.services.person.person_relationship_service - INFO - create_relationship:67 - Created primary relationship with ID: 567i8901-i23g-67i8-f901-971169629666
2025-12-29 10:42:15 - app.services.person.person_relationship_service - INFO - create_relationship:95 - Created inverse relationship with ID: 678j9012-j34h-78j9-g012-082270730777, type: BROTHER
2025-12-29 10:42:15 - app.services.person.person_relationship_service - INFO - create_relationship:101 - Successfully committed bidirectional relationship creation
2025-12-29 10:42:15 - app.api.routes.person.person - INFO - create_my_relationship:789 - [g7h8i9j0] ← POST /api/v1/person/me/relationships | Status: 200 | Time: 156.78ms
```

### Searching for Matching Persons

```
2025-12-29 10:45:00 - app.api.routes.person.person - INFO - search_matching_persons:145 - [h8i9j0k1] → POST /api/v1/person/search-matches | User: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000) | Query: {}
2025-12-29 10:45:00 - app.api.routes.person.person - DEBUG - search_matching_persons:145 - [h8i9j0k1] Request body: {"first_name": "John", "last_name": "Smith", "country_id": "901c2345-c23f-89k0-h123-193381841888", "state_id": "012d3456-d34g-90l1-i234-204492952999"}
2025-12-29 10:45:00 - app.api.routes.person.person - INFO - search_matching_persons:150 - Person search request from user user@example.com: name=John Smith, country=901c2345-c23f-89k0-h123-193381841888, state=012d3456-d34g-90l1-i234-204492952999, district=None, religion=None
2025-12-29 10:45:00 - app.services.person.person_matching_service - INFO - search_matching_persons:78 - Searching for matching persons with criteria: first_name=John, last_name=Smith
2025-12-29 10:45:00 - app.services.person.person_matching_service - INFO - search_matching_persons:145 - Found 3 potential matches
2025-12-29 10:45:00 - app.api.routes.person.person - INFO - search_matching_persons:165 - Found 3 matching persons for user user@example.com
2025-12-29 10:45:00 - app.api.routes.person.person - INFO - search_matching_persons:145 - [h8i9j0k1] ← POST /api/v1/person/search-matches | Status: 200 | Time: 234.56ms
```

## Error Scenarios

### Database Connection Error

```
2025-12-29 10:50:00 - app.repositories.user_repository - ERROR - get_by_email:45 - Database query failed: connection timeout
2025-12-29 10:50:00 - app.api.routes.auth - ERROR - login_access_token:42 - [i9j0k1l2] ✗ POST /api/v1/login/access-token | Error: DatabaseError: Database connection failed | Time: 5000.00ms
```

### Permission Denied

```
2025-12-29 10:52:30 - app.api.routes.users - INFO - delete_user:345 - [j0k1l2m3] → DELETE /api/v1/users/234f5678-f90c-23e4-b567-537725285111 | User: normaluser@example.com (ID: 345g6789-g01e-45g6-d789-759947407333) | Query: {}
2025-12-29 10:52:30 - app.api.routes.users - ERROR - delete_user:345 - [j0k1l2m3] ✗ DELETE /api/v1/users/234f5678-f90c-23e4-b567-537725285111 | Error: PermissionDeniedError: The user doesn't have enough privileges | Time: 12.34ms
```

### Validation Error

```
2025-12-29 10:55:00 - app.api.routes.users - INFO - register_user:156 - [k1l2m3n4] → POST /api/v1/users/signup | Query: {}
2025-12-29 10:55:00 - app.api.routes.users - ERROR - register_user:156 - [k1l2m3n4] ✗ POST /api/v1/users/signup | Error: ValidationError: Invalid date format. Use YYYY-MM-DD | Time: 5.67ms
```

## Performance Monitoring

### Slow Query Detection

```
2025-12-29 11:00:00 - app.api.routes.person.person - INFO - search_matching_persons:145 - [l2m3n4o5] → POST /api/v1/person/search-matches | User: user@example.com (ID: 123e4567-e89b-12d3-a456-426614174000) | Query: {}
2025-12-29 11:00:00 - app.services.person.person_matching_service - WARNING - search_matching_persons:145 - Search query took longer than expected: 2345.67ms
2025-12-29 11:00:00 - app.api.routes.person.person - INFO - search_matching_persons:145 - [l2m3n4o5] ← POST /api/v1/person/search-matches | Status: 200 | Time: 2456.78ms
```

## Startup Logs

```
2025-12-29 09:00:00 - app.core.logging_config - INFO - setup_logging:78 - Logging configured for environment: local
2025-12-29 09:00:00 - app.main - INFO - <module>:25 - Starting Family Management System in local environment
2025-12-29 09:00:00 - app.main - INFO - <module>:35 - CORS enabled for origins: ['http://localhost:5173']
2025-12-29 09:00:00 - app.main - INFO - <module>:38 - API router mounted at /api/v1
2025-12-29 09:00:00 - uvicorn.error - INFO - Started server process [12345]
2025-12-29 09:00:00 - uvicorn.error - INFO - Waiting for application startup.
2025-12-29 09:00:00 - uvicorn.error - INFO - Application startup complete.
2025-12-29 09:00:00 - uvicorn.error - INFO - Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Log Filtering Examples

### View only errors
```bash
docker compose logs backend | grep ERROR
```

### View specific user's activity
```bash
docker compose logs backend | grep "user@example.com"
```

### View specific request trace
```bash
docker compose logs backend | grep "\[a1b2c3d4\]"
```

### View authentication logs
```bash
docker compose logs backend | grep "auth_service"
```

### View relationship operations
```bash
docker compose logs backend | grep "person_relationship_service"
```

---
applyTo: "app/core/exceptions.py,app/core/error_handlers.py,**/*exception*.py"
---

# Error Handling Instructions

## Exception Hierarchy

This service uses a custom exception hierarchy that maps to specific HTTP status codes:

- `NotFoundError` → HTTP 404
- `ConflictError` → HTTP 409
- `ValidationError` → HTTP 422
- `DatabaseError` → HTTP 500
- `AuthenticationError` → HTTP 401
- `AuthorizationError` → HTTP 403

## Usage Patterns

**In Services**: Always raise domain-specific exceptions with context:
```python
from app.core.exceptions import NotFoundError, ConflictError

if not resource:
    raise NotFoundError(
        resource="Horse breed",
        identifier=breed_id,
        details={"operation": "update"}
    )

if existing_resource:
    raise ConflictError(
        message=f"Resource with name '{name}' already exists",
        conflicting_field="name",
        details={"existing_id": existing_resource.id}
    )
```

**Never Return HTTP Responses from Services**: Services should raise exceptions, not return HTTP responses. Global error handlers convert exceptions to appropriate HTTP responses.

## Exception Context

**Always provide context** when raising exceptions:
- `resource`: Type of resource ("Horse breed", "User", etc.)
- `identifier`: ID or unique identifier
- `details`: Additional context as dictionary
- `operation`: What operation was being performed

**Database Errors**: Wrap SQLAlchemy exceptions:
```python
try:
    self.db.commit()
except SQLAlchemyError as e:
    self.db.rollback()
    raise DatabaseError(
        message="Failed to create resource",
        operation="create_breed",
        details={"breed_name": breed_data.name, "error": str(e)}
    )
```

## Error Response Format

Global error handlers in `app/core/error_handlers.py` ensure consistent error response format:
```json
{
    "error": {
        "type": "NotFoundError",
        "message": "Horse breed with ID 123 not found",
        "details": {
            "resource": "Horse breed",
            "identifier": 123
        }
    }
}
```
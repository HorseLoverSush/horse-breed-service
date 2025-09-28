---
applyTo: "app/services/**/*.py"
---

# Service Layer Instructions

## Business Logic Patterns

All business logic must reside in service classes. Services are the only layer that should:
- Handle database transactions (commit/rollback)
- Raise domain-specific exceptions (NotFoundError, ConflictError, etc.)
- Contain business validation logic
- Log business events using `log_business_event()`

## Required Patterns

**Constructor Pattern**: Always initialize with database session and logger:
```python
def __init__(self, db: Session):
    self.db = db
    self.logger = get_logger("service.service_name")
```

**Performance Monitoring**: Use `@log_performance` decorator on methods that may be slow:
```python
@log_performance("operation_name", threshold_ms=500.0)
def my_operation(self):
    # Implementation
```

**Error Handling**: Always raise domain exceptions, never return HTTP responses:
```python
if not resource:
    raise NotFoundError(resource="Resource Type", identifier=resource_id)
```

**Soft Deletes**: Use `is_active=False` pattern instead of hard deletes:
```python
db_record.is_active = False
self.db.commit()
```

**Business Events**: Log significant business operations:
```python
log_business_event(
    self.logger,
    "resource_created",
    {"resource_id": resource.id, "resource_name": resource.name}
)
```

## Database Transaction Management

Services handle all transaction management. Always commit after successful operations and rollback on exceptions:

```python
try:
    # Database operations
    self.db.commit()
except SQLAlchemyError as e:
    self.db.rollback()
    raise DatabaseError(message="Operation failed", operation="operation_name")
```
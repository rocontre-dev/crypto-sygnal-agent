# Domain Exceptions

This folder contains custom exception classes for domain-specific errors.

## Purpose

Domain exceptions represent business rule violations and domain-level error conditions. They provide clear, meaningful error messages that help identify what went wrong and why.

## What Goes Here

- `DomainError` - Base exception for all domain errors
- `ValidationError` - Business rule validation failures
- `NotFoundError` - Resource not found errors
- `ConflictError` - Conflicting state errors
- `UnauthorizedError` - Authorization failures
- Any other domain-specific exceptions

## Example Structure

```python
# exceptions/domain_error.py
class DomainError(Exception):
    """Base exception for domain errors."""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or "domain_error"
        super().__init__(self.message)

# exceptions/validation_error.py
class ValidationError(DomainError):
    """Raised when business rule validation fails."""
    def __init__(self, message: str, field: str = None):
        super().__init__(message, "validation_error")
        self.field = field

# exceptions/not_found_error.py
class NotFoundError(DomainError):
    """Raised when a resource is not found."""
    def __init__(self, resource_type: str, resource_id: any):
        message = f"{resource_type} with id {resource_id} not found"
        super().__init__(message, "not_found")
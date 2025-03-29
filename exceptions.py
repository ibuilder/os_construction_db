class OSConstructionError(Exception):
    """Base exception for OSConstruction operations."""
    pass


class DatabaseConnectionError(OSConstructionError):
    """Raised when there's an issue connecting to the database."""
    pass


class ResourceNotFoundError(OSConstructionError):
    """Raised when a requested resource is not found."""
    pass


class ValidationError(OSConstructionError):
    """Raised when input data fails validation."""
    pass


class AuthenticationError(OSConstructionError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(OSConstructionError):
    """Raised when a user is not authorized to perform an action."""
    pass


class DatabaseError(OSConstructionError):
    """Raised when a database operation fails."""
    pass
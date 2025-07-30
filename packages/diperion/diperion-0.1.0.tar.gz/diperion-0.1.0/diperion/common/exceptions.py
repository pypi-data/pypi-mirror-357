"""
Diperion SDK Exceptions

Clean, developer-friendly exceptions for the Diperion Semantic Engine.
"""


class DiperionError(Exception):
    """Base exception for all Diperion SDK errors."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ConnectionError(DiperionError):
    """Raised when unable to connect to the Diperion server."""
    
    def __init__(self, message: str = "Unable to connect to Diperion server"):
        super().__init__(message, "CONNECTION_ERROR")


class AuthenticationError(DiperionError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTH_ERROR")


class BusinessNotFoundError(DiperionError):
    """Raised when a business is not found."""
    
    def __init__(self, business_id: str):
        message = f"Business '{business_id}' not found"
        super().__init__(message, "BUSINESS_NOT_FOUND")
        self.business_id = business_id


class NodeNotFoundError(DiperionError):
    """Raised when a node is not found."""
    
    def __init__(self, node_id: str):
        message = f"Node '{node_id}' not found"
        super().__init__(message, "NODE_NOT_FOUND")
        self.node_id = node_id


class InvalidQueryError(DiperionError):
    """Raised when a DSL query is invalid."""
    
    def __init__(self, query: str, reason: str = None):
        message = f"Invalid query: {query}"
        if reason:
            message += f" - {reason}"
        super().__init__(message, "INVALID_QUERY")
        self.query = query
        self.reason = reason


class ValidationError(DiperionError):
    """Raised when input validation fails."""
    
    def __init__(self, field: str, message: str):
        full_message = f"Validation error in '{field}': {message}"
        super().__init__(full_message, "VALIDATION_ERROR")
        self.field = field


class ServerError(DiperionError):
    """Raised when the server returns an error."""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message, "SERVER_ERROR")
        self.status_code = status_code 
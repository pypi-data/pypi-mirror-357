"""
Custom exceptions for The Odds API SDK.
"""


class OddsAPIError(Exception):
    """Base exception for all Odds API errors."""
    
    def __init__(self, message: str, status_code: int = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class OddsAPIAuthError(OddsAPIError):
    """Raised when authentication fails (invalid API key)."""
    
    def __init__(self, message: str = "Invalid API key") -> None:
        super().__init__(message, status_code=401)


class OddsAPIUsageLimitError(OddsAPIError):
    """Raised when API usage limit is exceeded."""
    
    def __init__(self, message: str = "API usage limit exceeded") -> None:
        super().__init__(message, status_code=401)


class OddsAPIValidationError(OddsAPIError):
    """Raised when one or more query parameters are invalid."""
    
    def __init__(self, message: str = "Invalid query parameters") -> None:
        super().__init__(message, status_code=422)


class OddsAPIRateLimitError(OddsAPIError):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message, status_code=429)


class OddsAPINotFoundError(OddsAPIError):
    """Raised when requested resource is not found."""
    
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class OddsAPIServerError(OddsAPIError):
    """Raised when server returns 5xx error."""
    
    def __init__(self, message: str = "Server error") -> None:
        super().__init__(message, status_code=500) 
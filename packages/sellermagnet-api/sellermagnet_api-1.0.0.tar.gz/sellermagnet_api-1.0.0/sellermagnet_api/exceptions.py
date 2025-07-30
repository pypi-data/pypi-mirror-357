class SellerMagnetException(Exception):
    """Base exception class for SellerMagnet API client errors."""
    pass

class AuthenticationError(SellerMagnetException):
    """Raised when authentication fails (e.g., invalid API key or insufficient credits)."""
    pass

class InvalidParameterError(SellerMagnetException):
    """Raised when required parameters are missing or invalid."""
    pass

class APIError(SellerMagnetException):
    """Raised for general API errors."""
    pass
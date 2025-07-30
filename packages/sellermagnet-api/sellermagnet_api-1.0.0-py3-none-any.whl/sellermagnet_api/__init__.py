from .client import SellerMagnetClient
from .exceptions import SellerMagnetException, AuthenticationError, InvalidParameterError, APIError

__version__ = "1.0.0"
__all__ = [
    "SellerMagnetClient",
    "SellerMagnetException",
    "AuthenticationError",
    "InvalidParameterError",
    "APIError",
]
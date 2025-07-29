"""
Custom exceptions for the Player2 API client.
"""


class Player2Error(Exception):
     
    pass


class Player2AuthError(Player2Error):
    """Raised when authentication is required or failed."""
    pass


class Player2RateLimitError(Player2Error):
    """Raised when rate limit is exceeded."""
    pass


class Player2NotFoundError(Player2Error):
    """Raised when a resource is not found."""
    pass


class Player2ConflictError(Player2Error):
    """Raised when there's a conflict (e.g., STT already started)."""
    pass


class Player2ServiceUnavailableError(Player2Error):
    """Raised when a service is unavailable."""
    pass


class Player2ValidationError(Player2Error):
    """Raised when request validation fails."""
    pass 
class InvalidTokenError(ValueError):
    """Raised when the API token is missing or invalid."""
    pass

class NotFoundError(Exception):
    """Raised when the requested information isn't found."""
    pass
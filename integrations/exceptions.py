class APIIntegrationError(Exception):
    """Base exception for all external API integrations."""
    pass


class RateLimitError(APIIntegrationError):
    """Raised when an external API returns a rate limit (429) status code."""
    pass


class QuotaExceededError(APIIntegrationError):
    """Raised when an external API quota/budget has been exhausted."""
    pass


class APIConnectionError(APIIntegrationError):
    """Raised when connection to an external API fails (timeout or network error)."""
    pass

"""Custom exceptions for Hotspot."""


class HotspotError(Exception):
    """Base exception for all Hotspot errors."""

    pass


class ValidationError(HotspotError):
    """Raised when input validation fails."""

    pass


class DataError(HotspotError):
    """Raised when data processing encounters errors."""

    pass


class QueryError(HotspotError):
    """Raised when query parameters are invalid."""

    pass


class ConfigurationError(HotspotError):
    """Raised when configuration is invalid."""

    pass

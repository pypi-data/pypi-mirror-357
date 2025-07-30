"""Custom exceptions for routina."""


class RoutinaError(Exception):
    """Base exception for all routina errors."""
    pass


class StorageError(RoutinaError):
    """Raised when there's an issue with storage operations."""
    pass


class ScheduleError(RoutinaError):
    """Raised when there's an issue with schedule configuration."""
    pass


class ExecutionError(RoutinaError):
    """Raised when there's an issue executing a scheduled function."""
    pass


class TimeoutError(ExecutionError):
    """Raised when a function execution times out."""
    pass


class RetryExhaustedError(ExecutionError):
    """Raised when all retry attempts have been exhausted."""
    pass 
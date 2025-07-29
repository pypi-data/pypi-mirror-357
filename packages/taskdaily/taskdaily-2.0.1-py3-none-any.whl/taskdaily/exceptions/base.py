"""Exceptions for TaskDaily."""


class TaskDailyError(Exception):
    """Base exception for TaskDaily."""

    pass


class ConfigError(TaskDailyError):
    """Configuration related errors."""

    pass


class StorageError(TaskDailyError):
    """Storage related errors."""

    pass


class FormatterError(TaskDailyError):
    """Formatter related errors."""

    pass


class ValidationError(TaskDailyError):
    """Validation related errors."""

    pass

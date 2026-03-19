"""
Custom application exceptions.
"""


class AppError(Exception):
    """Base exception for all application errors."""
    pass


class ConfigurationError(AppError):
    """Configuration is missing or invalid."""
    pass


class LLMServiceError(AppError):
    """LLM service returned an error."""
    pass

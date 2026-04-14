"""
Dependency Injection container.

Wires all dependencies together according to the configuration.
All modules are instantiated here and injected where needed.

This makes it easy to:
- Swap implementations for testing
- Change configuration in one place
- Understand how components depend on each other
"""

from typing import TYPE_CHECKING, Any, Optional
from fastapi import FastAPI

from .config.settings import Settings, get_settings
from .domain.chat import ChatProvider
from .repositories.entry_repository import EntryRepository
from .api.server import create_app

if TYPE_CHECKING:
    import gradio as gr


def get_settings_cached() -> Settings:
    """Get cached settings instance."""
    return get_settings()


def get_chat_provider(settings=None):
    """
    Get configured chat provider.

    Args:
        settings: Optional settings (uses cached if not provided)

    Returns:
        Configured chat provider instance
    """
    settings = settings or get_settings_cached()
    if not settings.api_key:
        return None
    from .providers.openai_compat import OpenAICompatProvider

    return OpenAICompatProvider(settings)


def get_entry_repository(settings=None):
    """Get repository for travel entries."""

    settings = settings or get_settings_cached()
    return EntryRepository(settings)


def get_fastapi_app(settings=None):
    """
    Get configured FastAPI application.

    Args:
        settings: Optional settings (uses cached if not provided)

    Returns:
        Configured FastAPI app
    """
    settings = settings or get_settings_cached()
    provider = get_chat_provider(settings)
    entry_repository = get_entry_repository(settings)
    return create_app(provider, settings, entry_repository)


def get_gradio_app(settings=None):
    """
    Get configured Gradio application.

    Args:
        settings: Optional settings (uses cached if not provided)

    Returns:
        Configured Gradio app
    """
    import gradio as gr  # noqa: F401
    from .ui.gradio_app import create_gradio_app

    settings = settings or get_settings_cached()
    provider = get_chat_provider(settings)
    return create_gradio_app(provider, settings)


# Aliases for convenience
get_app = get_fastapi_app

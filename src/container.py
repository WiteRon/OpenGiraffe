"""
Dependency Injection container.

Wires all dependencies together according to the configuration.
All modules are instantiated here and injected where needed.

This makes it easy to:
- Swap implementations for testing
- Change configuration in one place
- Understand how components depend on each other
"""

from fastapi import FastAPI
import gradio as gr

from .config.settings import Settings, get_settings
from .domain.chat import ChatProvider
from .providers.openai_compat import OpenAICompatProvider
from .api.server import create_app
from .ui.gradio_app import create_gradio_app


def get_settings_cached() -> Settings:
    """Get cached settings instance."""
    return get_settings()


def get_chat_provider(settings: Settings | None = None) -> ChatProvider:
    """
    Get configured chat provider.

    Args:
        settings: Optional settings (uses cached if not provided)

    Returns:
        Configured chat provider instance
    """
    settings = settings or get_settings_cached()
    return OpenAICompatProvider(settings)


def get_fastapi_app(settings: Settings | None = None) -> FastAPI:
    """
    Get configured FastAPI application.

    Args:
        settings: Optional settings (uses cached if not provided)

    Returns:
        Configured FastAPI app
    """
    settings = settings or get_settings_cached()
    provider = get_chat_provider(settings)
    return create_app(provider, settings)


def get_gradio_app(settings: Settings | None = None) -> gr.Blocks:
    """
    Get configured Gradio application.

    Args:
        settings: Optional settings (uses cached if not provided)

    Returns:
        Configured Gradio app
    """
    settings = settings or get_settings_cached()
    provider = get_chat_provider(settings)
    return create_gradio_app(provider, settings)


# Aliases for convenience
get_app = get_fastapi_app

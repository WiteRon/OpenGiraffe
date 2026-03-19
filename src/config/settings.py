"""
Centralized application configuration.
Uses Pydantic Settings to load from environment variables/.env file.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    """

    # LLM API configuration
    api_key: str
    base_url: str = "https://ark.cn-beijing.volces.com/api/coding/v3"
    model: str = "minimax-m2.5"

    # Server configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    ui_host: str = "0.0.0.0"
    ui_port: int = 7860

    # CORS configuration
    cors_allow_origins: list[str] = ["*"]

    # Default generation parameters
    default_temperature: float = 0.7
    default_max_tokens: int = 2000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="",
    )


# Cached settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings object.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

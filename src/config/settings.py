"""
Centralized application configuration.
Loads values from environment variables and a local .env file without extra packages.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import os


def _load_env_file(env_path):
    """Load simple KEY=VALUE pairs from a .env file."""

    values = {}  # type: Dict[str, str]
    if not env_path.exists():
        return values

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _get_setting(
    key,
    env_values,
    default=None,
    required=False,
):
    """Read a setting with environment variables taking precedence over .env values."""

    if key in os.environ:
        return os.environ[key]
    if key in env_values:
        return env_values[key]
    if required:
        raise ValueError(f"Missing required setting: {key}")
    return default


@dataclass
class Settings:
    """Application settings loaded from environment variables or .env file."""

    api_key: Optional[str] = None
    base_url: str = "https://ark.cn-beijing.volces.com/api/coding/v3"
    model: str = "minimax-m2.5"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    ui_host: str = "0.0.0.0"
    ui_port: int = 7860

    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = ""
    db_password: str = ""
    db_name: str = ""

    geocode_provider: str = "opencage"
    geocode_api_key: Optional[str] = None
    geocode_timeout: float = 8.0

    cors_allow_origins: Optional[List[str]] = None

    default_temperature: float = 0.7
    default_max_tokens: int = 2000

    def __post_init__(self):
        if self.cors_allow_origins is None:
            self.cors_allow_origins = ["*"]


# Cached settings instance
_settings = None  # type: Optional[Settings]


def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings object.
    """
    global _settings
    if _settings is None:
        env_values = _load_env_file(Path(".env"))
        cors_value = _get_setting("CORS_ALLOW_ORIGINS", env_values, default="*") or "*"

        _settings = Settings(
            api_key=_get_setting("API_KEY", env_values, default=None),
            base_url=_get_setting("BASE_URL", env_values, default="https://ark.cn-beijing.volces.com/api/coding/v3") or "https://ark.cn-beijing.volces.com/api/coding/v3",
            model=_get_setting("MODEL", env_values, default="minimax-m2.5") or "minimax-m2.5",
            api_host=_get_setting("API_HOST", env_values, default="0.0.0.0") or "0.0.0.0",
            api_port=int(_get_setting("API_PORT", env_values, default="8000") or "8000"),
            ui_host=_get_setting("UI_HOST", env_values, default="0.0.0.0") or "0.0.0.0",
            ui_port=int(_get_setting("UI_PORT", env_values, default="7860") or "7860"),
            db_host=_get_setting("DB_HOST", env_values, default="127.0.0.1") or "127.0.0.1",
            db_port=int(_get_setting("DB_PORT", env_values, default="3306") or "3306"),
            db_user=_get_setting("DB_USER", env_values, default="", required=True) or "",
            db_password=_get_setting("DB_PASSWORD", env_values, default="", required=True) or "",
            db_name=_get_setting("DB_NAME", env_values, default="", required=True) or "",
            geocode_provider=_get_setting("GEOCODE_PROVIDER", env_values, default="opencage") or "opencage",
            geocode_api_key=_get_setting("GEOCODE_API_KEY", env_values, default=None),
            geocode_timeout=float(_get_setting("GEOCODE_TIMEOUT", env_values, default="8.0") or "8.0"),
            cors_allow_origins=[item.strip() for item in cors_value.split(",") if item.strip()],
            default_temperature=float(_get_setting("DEFAULT_TEMPERATURE", env_values, default="0.7") or "0.7"),
            default_max_tokens=int(_get_setting("DEFAULT_MAX_TOKENS", env_values, default="2000") or "2000"),
        )
    return _settings

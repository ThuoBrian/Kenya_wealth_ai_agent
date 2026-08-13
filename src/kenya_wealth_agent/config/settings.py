"""Application settings using pydantic-settings.

Configuration priority (highest to lowest):
1. Environment variables
2. ``.env`` file
3. ``config.ini`` file
4. Defaults defined here

Environment variables are prefixed with ``KWA_`` (e.g. ``KWA_MODEL``).
"""

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from kenya_wealth_agent.config.constants import AVAILABLE_MODELS

DEFAULT_CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "config.ini"


class Settings(BaseSettings):
    """Runtime settings for Kenya Wealth Agent."""

    model_config = SettingsConfigDict(
        env_prefix="KWA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ollama
    model: str = Field(default="nemotron-3-super:cloud")
    base_url: str = Field(default="http://localhost:11434")

    # Agent
    developer_name: str = Field(default="Brian Thuo")
    version: str = Field(default="1.0.0")

    # Output
    output_dir: str = Field(default="output")
    report_filename: str = Field(default="kenya_wealth_advice.html")

    # Web
    cors_origins: str = Field(default="http://localhost:8000,http://127.0.0.1:8000")
    max_message_length: int = Field(default=4_000, ge=100)
    request_timeout: float = Field(default=60.0, gt=0)

    # Feature flags
    enable_streaming: bool = Field(default=True)
    enable_rate_limiting: bool = Field(default=True)

    # Logging
    log_level: str = Field(default="INFO")
    structured_logs: bool = Field(default=True)

    @field_validator("model")
    @classmethod
    def _resolve_model_alias(cls, value: str) -> str:
        """Allow config files and env vars to use short aliases like 'glm'."""
        return AVAILABLE_MODELS.get(value.lower(), value)

    @field_validator("log_level")
    @classmethod
    def _validate_log_level(cls, value: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = value.upper()
        if upper not in allowed:
            raise ValueError(f"log_level must be one of {allowed}, got {value!r}")
        return upper

    @property
    def cors_origin_list(self) -> list[str]:
        """Return CORS origins as a list of strings."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


def load_settings_from_config_ini(config_path: str | Path | None = None) -> dict[str, Any]:
    """Load values from ``config.ini`` in a pydantic-settings-friendly dict.

    Args:
        config_path: Optional path to a config.ini file.  Defaults to the
            repository-root ``config.ini``.

    Returns:
        Dictionary of settings extracted from the file.
    """
    import configparser

    path = Path(config_path) if config_path else DEFAULT_CONFIG_FILE
    if not path.exists():
        return {}

    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")

    mapping: dict[str, Any] = {}
    if parser.has_section("ollama"):
        mapping["model"] = parser.get("ollama", "model", fallback=None)
        mapping["base_url"] = parser.get("ollama", "base_url", fallback=None)
    if parser.has_section("agent"):
        mapping["developer_name"] = parser.get("agent", "developer_name", fallback=None)
        mapping["version"] = parser.get("agent", "version", fallback=None)
    if parser.has_section("output"):
        mapping["output_dir"] = parser.get("output", "output_dir", fallback=None)
        mapping["report_filename"] = parser.get("output", "report_filename", fallback=None)

    return {k: v for k, v in mapping.items() if v is not None}


@lru_cache(maxsize=1)
def get_settings(config_path: str | Path | None = None) -> Settings:
    """Return a cached ``Settings`` instance.

    Values from ``config.ini`` are merged with environment variables and
    defaults.  Environment variables take precedence.

    Args:
        config_path: Optional path to a config.ini file.

    Returns:
        A fully resolved ``Settings`` object.
    """
    file_values = load_settings_from_config_ini(config_path)
    return Settings(**file_values)


def reload_settings(config_path: str | Path | None = None) -> Settings:
    """Reload settings, clearing the cache.

    Args:
        config_path: Optional path to a config.ini file.

    Returns:
        A freshly resolved ``Settings`` object.
    """
    get_settings.cache_clear()
    return get_settings(config_path)

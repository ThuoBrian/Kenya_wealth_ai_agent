"""
Configuration loader for Kenya Wealth Agent.

Reads settings from config.ini file and environment variables.
"""

import os
import configparser
from pathlib import Path
from typing import Optional

# Path to config file (same directory as this module)
CONFIG_FILE = Path(__file__).parent.parent / "config.ini"


class Config:
    """Configuration settings for Kenya Wealth Agent."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file and environment.

        Args:
            config_path: Optional path to config file (default: config.ini)
        """
        self._config = configparser.ConfigParser()

        # Load from file if it exists
        config_file = Path(config_path) if config_path else CONFIG_FILE
        if config_file.exists():
            self._config.read(config_file)

        # Set defaults
        self._defaults = {
            "ollama": {
                "model": "nemotron-3-super:cloud",
                "base_url": "http://localhost:11434",
            },
            "agent": {
                "developer_name": "Brian Thuo",
                "version": "1.0.0",
            },
            "output": {
                "output_dir": "output",
                "report_filename": "kenya_wealth_advice.html",
            },
            "display": {
                "enable_colors": "true",
                "show_timestamps": "true",
            },
        }

    def _get(self, section: str, key: str) -> str:
        """Get a config value with fallback to defaults and environment.

        Priority: Environment variable > config file > default
        """
        env_key = f"{section.upper()}_{key.upper()}"

        # Check environment variable first
        env_value = os.environ.get(env_key)
        if env_value:
            return env_value

        # Check config file
        try:
            if self._config.has_option(section, key):
                return self._config.get(section, key)
        except configparser.Error:
            pass

        # Return default
        return self._defaults.get(section, {}).get(key, "")

    def _get_bool(self, section: str, key: str) -> bool:
        """Get a boolean config value."""
        value = self._get(section, key).lower()
        return value in ("true", "yes", "1", "on")

    # Ollama settings
    @property
    def model(self) -> str:
        """The Ollama model to use."""
        return self._get("ollama", "model")

    @property
    def base_url(self) -> str:
        """The Ollama server URL."""
        return self._get("ollama", "base_url")

    # Agent settings
    @property
    def developer_name(self) -> str:
        """Developer name shown in reports."""
        return self._get("agent", "developer_name")

    @property
    def version(self) -> str:
        """Application version."""
        return self._get("agent", "version")

    # Output settings
    @property
    def output_dir(self) -> str:
        """Directory for generated reports."""
        return self._get("output", "output_dir")

    @property
    def report_filename(self) -> str:
        """Default report filename."""
        return self._get("output", "report_filename")

    # Display settings
    @property
    def enable_colors(self) -> bool:
        """Whether to enable colored output."""
        return self._get_bool("display", "enable_colors")

    @property
    def show_timestamps(self) -> bool:
        """Whether to show timestamps in conversation."""
        return self._get_bool("display", "show_timestamps")

    def __repr__(self) -> str:
        """Return a string representation of the config."""
        return (
            f"Config(model={self.model!r}, base_url={self.base_url!r}, "
            f"developer={self.developer_name!r})"
        )


# Global config instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get the global configuration instance.

    Args:
        config_path: Optional path to config file (only used on first call)

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def reload_config(config_path: Optional[str] = None) -> Config:
    """Reload configuration from file.

    Args:
        config_path: Optional path to config file

    Returns:
        New Config instance
    """
    global _config
    _config = Config(config_path)
    return _config


# Available models for reference
AVAILABLE_MODELS = {
    "nemotron": "nemotron-3-super:cloud",
    "llama3": "llama3.1:latest",
    "llama3.1": "llama3.1:latest",
    "mistral": "mistral:latest",
    "qwen": "qwen2.5:latest",
    "qwen2.5": "qwen2.5:latest",
    "glm": "glm-5:cloud",
    "glm-5": "glm-5:cloud",
}


def list_available_models() -> None:
    """Print available models."""
    print("\nAvailable models you can use in config.ini:\n")
    print(f"{'Alias':<15} {'Model Name':<30}")
    print("-" * 45)
    for alias, model in AVAILABLE_MODELS.items():
        print(f"{alias:<15} {model:<30}")
    print()


if __name__ == "__main__":
    # Test the configuration
    config = get_config()
    print(f"Configuration loaded from: {CONFIG_FILE}")
    print(f"  Model: {config.model}")
    print(f"  Base URL: {config.base_url}")
    print(f"  Developer: {config.developer_name}")
    print(f"  Version: {config.version}")
    print(f"  Output Dir: {config.output_dir}")
    list_available_models()
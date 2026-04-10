"""
Configuration loader for Kenya Wealth Agent.

This module handles loading configuration from config.ini file
and environment variables.
"""

import os
import configparser
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class OllamaConfig:
    """Ollama server configuration."""
    model: str = "nemotron-3-super:cloud"
    base_url: str = "http://localhost:11434"


@dataclass
class AgentConfig:
    """Agent configuration."""
    developer_name: str = "Brian Thuo"
    version: str = "1.0.0"


@dataclass
class OutputConfig:
    """Output configuration."""
    output_dir: str = "output"
    report_filename: str = "kenya_wealth_advice.html"


@dataclass
class DisplayConfig:
    """Display configuration."""
    enable_colors: bool = True
    show_timestamps: bool = True


class Config:
    """Configuration manager for Kenya Wealth Agent.

    Loads configuration from:
    1. config.ini file (lowest priority)
    2. Environment variables (medium priority)
    3. Command-line arguments (highest priority - not implemented yet)

    Example usage:
        config = Config.load()
        print(config.ollama.model)
        print(config.agent.developer_name)
    """

    def __init__(
        self,
        ollama: OllamaConfig = None,
        agent: AgentConfig = None,
        output: OutputConfig = None,
        display: DisplayConfig = None,
    ):
        self.ollama = ollama or OllamaConfig()
        self.agent = agent or AgentConfig()
        self.output = output or OutputConfig()
        self.display = display or DisplayConfig()

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from file and environment variables.

        Args:
            config_path: Path to config.ini file (default: looks in same directory as this file)

        Returns:
            Config object with loaded settings
        """
        if config_path is None:
            config_path = cls._find_config_file()

        # Start with defaults
        ollama = OllamaConfig()
        agent = AgentConfig()
        output = OutputConfig()
        display = DisplayConfig()

        # Load from config.ini if it exists
        if config_path and os.path.exists(config_path):
            parser = configparser.ConfigParser()
            parser.read(config_path)

            # Ollama settings
            if 'ollama' in parser:
                ollama.model = parser.get('ollama', 'model', fallback=ollama.model)
                ollama.base_url = parser.get('ollama', 'base_url', fallback=ollama.base_url)

            # Agent settings
            if 'agent' in parser:
                agent.developer_name = parser.get('agent', 'developer_name', fallback=agent.developer_name)
                agent.version = parser.get('agent', 'version', fallback=agent.version)

            # Output settings
            if 'output' in parser:
                output.output_dir = parser.get('output', 'output_dir', fallback=output.output_dir)
                output.report_filename = parser.get('output', 'report_filename', fallback=output.report_filename)

            # Display settings
            if 'display' in parser:
                display.enable_colors = parser.getboolean('display', 'enable_colors', fallback=display.enable_colors)
                display.show_timestamps = parser.getboolean('display', 'show_timestamps', fallback=display.show_timestamps)

        # Override with environment variables (higher priority)
        ollama.model = os.environ.get("OLLAMA_MODEL", ollama.model)
        ollama.base_url = os.environ.get("OLLAMA_BASE_URL", ollama.base_url)

        return cls(ollama=ollama, agent=agent, output=output, display=display)

    @staticmethod
    def _find_config_file() -> Optional[str]:
        """Find the config.ini file.

        Looks in:
        1. Current working directory
        2. Same directory as this module
        3. Parent directory of this module

        Returns:
            Path to config.ini or None if not found
        """
        # Check common locations
        locations = [
            os.getcwd(),  # Current working directory
            Path(__file__).parent.parent,  # Package root (parent of config/)
            Path(__file__).parent,  # config/ directory
        ]

        for location in locations:
            config_file = os.path.join(location, "config.ini")
            if os.path.exists(config_file):
                return config_file

        return None

    def get_report_path(self) -> str:
        """Get the full path for the HTML report.

        Returns:
            Full path to the report file
        """
        return os.path.join(self.output.output_dir, self.output.report_filename)

    def __repr__(self) -> str:
        return (
            f"Config(\n"
            f"  ollama=OllamaConfig(model='{self.ollama.model}', base_url='{self.ollama.base_url}'),\n"
            f"  agent=AgentConfig(developer_name='{self.agent.developer_name}', version='{self.agent.version}'),\n"
            f"  output=OutputConfig(output_dir='{self.output.output_dir}', report_filename='{self.output.report_filename}'),\n"
            f"  display=DisplayConfig(enable_colors={self.display.enable_colors}, show_timestamps={self.display.show_timestamps})\n"
            f")"
        )


# Global config instance (lazy loaded)
_config: Optional[Config] = None


def get_config(reload: bool = False) -> Config:
    """Get the global configuration instance.

    Args:
        reload: Force reload configuration from file

    Returns:
        Config object
    """
    global _config
    if _config is None or reload:
        _config = Config.load()
    return _config


def reload_config() -> Config:
    """Reload configuration from file.

    Returns:
        New Config object
    """
    return get_config(reload=True)
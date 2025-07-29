"""
Application configuration management for ZScheduler
"""

import os
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class AppConfig:
    """
    Manages application configuration and settings.

    Handles loading and saving settings from/to a JSON file.
    Provides defaults for settings that aren't specified.
    """

    # Default configuration values
    DEFAULT_CONFIG = {
        "ui": {
            "theme": "dark",  # 'dark' or 'light'
            "default_view": "list",  # 'list', 'calendar', 'timeline', etc.
            "refresh_interval": 1000,  # milliseconds
            "confirm_delete": True,
            "show_toolbar": True,
            "show_statusbar": True,
            "minimize_to_tray": True,
            "minimize_on_close": False
        },
        "window": {
            "width": 1200,
            "height": 800,
            "x": None,
            "y": None,
            "maximized": False
        },
        "ui.theme.dark_colors": {
            "background": "#0a192f",  # Deep blue
            "text": "#f1fa8c",        # Neon yellow
            "accent": "#50fa7b",      # Light green
            "success": "#50fa7b",     # Light green
            "warning": "#ffb86c",     # Orange
            "error": "#ff5555",       # Red
            "info": "#8be9fd"         # Cyan
        },
        "ui.theme.light_colors": {
            "background": "#e0f2e9",  # Light green
            "text": "#0a192f",        # Dark blue
            "accent": "#1a365d",      # Deeper blue
            "success": "#38a169",     # Green
            "warning": "#dd6b20",     # Orange
            "error": "#e53e3e",       # Red
            "info": "#3182ce"         # Blue
        },
        "scheduler": {
            "auto_start": True
        }
    }

    def __init__(self, config_path: str):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> None:
        """Load configuration from file, or use defaults if file doesn't exist."""
        if not os.path.exists(self.config_path):
            logger.info("No configuration file found at " + str(self.config_path) + ", using defaults")
            return

        try:
            with open(self.config_path, 'r') as f:
                stored_config = json.load(f)

            # Update default config with stored values (keeping defaults for missing values)
            self._update_recursive(self.config, stored_config)
            logger.info("Loaded configuration from " + str(self.config_path))

        except Exception as e:
            logger.error("Error loading configuration from " + str(self.config_path) + ": " + str(e))

    def save(self) -> None:
        """Save current configuration to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)

            logger.info("Saved configuration to " + str(self.config_path))

        except Exception as e:
            logger.error("Error saving configuration to " + str(self.config_path) + ": " + str(e))

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key: Dot-separated key path (e.g., 'window.width')
            default: Default value if key is not found

        Returns:
            Configuration value or default
        """
        try:
            parts = key.split('.')
            value = self.config
            for part in parts:
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Dot-separated key path (e.g., 'window.width')
            value: Value to set
        """
        parts = key.split('.')
        target = self.config

        # Navigate to the containing dictionary
        for part in parts[:-1]:
            if part not in target or not isinstance(target[part], dict):
                target[part] = {}
            target = target[part]

        # Set the value
        target[parts[-1]] = value

    def _update_recursive(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively update a nested dictionary.

        Args:
            target: Dictionary to update
            source: Dictionary with new values
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._update_recursive(target[key], value)
            else:
                target[key] = value

    def get_theme_colors(self) -> Dict[str, str]:
        """
        Get the current theme's color palette.

        Returns:
            Dictionary of color values for the current theme
        """
        theme = self.get('theme', 'dark')
        colors_key = 'colors.' + theme
        return self.get(colors_key, {})

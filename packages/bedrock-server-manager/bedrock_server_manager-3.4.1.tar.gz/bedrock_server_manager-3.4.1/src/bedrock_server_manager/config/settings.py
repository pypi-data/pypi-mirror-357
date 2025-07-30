# bedrock_server_manager/config/settings.py
"""Manages application-wide configuration settings.

This module provides the `Settings` class, which is responsible for loading
settings from a JSON file, providing default values for missing keys, saving
changes back to the file, and determining the appropriate application data and
configuration directories based on the environment.
"""

import os
import json
from typing import Any
import logging
from bedrock_server_manager.error import ConfigurationError
from bedrock_server_manager.config.const import (
    package_name,
    env_name,
    get_installed_version,
)


logger = logging.getLogger(__name__)


class Settings:
    """Manages loading, accessing, and saving application settings.

    This class acts as a single source of truth for configuration. It handles
    the logic for determining application data and config directories, provides
    sensible defaults, and ensures critical directories exist. It offers simple
    `get` and `set` methods for interacting with the configuration values,
    persisting any changes to a JSON file.
    """

    def __init__(self):
        """Initializes the Settings object.

        This constructor determines the application's file paths, loads any
        existing configuration from `script_config.json`, creates a default
        configuration if one doesn't exist, and ensures all necessary
        directories are present on the filesystem.
        """
        logger.debug("Initializing Settings")
        # Determine the primary application data and config directories.
        self._app_data_dir_path = self._determine_app_data_dir()
        self._config_dir_path = self._determine_app_config_dir()
        self.config_file_name = "script_config.json"
        self.config_path = os.path.join(self._config_dir_path, self.config_file_name)

        # Get the installed package version.
        self._version_val = get_installed_version()

        # Load settings from the config file or create a default one.
        self._settings = {}
        self.load()

    def _determine_app_data_dir(self) -> str:
        """Determines the main application data directory.

        It prioritizes the `BSM_DATA_DIR` environment variable if set.
        Otherwise, it defaults to a 'bedrock-server-manager' directory in the
        user's home folder. The directory is created if it doesn't exist.

        Returns:
            The absolute path to the application data directory.
        """
        env_var_name = f"{env_name}_DATA_DIR"
        data_dir = os.environ.get(env_var_name)
        if not data_dir:
            data_dir = os.path.join(os.path.expanduser("~"), f"{package_name}")
        os.makedirs(data_dir, exist_ok=True)
        return data_dir

    def _determine_app_config_dir(self) -> str:
        """Determines the application's configuration directory.

        This directory is typically named `.config` and is nested within the main
        application data directory. It is created if it doesn't exist.

        Returns:
            The absolute path to the application configuration directory.
        """
        config_dir = os.path.join(self._app_data_dir_path, ".config")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir

    @property
    def default_config(self) -> dict:
        """Provides the default configuration values for the application.

        These defaults are used when a configuration file is not found or a
        specific setting is missing. Paths are constructed dynamically based on
        the determined application data directory.

        Returns:
            A dictionary of default settings.
        """
        app_data_dir_val = self._app_data_dir_path
        return {
            "BASE_DIR": os.path.join(app_data_dir_val, "servers"),
            "CONTENT_DIR": os.path.join(app_data_dir_val, "content"),
            "DOWNLOAD_DIR": os.path.join(app_data_dir_val, ".downloads"),
            "BACKUP_DIR": os.path.join(app_data_dir_val, "backups"),
            "PLUGIN_DIR": os.path.join(app_data_dir_val, "plugins"),
            "LOG_DIR": os.path.join(app_data_dir_val, ".logs"),
            "BACKUP_KEEP": 3,
            "DOWNLOAD_KEEP": 3,
            "LOGS_KEEP": 3,
            "FILE_LOG_LEVEL": logging.INFO,
            "CLI_LOG_LEVEL": logging.WARN,
            "WEB_PORT": 11325,
            "TOKEN_EXPIRES_WEEKS": 4,
        }

    def load(self):
        """Loads settings from the JSON configuration file.

        This method starts with the default settings. If a configuration file
        exists, it loads the user's settings and merges them, with user settings
        taking precedence. If the file doesn't exist, it's created with the
        defaults.
        """
        # Always start with a fresh copy of the defaults to build upon.
        default_settings = self.default_config.copy()

        if os.path.exists(self.config_path):
            # If the file exists, try to load and merge it.
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    # Update the defaults with the user's saved settings.
                    default_settings.update(user_config)
            except (ValueError, OSError) as e:
                # If the file is corrupt or unreadable, log a warning and use defaults.
                logger.warning(
                    f"Could not load config file at {self.config_path}: {e}. "
                    "Using default settings. The corrupt file will be overwritten on the next settings change."
                )
        else:
            # If the file does not exist, create it with the default values.
            logger.info(
                f"Configuration file not found at {self.config_path}. Creating with default settings."
            )
            self._settings = default_settings
            self._write_config()

        # Set the final merged settings and ensure all necessary directories exist.
        self._settings = default_settings
        self._ensure_dirs_exist()

    def _ensure_dirs_exist(self):
        """Ensures that all critical directories specified in the settings exist.

        This method iterates through key directory paths defined in the
        configuration and creates any that are missing.

        Raises:
            ConfigurationError: If a directory cannot be created due to an
                `OSError` (e.g., permissions issue).
        """
        dirs_to_check = [
            self.get("BASE_DIR"),
            self.get("CONTENT_DIR"),
            self.get("DOWNLOAD_DIR"),
            self.get("BACKUP_DIR"),
            self.get("PLUGIN_DIR"),
            self.get("LOG_DIR"),
        ]
        for dir_path in dirs_to_check:
            if dir_path and isinstance(dir_path, str):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                except OSError as e:
                    raise ConfigurationError(
                        f"Could not create critical directory: {dir_path}"
                    ) from e

    def _write_config(self):
        """Writes the current settings dictionary to the JSON configuration file.

        Raises:
            ConfigurationError: If writing the configuration fails due to an
                `OSError` or `TypeError` (serialization issue).
        """
        try:
            os.makedirs(self._config_dir_path, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._settings, f, indent=4, sort_keys=True)
        except (OSError, TypeError) as e:
            raise ConfigurationError(f"Failed to write configuration: {e}") from e

    def get(self, key: str, default=None) -> Any:
        """Retrieves a setting value for a given key.

        Args:
            key: The configuration key to retrieve.
            default: The value to return if the key is not found.

        Returns:
            The value associated with the key, or the default value.
        """
        return self._settings.get(key, default)

    def set(self, key: str, value: Any):
        """Sets a configuration value and saves the change to the file.

        This method updates the in-memory settings dictionary and then
        immediately persists the entire configuration to the JSON file. It
        avoids writing to disk if the new value is the same as the old one.

        Args:
            key: The configuration key to set.
            value: The value to associate with the key.
        """
        if key in self._settings and self._settings[key] == value:
            return  # No change, so no need to write to the file.
        self._settings[key] = value
        logger.info(f"Setting '{key}' updated to '{value}'. Saving configuration.")
        self._write_config()

    @property
    def config_dir(self) -> str:
        """The absolute path to the application's configuration directory."""
        return self._config_dir_path

    @property
    def app_data_dir(self) -> str:
        """The absolute path to the application's main data directory."""
        return self._app_data_dir_path

    @property
    def version(self) -> str:
        """The installed version of the application package."""
        return self._version_val


# A singleton instance of the Settings class, used throughout the application.
settings = Settings()

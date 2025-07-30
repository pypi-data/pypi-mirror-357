import os
import sys
import tomllib
from functools import cache
from pathlib import Path
from typing import Any

import click

PGTUI_CONFIG_DIR_NAME = "pgtui"
SETTINGS_FILE_NAME = "settings.toml"
STYLESHEET_FILE_NAME = "styles.tcss"

Settings = dict[str, Any]


def get_settings_path() -> Path:
    return _config_dir() / PGTUI_CONFIG_DIR_NAME / SETTINGS_FILE_NAME


def load_settings() -> Settings:
    path = get_settings_path()

    if not path.exists():
        return {}

    try:
        with open(path) as f:
            return tomllib.loads(f.read())
    except Exception as exc:
        raise click.ClickException(f"Cannot load settings from '{path}': {str(exc)}")


def _config_dir() -> Path:
    """Returns the path to the system config directory"""

    # On Windows, store the config in roaming appdata
    if sys.platform == "win32" and "APPDATA" in os.environ:
        return Path(os.getenv("APPDATA"))

    # Respect XDG_CONFIG_HOME env variable if set
    # https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html
    if "XDG_CONFIG_HOME" in os.environ:
        return Path(os.environ["XDG_CONFIG_HOME"]).expanduser()

    # Default to ~/.config/
    return Path.home() / ".config"

from __future__ import annotations

"""Read configuration from ``config.ini`` and environment variables."""

import os
from pathlib import Path
import configparser

CONFIG_PATH = Path.cwd() / "config.ini"
_parser = configparser.ConfigParser()
if CONFIG_PATH.exists():
    _parser.read(CONFIG_PATH)

__all__ = ["get_log_root", "get_database_url"]

def get_log_root(default: Path) -> Path:
    """Return the folder containing log files.

    The value is resolved in this order:
    1. ``LOG_ROOT`` environment variable
    2. ``log_root`` entry under the ``[settings]`` section of ``config.ini``
    3. ``default`` argument
    """

    value = os.environ.get("LOG_ROOT") or _parser.get(
        "settings", "log_root", fallback=str(default)
    )
    return Path(value).expanduser()

def get_database_url(default: str) -> str:
    """Return the database connection URL.

    Resolution order mirrors :func:`get_log_root`.
    """

    return os.environ.get("DATABASE_URL") or _parser.get(
        "settings", "database_url", fallback=default
    )

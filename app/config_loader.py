from __future__ import annotations
import os
from pathlib import Path
import configparser

CONFIG_PATH = Path.cwd() / "config.ini"
_parser = configparser.ConfigParser()
if CONFIG_PATH.exists():
    _parser.read(CONFIG_PATH)

__all__ = ["get_log_root", "get_database_url"]

def get_log_root(default: Path) -> Path:
    value = os.environ.get("LOG_ROOT") or _parser.get("settings", "log_root", fallback=str(default))
    return Path(value).expanduser()

def get_database_url(default: str) -> str:
    return os.environ.get("DATABASE_URL") or _parser.get("settings", "database_url", fallback=default)

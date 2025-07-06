import importlib
from pathlib import Path
import sys
import os


def test_config_ini_read(monkeypatch, tmp_path):
    cfg = tmp_path / "config.ini"
    cfg.write_text(
        """[settings]\nlog_root = /tmp/logs\ndatabase_url = sqlite:///tmp/db\n"""
    )
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    loader = importlib.reload(importlib.import_module("app.config_loader"))
    assert loader.get_log_root(Path.home()) == Path("/tmp/logs")
    assert loader.get_database_url("sqlite:///default.db") == "sqlite:///tmp/db"
    os.chdir(orig_cwd)
    importlib.reload(loader)
    sys.path.remove(str(root))


def test_env_overrides_config(monkeypatch, tmp_path):
    cfg = tmp_path / "config.ini"
    cfg.write_text(
        """[settings]\nlog_root = /tmp/logs\ndatabase_url = sqlite:///tmp/db\n"""
    )
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    monkeypatch.setenv("LOG_ROOT", "/env/logs")
    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@localhost/db")
    loader = importlib.reload(importlib.import_module("app.config_loader"))
    assert loader.get_log_root(Path.home()) == Path("/env/logs")
    assert loader.get_database_url("sqlite:///default.db") == "postgres://u:p@localhost/db"
    os.chdir(orig_cwd)
    importlib.reload(loader)
    sys.path.remove(str(root))

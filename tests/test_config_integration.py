import importlib
import os
import sys
from pathlib import Path


def test_modules_use_config_ini(tmp_path):
    cfg = tmp_path / "config.ini"
    cfg.write_text(
        """[settings]\nlog_root = /tmp/config_logs\ndatabase_url = sqlite:///tmp/config.db\n"""
    )
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    loader = importlib.reload(importlib.import_module("app.config_loader"))
    main = importlib.reload(importlib.import_module("app.web.main"))
    db = importlib.reload(importlib.import_module("app.db"))
    assert main.LOG_ROOT == Path("/tmp/config_logs")
    assert db.DATABASE_URL == "sqlite:///tmp/config.db"
    os.chdir(orig_cwd)
    importlib.reload(loader)
    importlib.reload(main)
    importlib.reload(db)
    sys.path.remove(str(root))


def test_env_overrides_config_ini(monkeypatch, tmp_path):
    cfg = tmp_path / "config.ini"
    cfg.write_text(
        """[settings]\nlog_root = /tmp/config_logs\ndatabase_url = sqlite:///tmp/config.db\n"""
    )
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))
    orig_cwd = os.getcwd()
    os.chdir(tmp_path)
    monkeypatch.setenv("LOG_ROOT", "/env/logs")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///env.db")
    loader = importlib.reload(importlib.import_module("app.config_loader"))
    main = importlib.reload(importlib.import_module("app.web.main"))
    db = importlib.reload(importlib.import_module("app.db"))
    assert main.LOG_ROOT == Path("/env/logs")
    assert db.DATABASE_URL == "sqlite:///env.db"
    os.chdir(orig_cwd)
    importlib.reload(loader)
    importlib.reload(main)
    importlib.reload(db)
    sys.path.remove(str(root))


def test_database_url_uses_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///env.db")
    db = importlib.reload(importlib.import_module("app.db"))
    assert db.DATABASE_URL == "sqlite:///env.db"


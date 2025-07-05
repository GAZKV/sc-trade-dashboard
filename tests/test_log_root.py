import importlib

from pathlib import Path
from tests.test_log_parser import BUY_LINE


def test_log_collection_respects_log_root_env(tmp_path, monkeypatch):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    log_file = log_dir / "sample.log"
    log_file.write_text(BUY_LINE)

    monkeypatch.setenv("LOG_ROOT", str(log_dir))

    main = importlib.reload(importlib.import_module("app.web.main"))

    from app.log_parser import collect_files, iter_records

    files = collect_files([str(main.LOG_ROOT)])
    assert log_file in files

    records = list(iter_records(files))
    assert len(records) == 1


def test_log_root_defaults_to_home(monkeypatch):
    monkeypatch.delenv("LOG_ROOT", raising=False)

    main = importlib.reload(importlib.import_module("app.web.main"))

    expected = Path.home() / "StarCitizen" / "LIVE"
    assert main.LOG_ROOT == expected


def test_log_root_uses_env(monkeypatch, tmp_path):
    monkeypatch.setenv("LOG_ROOT", str(tmp_path))

    main = importlib.reload(importlib.import_module("app.web.main"))

    assert main.LOG_ROOT == tmp_path
    assert isinstance(main.LOG_ROOT, Path)

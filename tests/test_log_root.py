import importlib

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

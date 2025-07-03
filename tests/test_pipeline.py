"""Utility script to run the log parsing and analysis pipeline."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd

from app.log_parser import collect_files, iter_records
from app.analysis import analyse

DEFAULT_LOG_DIR = Path(__file__).parent / "logs"


def run_pipeline(log_dir: Path = DEFAULT_LOG_DIR) -> dict:
    files = collect_files([str(log_dir)])
    if not files:
        raise FileNotFoundError(f"No .log files found in {log_dir}")
    df = pd.DataFrame(iter_records(files))
    ctx = analyse(df)
    print("KPIs", ctx.get("kpi"))
    return ctx


def test_run_pipeline():
    """Run the pipeline on bundled log samples and ensure KPIs are returned."""
    ctx = run_pipeline()
    assert ctx["kpi"]["total_buys"] >= 0
    assert ctx["kpi"]["total_sells"] >= 0


if __name__ == "__main__":
    import sys
    log_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LOG_DIR
    run_pipeline(log_dir)

import subprocess
import sys
import os
from pathlib import Path


def test_generate_report_creates_excel(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "generate_report.py"
    logs = Path(__file__).parent / "logs"
    html = tmp_path / "report.html"
    xls = tmp_path / "report.xlsx"

    env = dict(**os.environ, PYTHONPATH=str(repo_root))
    subprocess.check_call([
        sys.executable,
        str(script),
        str(logs),
        str(html),
        "--excel",
        str(xls),
    ], cwd=repo_root, env=env)

    assert xls.exists()

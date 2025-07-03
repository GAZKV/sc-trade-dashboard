import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.report import render_html


def test_render_html_embeds_context(tmp_path):
    ctx = {"kpi": {"total_profit_sc": 42}, "daily_profit": {"labels": [], "values": []},
           "buy_summary": [], "sell_summary": [], "best_routes": [], "pending_goods": []}
    dst = tmp_path / "report.html"
    render_html(ctx, dst)
    html = dst.read_text()
    assert 'init-data' in html
    data_start = html.find('init-data')
    assert 'total_profit_sc' in html[data_start:]

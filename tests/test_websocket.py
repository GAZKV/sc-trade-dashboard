import asyncio
import json
from pathlib import Path
import sys
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.web import main
from app.log_parser import collect_files, iter_records
from app.analysis import analyse
from tests.test_log_parser import BUY_LINE


def test_websocket_updates_with_log(tmp_path, monkeypatch):
    log_file = tmp_path / "test.log"
    log_file.write_text("")

    monkeypatch.setattr(main, "LOG_ROOT", tmp_path)

    async def fast_watch_logs():
        while True:
            files = collect_files([str(tmp_path)])
            df = pd.DataFrame(iter_records(files))
            ctx = analyse(df)
            ctx["log_info"] = {"path": str(tmp_path), "count": len(files)}
            main._latest_ctx = ctx
            await asyncio.sleep(0.05)

    async def fast_ws_dashboard(ws):
        await ws.accept()
        try:
            while True:
                await ws.send_text(json.dumps(main._latest_ctx or {}))
                await asyncio.sleep(0.05)
        except WebSocketDisconnect:
            pass

    monkeypatch.setattr(main, "watch_logs", fast_watch_logs)
    monkeypatch.setattr(main, "ws_dashboard", fast_ws_dashboard)

    with TestClient(main.app) as client:
        with client.websocket_connect("/ws") as ws:
            data = ws.receive_json()
            assert data.get("kpi", {}).get("total_buys") == 0

            log_file.write_text(BUY_LINE + "\n")

            for _ in range(20):
                data = ws.receive_json()
                if data.get("kpi", {}).get("total_buys") == 1:
                    break
            else:
                raise AssertionError("WebSocket did not reflect log update")

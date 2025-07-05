from pathlib import Path
import os
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager, suppress
import asyncio
import pandas as pd
import json
from ..log_parser import collect_files, iter_records
from ..analysis import analyse

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

DEFAULT_LOG_ROOT = Path.home() / "StarCitizen" / "LIVE"
LOG_ROOT = Path(os.getenv("LOG_ROOT", str(DEFAULT_LOG_ROOT)))  # configurable

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(watch_logs())
    try:
        yield
    finally:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

app = FastAPI(title="SC Trade Dashboard API", lifespan=lifespan)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "static"),
    name="static",
)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

_latest_ctx: dict | None = None


async def watch_logs():
    """Background coroutine – rescans every 10 s and recalculates KPIs."""
    global _latest_ctx
    while True:
        try:
            df = pd.DataFrame(iter_records(collect_files([str(LOG_ROOT)])))
            if not df.empty:
                _latest_ctx = analyse(df)
        except Exception:
            import logging
            logging.exception("Analyse failed:")
        await asyncio.sleep(10)


@app.get("/api/metrics")
async def metrics():

    return _latest_ctx or {"status": "bootstrapping"}


@app.websocket("/ws")
async def ws_dashboard(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_text(json.dumps(_latest_ctx or {}))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

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
from pydantic import BaseModel
from ..log_parser import collect_files, iter_records
from ..analysis import analyse
from ..db import (
    init_db,
    get_all_names,
    save_resource_name,
    save_shop_name,
)

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

DEFAULT_LOG_ROOT = Path.home() / "StarCitizen" / "LIVE"
# Resolve LOG_ROOT from the environment while falling back to the user's home
# directory. ``Path`` accepts a ``Path`` instance so the default can remain a
# ``Path`` object without string conversion.
LOG_ROOT = Path(os.environ.get("LOG_ROOT", DEFAULT_LOG_ROOT))

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
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
            files = collect_files([str(LOG_ROOT)])
            df = pd.DataFrame(iter_records(files))
            ctx = analyse(df)
            ctx["log_info"] = {"path": str(LOG_ROOT), "count": len(files)}
            _latest_ctx = ctx
        except Exception:
            import logging
            logging.exception("Analyse failed:")
        await asyncio.sleep(10)


@app.get("/api/metrics")
async def metrics():

    return _latest_ctx or {"status": "bootstrapping"}


class ResourceItem(BaseModel):
    guid: str
    name: str


class ShopItem(BaseModel):
    shop_id: str
    name: str


@app.get("/api/names")
async def all_names():
    return get_all_names()


@app.post("/api/names/resource")
async def add_resource_name(item: ResourceItem):
    save_resource_name(item.guid, item.name)
    return {"status": "ok"}


@app.post("/api/names/shop")
async def add_shop_name(item: ShopItem):
    save_shop_name(item.shop_id, item.name)
    return {"status": "ok"}


@app.websocket("/ws")
async def ws_dashboard(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_text(json.dumps(_latest_ctx or {}))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

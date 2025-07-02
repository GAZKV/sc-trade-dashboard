from pathlib import Path  
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import asyncio, pandas as pd, json
from ..log_parser import collect_files, iter_records
from ..analysis   import analyse

LOG_ROOT = Path(r"C:/Program Files/Roberts Space Industries/StarCitizen/LIVE")  # configurable
app = FastAPI(title="SC Trade Dashboard API")
app.mount("/static", StaticFiles(directory=Path(__file__).parent/"static"), name="static")

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
            import logging, traceback
            logging.exception("Analyse failed:")
        await asyncio.sleep(10)

@app.on_event("startup")
async def startup():
    asyncio.create_task(watch_logs())

@app.get("/api/metrics")
async def metrics():
    return _latest_ctx or {"status": "bootstrapping"}

@app.websocket("/ws")
async def ws_dashboard(ws: WebSocket):
    await ws.accept()
    while True:
        await ws.send_text(json.dumps(_latest_ctx or {}))
        await asyncio.sleep(5)
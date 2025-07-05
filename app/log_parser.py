from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime
from decimal import Decimal

from .config import (
    BUY_MARK,
    SELL_MARK,
    MOVE_MARK,
    STOCK_MARK,
    LINE_RE,
    FIELD_RE,
    PRICE_FACTOR,
)

__all__ = ["collect_files", "iter_records"]


# ───────────────── helper: robust bytes→str ──────────────────


def decode_bytes(raw: bytes) -> str:
    for enc in ("utf-8", "latin-1", "utf-16-le", "utf-16-be"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("ascii", errors="ignore")

# ───────────────── core parser ──────────────────


def _parse_line(line: str) -> dict | None:
    if not any(mark in line for mark in (BUY_MARK, SELL_MARK, MOVE_MARK, STOCK_MARK)):
        return None
    m = re.match(LINE_RE, line)
    if not m:
        return None

    msg = m.group("msg")
    if BUY_MARK in msg:
        op = "Buy"
    elif SELL_MARK in msg:
        op = "Sell"
    elif MOVE_MARK in msg:
        op = "Move"
    elif STOCK_MARK in msg:
        op = "Stock"
    else:
        return None

    fields = {k: v for k, v in re.findall(FIELD_RE, msg)}
    try:
        qty_raw = Decimal(fields.get("quantity", "0").split()[0])
        quantity = qty_raw / Decimal("100") if op == "Buy" else qty_raw
        price_cs = (
            Decimal(fields.get("shopPricePerCentiSCU", "0")) * PRICE_FACTOR
        )
        return {
            "timestamp": datetime.strptime(
                m.group("ts"), "%Y-%m-%dT%H:%M:%S.%fZ"
            ),
            "operation": op,
            "shopId": fields.get("shopId", ""),
            "shopName": fields.get("shopName", ""),
            "resourceGUID": fields.get("resourceGUID", ""),
            "quantity": quantity,
            "shopPricePerCentiSCU": price_cs,
            "price": Decimal(fields.get("price", "0")),
            "amount": Decimal(fields.get("amount", "0")),
        }
    except Exception:
        return None

# ───────────────── public generators ──────────────────


def iter_records(paths: list[Path]):
    for path in paths:
        with path.open("rb") as fh:
            for raw in fh:
                rec = _parse_line(decode_bytes(raw))
                if rec:
                    yield rec


def collect_files(inputs: list[str]) -> list[Path]:
    files: list[Path] = []
    for p_str in inputs:
        p = Path(p_str)
        if p.is_file() and p.suffix.lower() == ".log":
            files.append(p)
        elif p.is_dir():
            files.extend(p.rglob("*.log"))
        else:
            files.extend(Path().glob(p_str))
    seen, uniq = set(), []
    for f in files:
        if f not in seen:
            uniq.append(f)
            seen.add(f)
    return uniq

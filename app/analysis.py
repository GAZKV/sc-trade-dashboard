from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, List

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# If you need the base64 helper for images
from .report import fig_to_b64


__all__ = ["analyse"]


def _best_routes(buys: pd.DataFrame, sells: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Return top profitable buy→sell routes per commodity."""
    if buys.empty or sells.empty:
        return pd.DataFrame()

    buy_unit = buys.assign(unit_price=buys.price / buys.quantity)
    sell_unit = sells.assign(unit_price=sells.amount / sells.quantity)

    buy_avg = (
        buy_unit.groupby(["resourceGUID", "shopId"]).unit_price.mean().reset_index()
    )
    sell_avg = (
        sell_unit.groupby(["resourceGUID", "shopId"]).unit_price.mean().reset_index()
    )

    routes = []
    for res in set(buy_avg.resourceGUID) & set(sell_avg.resourceGUID):
        buy_opts = buy_avg[buy_avg.resourceGUID == res]
        sell_opts = sell_avg[sell_avg.resourceGUID == res]
        best_buy = buy_opts.sort_values("unit_price").iloc[0]
        best_sell = sell_opts.sort_values("unit_price", ascending=False).iloc[0]
        profit = best_sell.unit_price - best_buy.unit_price
        if profit <= 0:
            continue
        routes.append(
            {
                "resourceGUID": res,
                "buyShopId": best_buy.shopId,
                "sellShopId": best_sell.shopId,
                "profitPerUnit": float(profit),
            }
        )

    if not routes:
        return pd.DataFrame()
    df_routes = pd.DataFrame(routes).sort_values("profitPerUnit", ascending=False)
    return df_routes.head(top_n)


def _pending_inventory(buys: pd.DataFrame, sells: pd.DataFrame) -> pd.DataFrame:
    """Return quantity and cost of goods not yet sold."""
    if buys.empty:
        return pd.DataFrame()

    buy_stats = buys.groupby("resourceGUID").agg(
        bought_qty=("quantity", "sum"), spent_sc=("price", "sum")
    )
    sell_stats = sells.groupby("resourceGUID").agg(sold_qty=("quantity", "sum"))

    pending = buy_stats.join(sell_stats, how="left").fillna(0)
    pending["pending_qty"] = pending.bought_qty - pending.sold_qty
    pending = pending[pending.pending_qty > 0].copy()
    avg_price = pending.spent_sc / pending.bought_qty
    pending["pending_cost_sc"] = (avg_price * pending.pending_qty).fillna(0)
    return pending.reset_index()[
        ["resourceGUID", "pending_qty", "pending_cost_sc"]
    ]


def _records(df: pd.DataFrame) -> List[dict]:
    """Convert a DataFrame to a list of dicts with Decimals cast to float."""
    if df.empty:
        return []
    records = []
    for rec in df.to_dict("records"):
        for k, v in rec.items():
            if isinstance(v, Decimal):
                rec[k] = float(v)
        records.append(rec)
    return records


def _daily_profit_series(buys: pd.DataFrame, sells: pd.DataFrame) -> Dict[str, List]:
    """Return dict with date labels and profit values."""
    if buys.empty and sells.empty:
        return {"labels": [], "values": []}

    # ensure date column
    all_ops = pd.concat([buys, sells], ignore_index=True)
    all_ops["date"] = all_ops.timestamp.dt.date

    buy_daily = buys.groupby(buys.timestamp.dt.date).price.sum()
    sell_daily = sells.groupby(sells.timestamp.dt.date).amount.sum()

    daily = sell_daily.sub(buy_daily, fill_value=0).sort_index()

    return {
        "labels": [d.isoformat() for d in daily.index],
        "values": [float(v) for v in daily.values],
    }


def _summary_table_buy(buys: pd.DataFrame) -> pd.DataFrame:
    if buys.empty:
        return pd.DataFrame()
    return (
        buys.groupby(["shopId", "resourceGUID"])
        .agg(
            minQuantity=("quantity", "min"),
            avgQuantity=("quantity", "mean"),
            maxQuantity=("quantity", "max"),
            minPriceperCentiSCU=("shopPricePerCentiSCU", "min"),
            avgPriceperCentiSCU=("shopPricePerCentiSCU", "mean"),
            maxPriceperCentiSCU=("shopPricePerCentiSCU", "max"),
        )
        .reset_index()
    )


def _summary_table_sell(sells: pd.DataFrame) -> pd.DataFrame:
    if sells.empty:
        return pd.DataFrame()
    sells = sells.copy()
    sells["amountSell"] = sells.amount / sells.quantity
    return (
        sells.groupby(["shopId", "resourceGUID"])
        .agg(
            minQuantity=("quantity", "min"),
            avgQuantity=("quantity", "mean"),
            maxQuantity=("quantity", "max"),
            minAmountSell=("amountSell", "min"),
            avgAmountSell=("amountSell", "mean"),
            maxAmountSell=("amountSell", "max"),
        )
        .reset_index()
    )


def analyse(df: pd.DataFrame) -> dict:
    """Compute KPIs and summaries from the combined log DataFrame."""
    if df.empty:
        return {
            "kpi": {
                "total_profit_sc": 0,
                "total_buys": 0,
                "total_sells": 0,
            },
            "daily_profit": {"labels": [], "values": []},
            "buy_summary": [],
            "sell_summary": [],
        }

    # filter out zero / negative qty rows, copy to avoid SettingWithCopy
    df = df[df.quantity > 0].copy()

    buys = df[df.operation == "Buy"].copy()
    sells = df[df.operation == "Sell"].copy()

    # Total profit calculation
    total_profit = sells.amount.sum() - buys.price.sum()

    kpi = {
        "total_profit_sc": float(total_profit),
        "total_buys": int(len(buys)),
        "total_sells": int(len(sells)),
    }

    daily_profit = _daily_profit_series(buys, sells)

    buy_summary = _records(_summary_table_buy(buys))
    sell_summary = _records(_summary_table_sell(sells))

    best_routes = _records(_best_routes(buys, sells))
    pending_goods = _records(_pending_inventory(buys, sells))

    return {
        "kpi": kpi,
        "daily_profit": daily_profit,
        "buy_summary": buy_summary,
        "sell_summary": sell_summary,
        "best_routes": best_routes,
        "pending_goods": pending_goods,
    }

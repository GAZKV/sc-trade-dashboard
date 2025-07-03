from __future__ import annotations

from typing import Dict, List

import pandas as pd


__all__ = ["analyse"]


def _daily_profit_series(
    buys: pd.DataFrame, sells: pd.DataFrame
) -> Dict[str, List]:
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
        buys.groupby(["shopName", "resourceGUID"])
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
        sells.groupby(["shopName", "resourceGUID"])
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

    buy_summary = _summary_table_buy(buys).to_dict("records")
    sell_summary = _summary_table_sell(sells).to_dict("records")

    return {
        "kpi": kpi,
        "daily_profit": daily_profit,
        "buy_summary": buy_summary,
        "sell_summary": sell_summary,
    }

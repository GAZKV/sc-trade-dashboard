from decimal import Decimal
from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analysis import analyse


def test_analyse_empty():
    df = pd.DataFrame(columns=["timestamp", "operation", "shopId", "shopName", "resourceGUID", "quantity", "shopPricePerCentiSCU", "price", "amount"])
    ctx = analyse(df)
    assert ctx["kpi"]["total_profit_sc"] == 0
    assert ctx["kpi"]["total_buys"] == 0
    assert ctx["kpi"]["total_sells"] == 0
    assert ctx["daily_profit"] == {"labels": [], "values": []}


def test_analyse_basic_profit():
    data = [
        {
            "timestamp": pd.Timestamp("2025-01-01T10:00:00Z"),
            "operation": "Buy",
            "shopId": "ID1",
            "shopName": "ShopA",
            "resourceGUID": "res1",
            "quantity": Decimal("10"),
            "shopPricePerCentiSCU": Decimal("0"),
            "price": Decimal("100000"),
            "amount": Decimal("0"),
        },
        {
            "timestamp": pd.Timestamp("2025-01-02T10:00:00Z"),
            "operation": "Sell",
            "shopId": "ID2",
            "shopName": "ShopB",
            "resourceGUID": "res1",
            "quantity": Decimal("10"),
            "shopPricePerCentiSCU": Decimal("0"),
            "price": Decimal("0"),
            "amount": Decimal("150000"),
        },
    ]
    df = pd.DataFrame(data)
    ctx = analyse(df)
    assert ctx["kpi"]["total_profit_sc"] == 50000
    assert ctx["kpi"]["total_buys"] == 1
    assert ctx["kpi"]["total_sells"] == 1
    assert ctx["daily_profit"]["labels"] == ["2025-01-01", "2025-01-02"]
    assert ctx["daily_profit"]["values"] == [-100000.0, 150000.0]
    assert ctx["best_routes"][0]["profitPerUnit"] == 5000.0
    assert ctx["pending_goods"] == []
    last = {rec["shopId"]: rec["operation"] for rec in ctx["last_transactions"]}
    assert last["ID1"] == "Buy"
    assert last["ID2"] == "Sell"


def test_pending_inventory_and_suggested_shop():
    data = [
        {
            "timestamp": pd.Timestamp("2025-02-01T10:00:00Z"),
            "operation": "Buy",
            "shopId": "B1",
            "shopName": "BuyShop",
            "resourceGUID": "res2",
            "quantity": Decimal("10"),
            "shopPricePerCentiSCU": Decimal("100"),
            "price": Decimal("1000"),
            "amount": Decimal("0"),
        },
        {
            "timestamp": pd.Timestamp("2025-02-02T10:00:00Z"),
            "operation": "Sell",
            "shopId": "S1",
            "shopName": "SellLow",
            "resourceGUID": "res2",
            "quantity": Decimal("4"),
            "shopPricePerCentiSCU": Decimal("0"),
            "price": Decimal("0"),
            "amount": Decimal("600"),
        },
        {
            "timestamp": pd.Timestamp("2025-02-03T10:00:00Z"),
            "operation": "Sell",
            "shopId": "S2",
            "shopName": "SellHigh",
            "resourceGUID": "res2",
            "quantity": Decimal("2"),
            "shopPricePerCentiSCU": Decimal("0"),
            "price": Decimal("0"),
            "amount": Decimal("400"),
        },
    ]

    df = pd.DataFrame(data)
    ctx = analyse(df)
    pending = ctx["pending_goods"]
    assert len(pending) == 1
    rec = pending[0]
    assert rec["resourceGUID"] == "res2"
    assert rec["pending_qty"] == 4
    assert rec["pending_uec"] == 400
    assert rec["suggested shopId"] == "S2"

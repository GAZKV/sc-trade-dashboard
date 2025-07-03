from decimal import Decimal
from pathlib import Path
import sys
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analysis import analyse


def test_analyse_empty():
    df = pd.DataFrame(columns=["timestamp", "operation", "shopName", "resourceGUID", "quantity", "shopPricePerCentiSCU", "price", "amount"])
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

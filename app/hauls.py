"""Track buy/sell moves and compute haul profits."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable, Dict, List

__all__ = ["HaulTracker", "track_hauls"]


@dataclass
class _Item:
    qty: Decimal
    unit_cost: Decimal
    buy_shop: str
    location: str
    buy_ts: object  # datetime


class HaulTracker:
    """Maintain per-resource inventories and build haul records."""

    def __init__(self) -> None:
        self.inventory: Dict[str, List[_Item]] = defaultdict(list)
        self.hauls: List[dict] = []

    # ────────── inventory management ──────────
    def _add_buy(self, rec: dict) -> None:
        qty = rec["quantity"]
        if qty <= 0:
            return
        unit_cost = rec["price"] / qty if qty else Decimal("0")
        item = _Item(
            qty=qty,
            unit_cost=unit_cost,
            buy_shop=rec["shopId"],
            location=rec["shopId"],
            buy_ts=rec["timestamp"],
        )
        self.inventory[rec["resourceGUID"]].append(item)

    def _sell(self, rec: dict) -> None:
        resource = rec["resourceGUID"]
        qty = rec["quantity"]
        if qty <= 0:
            return
        revenue_total = rec["amount"]
        unit_sell = revenue_total / qty if qty else Decimal("0")
        items = self.inventory[resource]
        i = 0
        while qty > 0 and i < len(items):
            item = items[i]
            if item.qty <= 0:
                items.pop(i)
                continue
            take = item.qty if item.qty <= qty else qty
            cost = take * item.unit_cost
            revenue = take * unit_sell
            self.hauls.append(
                {
                    "resourceGUID": resource,
                    "buy_shop": item.buy_shop,
                    "sell_shop": rec["shopId"],
                    "quantity": take,
                    "buy_price": cost,
                    "sell_price": revenue,
                    "profit": revenue - cost,
                }
            )
            item.qty -= take
            qty -= take
            if item.qty == 0:
                items.pop(i)
            else:
                i += 1
        # ignore unmatched quantity

    def _move(self, rec: dict) -> None:
        resource = rec["resourceGUID"]
        qty = rec["quantity"]
        dest = rec["shopId"]
        if qty <= 0:
            return
        items = self.inventory[resource]
        i = 0
        while qty > 0 and i < len(items):
            item = items[i]
            if item.qty <= 0:
                items.pop(i)
                continue
            take = item.qty if item.qty <= qty else qty
            if take == item.qty:
                item.location = dest
            else:
                item.qty -= take
                new_item = _Item(
                    qty=take,
                    unit_cost=item.unit_cost,
                    buy_shop=item.buy_shop,
                    location=dest,
                    buy_ts=item.buy_ts,
                )
                items.insert(i + 1, new_item)
            qty -= take
            i += 1
        # ignore leftover qty if move exceeds inventory

    # ────────── public API ──────────
    def process(self, rec: dict) -> None:
        op = rec.get("operation")
        if op == "Buy":
            self._add_buy(rec)
        elif op == "Sell":
            self._sell(rec)
        elif op == "Move":
            self._move(rec)

    def completed_hauls(self) -> List[dict]:
        return self.hauls


def track_hauls(records: Iterable[dict]) -> List[dict]:
    """Process records chronologically and return haul list."""
    tracker = HaulTracker()
    for rec in sorted(records, key=lambda r: r["timestamp"]):
        tracker.process(rec)
    return tracker.completed_hauls()

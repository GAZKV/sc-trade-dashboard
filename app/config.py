from decimal import Decimal

BUY_MARK = "<CEntityComponentCommodityUIProvider::SendCommodityBuyRequest>"
SELL_MARK = "<CEntityComponentCommodityUIProvider::SendCommoditySellRequest>"

LINE_RE = (
    r"^<?"
    r"(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)"
    r">?\s*\[Notice]\s*"
    r"(?P<msg>.*)$"
)
FIELD_RE = r"(\w+)\[([^]]+)]"

PRICE_FACTOR = Decimal("1000")  # centi‑SCU → micro‑SCU

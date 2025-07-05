from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.hauls import track_hauls
from app.log_parser import _parse_line, collect_files, iter_records
from tests.test_log_parser import BUY_LINE, SELL_LINE, MOVE_LINE


def test_basic_buy_sell():
    records = [_parse_line(BUY_LINE), _parse_line(SELL_LINE)]
    hauls = track_hauls(records)
    assert len(hauls) == 1
    h = hauls[0]
    assert h["buy_shop"] == "4511624678944"
    assert h["sell_shop"] == "4511623301041"
    assert h["quantity"] == Decimal("96")
    expected_profit = Decimal("2038501.000000") - Decimal("2159456.000000") * Decimal("96") / Decimal("120")
    assert h["profit"] == expected_profit


def test_move_then_sell():
    buy = _parse_line(BUY_LINE)
    move_line = MOVE_LINE.replace("quantity[10]", "quantity[120]")
    move = _parse_line(move_line)
    sell_line = (
        SELL_LINE.replace("4511623301041", "4511623301042")
        .replace("quantity[96]", "quantity[120]")
        .replace("amount[2038501.000000]", "amount[2548126.250000]")
    )
    sell = _parse_line(sell_line)
    hauls = track_hauls([buy, move, sell])
    assert len(hauls) == 1
    h = hauls[0]
    assert h["buy_shop"] == "4511624678944"
    assert h["sell_shop"] == "4511623301042"
    assert h["quantity"] == Decimal("120")


def test_hauls_from_sample_logs():
    log_dir = Path(__file__).parent / "logs"
    files = collect_files([str(log_dir)])
    records = list(iter_records(files))
    hauls = track_hauls(records)
    assert len(hauls) == 2
    profits = [float(h["profit"]) for h in hauls]
    assert profits[0] == 120937.0
    assert profits[1] == 90993.0

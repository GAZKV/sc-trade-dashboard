from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.log_parser import _parse_line, iter_records, collect_files

BUY_LINE = "<2025-06-21T22:00:18.409Z> [Notice] <CEntityComponentCommodityUIProvider::SendCommodityBuyRequest> Sending SShopCommodityBuyRequest - playerId[3563068139983] shopId[4511624678944] shopName[SCShop_ht_delta_rayari_m_store] kioskId[4511624678943] price[2159456.000000] shopPricePerCentiSCU[179.954651] resourceGUID[096618a0-1f7d-48db-9c6a-9ac459386527] autoLoading[0] quantity[12000.000000 cSCU] Cargo Box Data: boxSize[8.000000] | unitAmount[15] [Team_CoreGameplayFeatures][Shops][UI]"

SELL_LINE = "<2025-06-21T22:36:46.210Z> [Notice] <CEntityComponentCommodityUIProvider::SendCommoditySellRequest> Sending SShopCommoditySellRequest - playerId[3563068139983] shopId[4511623301041] shopName[SCShop_ht_delta_shubin_m_store] kioskId[4511623301040] amount[2038501.000000] resourceGUID[096618a0-1f7d-48db-9c6a-9ac459386527] autoLoading[0] quantity[96] transactionMode[Location] Cargo Box Data:  [boxSize[8] | unitAmount[12]] [Team_CoreGameplayFeatures][Shops][UI]"


def test_parse_buy_line():
    rec = _parse_line(BUY_LINE)
    assert rec["operation"] == "Buy"
    assert rec["quantity"] == Decimal("120.000000")
    assert rec["price"] == Decimal("2159456.000000")
    assert rec["shopPricePerCentiSCU"] == Decimal("179954.651000")


def test_parse_sell_line():
    rec = _parse_line(SELL_LINE)
    assert rec["operation"] == "Sell"
    assert rec["amount"] == Decimal("2038501.000000")
    assert rec["quantity"] == Decimal("96")


def test_iter_records_and_collect_files(tmp_path):
    log_file = tmp_path / "sample.log"
    log_file.write_text(BUY_LINE + "\n" + SELL_LINE)

    files = collect_files([str(tmp_path)])
    assert log_file in files

    records = list(iter_records(files))
    assert len(records) == 2
    assert records[0]["operation"] == "Buy"
    assert records[1]["operation"] == "Sell"

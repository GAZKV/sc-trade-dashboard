#!/usr/bin/env python3
"""CLI wrapper to keep parity with the standalone script."""
import argparse
import logging
import sys
from pathlib import Path
import pandas as pd

from app.log_parser import collect_files, iter_records
from app.analysis import analyse
from app.report import render_html


def main():
    p = argparse.ArgumentParser("Generate Star Citizen trade report")
    p.add_argument("log_paths", nargs="+", help="folders / *.log patterns")
    p.add_argument("output_html", type=Path)
    p.add_argument("--excel", type=Path)
    args = p.parse_args()

    files = collect_files(args.log_paths)
    if not files:
        logging.error("No .log files found")
        sys.exit(1)

    df = pd.DataFrame(iter_records(files))
    if df.empty:
        logging.error("No BUY/SELL events detected")
        sys.exit(2)

    ctx = analyse(df)
    render_html(ctx, args.output_html)
    logging.info("HTML report generated → %s", args.output_html)

    if args.excel:
        try:
            buy_df  = pd.DataFrame(ctx.get("buy_summary", []))
            sell_df = pd.DataFrame(ctx.get("sell_summary", []))
            with pd.ExcelWriter(args.excel) as xls:
                buy_df.to_excel(xls, "BUY", index=False)
                sell_df.to_excel(xls, "SELL", index=False)
        except Exception as exc:
            logging.error("Failed to write Excel report: %s", exc)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Download OHLCV data via yfinance.

Usage:
    python tests/download_data.py

Data is saved as CSV to tests/data/{TICKER}.csv
Columns are normalized to lowercase to match indicator expectations.
"""

import os
import sys

import yfinance as yf

# Allow running from project root regardless of cwd
sys.path.insert(0, os.path.dirname(__file__))
from config import DATA_DIR, INTERVAL, PERIOD, TICKERS


def download(ticker: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"{ticker}.csv")

    print(f"Downloading {ticker} ({PERIOD}, {INTERVAL})...", end=" ", flush=True)
    df = yf.download(ticker, period=PERIOD, interval=INTERVAL, auto_adjust=True)

    if df.empty:
        print("FAILED (no data)")
        return ""

    # Flatten MultiIndex columns if present (yfinance >= 0.2.32)
    if isinstance(df.columns, __import__("pandas").MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Normalize: lowercase, match indicator column expectations
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]

    # yfinance returns 'close' as 'adj close' when auto_adjust=False,
    # but with auto_adjust=True we get the standard OHLCV columns.
    # Add quote_volume and taker_buy columns expected by some indicators.
    # We approximate: quote_volume ≈ close * volume
    if "quote_volume" not in df.columns:
        df["quote_volume"] = df["close"] * df["volume"]

    # taker_buy_quote_asset_volume: approximate as 50% of quote_volume
    if "taker_buy_quote_asset_volume" not in df.columns:
        df["taker_buy_quote_asset_volume"] = df["quote_volume"] * 0.5

    df.to_csv(path)
    rows = len(df)
    date_range = f"{df.index[0].date()} → {df.index[-1].date()}"
    print(f"OK  {rows} rows  ({date_range})  → {path}")
    return path


def main():
    for ticker in TICKERS:
        download(ticker)


if __name__ == "__main__":
    main()

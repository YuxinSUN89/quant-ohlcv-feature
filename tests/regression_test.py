#!/usr/bin/env python3
"""
Regression test: compare master vs config-pandas indicator outputs.

Runs each indicator from both branches on the same data and compares the
result column. Reports files where outputs differ beyond tolerance.

Usage:
    python tests/regression_test.py                     # all tickers
    python tests/regression_test.py --tickers AAPL       # 1 stock
    python tests/regression_test.py --tickers AAPL MSFT  # 2 stocks
"""

import argparse
import importlib
import os
import subprocess
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
if TEST_DIR not in sys.path:
    sys.path.insert(0, TEST_DIR)

from config import DATA_DIR, INDICATOR_CONFIG, PERIODS

from indicator_config import unwrap_configured

FEATURE_DIRS = [
    "momentum_feature",
    "trend_feature",
    "volatility_feature",
    "volume_feature",
    "price_feature",
    "liquidity_feature",
    "composite_feature",
]

# Known intentional fixes on config-pandas that produce different output vs master.
# Format: (indicator_name, periods_where_different)
# These are NOT bugs — they are corrections.
KNOWN_DIFFS = {
    # ewm(n) → ewm(span=n): com→span changes alpha from 1/(1+n) to 2/(n+1)
    "Smi": "all",
    "Sroc": "all",
    "SrocVol": "all",
    "Stc": "all",
    "Dema": "all",
    "T3": "all",
    "Tema": "all",
    "Trix": "all",
    "Ko": "all",
    "Pvo": "all",
    # Adtm: eps added to denominator (div-by-zero protection)
    "Adtm": "all",
    # Kama: shift(1) → shift(n)
    "Kama": "all",
}


def discover_indicators():
    """Return sorted list of (file_path, module_name, stem) for all indicators."""
    indicators = []
    for d in FEATURE_DIRS:
        full_dir = os.path.join(PROJECT_ROOT, d)
        if not os.path.isdir(full_dir):
            continue
        for f in sorted(os.listdir(full_dir)):
            if f.endswith(".py") and f != "__init__.py":
                path = os.path.join(d, f)
                mod_name = f"{d}.{f[:-3]}"
                stem = f[:-3]
                indicators.append((path, mod_name, stem))
    return indicators


def get_master_source(indicator_path):
    """Get indicator source from master branch via git."""
    result = subprocess.run(
        ["git", "show", f"master:{indicator_path}"], capture_output=True, text=True, cwd=PROJECT_ROOT
    )
    if result.returncode != 0:
        return None
    return result.stdout


def run_master_indicator(source, df, n, factor_name):
    """Execute master's indicator source in isolated namespace."""
    mod_ns = {}
    exec(compile(source, "<master>", "exec"), mod_ns)
    return mod_ns["signal"](df.copy(), n, factor_name)


def run_config_indicator(mod_name, df, n, factor_name):
    """Run config-pandas indicator through the config wrapper."""
    mod = importlib.import_module(mod_name)
    wrapped_df = INDICATOR_CONFIG.wrap(df.copy())
    result = mod.signal(wrapped_df, n, factor_name)
    return unwrap_configured(result)


def compare_series(master_col, config_col, rtol=1e-7, atol=1e-10):
    """Compare two pandas Series, return (match_pct, max_abs_diff, max_rel_diff, details)."""
    # Align indices
    master_vals = master_col.astype(float).values
    config_vals = config_col.astype(float).values

    if len(master_vals) != len(config_vals):
        return 0.0, float("inf"), float("inf"), f"length mismatch: {len(master_vals)} vs {len(config_vals)}"

    # Both NaN = match
    both_nan = np.isnan(master_vals) & np.isnan(config_vals)
    one_nan = np.isnan(master_vals) ^ np.isnan(config_vals)

    # Compare non-NaN values
    valid = ~np.isnan(master_vals) & ~np.isnan(config_vals)
    if valid.sum() == 0:
        if one_nan.sum() == 0:
            return 100.0, 0.0, 0.0, "all NaN, match"
        return 0.0, float("inf"), float("inf"), f"NaN mismatch: {one_nan.sum()}"

    m = master_vals[valid]
    c = config_vals[valid]

    abs_diffs = np.abs(m - c)
    denom = np.maximum(np.abs(m), np.abs(c))
    denom = np.maximum(denom, 1e-10)
    rel_diffs = abs_diffs / denom

    close = (abs_diffs <= atol) | (rel_diffs <= rtol)
    match_pct = (close.sum() + both_nan.sum()) / len(master_vals) * 100

    max_abs = float(abs_diffs.max()) if len(abs_diffs) > 0 else 0.0
    max_rel = float(rel_diffs.max()) if len(rel_diffs) > 0 else 0.0

    details = ""
    nan_mismatch = int(one_nan.sum())
    if nan_mismatch > 0:
        details += f"NaN mismatch: {nan_mismatch}/{len(master_vals)}"
    if close.sum() < len(m):
        details += f" value mismatch: {len(m) - int(close.sum())}/{len(m)}"

    return match_pct, max_abs, max_rel, details


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tickers", nargs="+", default=None)
    parser.add_argument("--periods", nargs="+", type=int, default=None)
    parser.add_argument("--tol", type=float, default=1e-6, help="relative tolerance")
    args = parser.parse_args()

    indicators = discover_indicators()
    tickers = args.tickers or [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "META",
        "NVDA",
        "TSLA",
        "NFLX",
        "XOM",
        "CVX",
        "JPM",
        "BAC",
        "JNJ",
        "PFE",
        "CAT",
        "HD",
        "PG",
        "KO",
        "NEE",
        "GLD",
        "TLT",
        "BTC-USD",
        "ABBV",
        "UNH",
        "MRK",
        "DE",
        "UNP",
        "HON",
        "GE",
        "BA",
        "NKE",
        "MCD",
        "SBUX",
        "TGT",
        "COST",
        "LIN",
        "APD",
        "SHW",
        "NEM",
        "DUK",
        "AMT",
        "PLD",
        "T",
        "VZ",
        "COP",
        "SLB",
        "OXY",
        "GS",
        "MS",
        "BLK",
        "SCHW",
        "AXP",
        "LLY",
        "AMGN",
        "VRA",
    ]
    periods = args.periods or PERIODS

    print(f"Tickers: {len(tickers)}")
    print(f"Periods: {periods}")
    print(f"Indicators: {len(indicators)}")
    print(f"Tolerance: {args.tol}")
    print(f"Config: min_periods={INDICATOR_CONFIG.min_periods}, ddof={INDICATOR_CONFIG.ddof}")
    print()

    total = 0
    ok = 0
    known_diff = 0
    diff = 0
    error_master = 0
    error_config = 0
    diff_details = []

    for ticker in tickers:
        csv_path = os.path.join(DATA_DIR, f"{ticker}.csv")
        if not os.path.exists(csv_path):
            print(f"  {ticker}: no data, skip")
            continue

        df = pd.read_csv(csv_path, index_col=0)
        print(f"  {ticker} ({len(df)} rows):")

        for ind_path, mod_name, stem in indicators:
            is_known = stem in KNOWN_DIFFS

            for n in periods:
                total += 1
                factor_name = f"test_{stem}_{n}"

                # Run master version
                master_source = get_master_source(ind_path)
                if master_source is None:
                    error_master += 1
                    continue

                try:
                    master_result = run_master_indicator(master_source, df, n, factor_name)
                    master_col = master_result[factor_name]
                except Exception:
                    error_master += 1
                    continue

                # Run config-pandas version
                try:
                    config_result = run_config_indicator(mod_name, df, n, factor_name)
                    config_col = config_result[factor_name]
                except Exception as e:
                    error_config += 1
                    diff_details.append(f"  CONFIG ERROR: {ticker}/{stem}/n={n}: {e}")
                    continue

                # Compare
                match_pct, max_abs, max_rel, details = compare_series(master_col, config_col, rtol=args.tol)

                if match_pct >= 99.9:
                    ok += 1
                elif is_known:
                    known_diff += 1
                else:
                    diff += 1
                    diff_details.append(
                        f"  DIFF: {ticker}/{stem}/n={n}: match={match_pct:.1f}% "
                        f"max_abs={max_abs:.2e} max_rel={max_rel:.2e} {details}"
                    )

        _pct = (ok + known_diff + diff) / max(total, 1) * 100
        print(
            f"    progress: {ok} ok, {known_diff} known-diff, {diff} unknown-diff, "
            f"{error_master} master-err, {error_config} config-err"
        )

    print(f"\n{'=' * 70}")
    print("  REGRESSION TEST SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total runs:        {total}")
    print(f"  Match (≥99.9%):    {ok}")
    print(f"  Known diffs:       {known_diff}")
    print(f"  Unknown diffs:     {diff}")
    print(f"  Master errors:     {error_master}")
    print(f"  Config errors:     {error_config}")
    print()

    if diff_details:
        # Show first 50 unknown diffs
        print(f"  UNKNOWN DIFFS ({len(diff_details)} total, showing first 50):")
        for d in diff_details[:50]:
            print(d)
        if len(diff_details) > 50:
            print(f"  ... and {len(diff_details) - 50} more")
        print()

    pass_rate = ok / max(total - known_diff - error_master - error_config, 1) * 100
    print(f"  Pass rate (excl known/errs): {pass_rate:.1f}%")

    if diff == 0 and error_config == 0:
        print("  ✓ ALL INDICATORS MATCH (excluding known diffs)")
        return 0
    else:
        print("  ✗ Some unexpected differences found")
        return 1


if __name__ == "__main__":
    sys.exit(main())

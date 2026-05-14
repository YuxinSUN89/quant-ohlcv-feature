#!/usr/bin/env python3
"""
Run every indicator across all tickers and periods.
Save results + metadata to a CSV file for later comparison.

Usage:
    python tests/run_suite.py
    python tests/run_suite.py --output results/my_run.csv
    python tests/run_suite.py --resample-size 500 --resample-seed 42
    python tests/run_suite.py --resample-fraction 0.5 --resample-seed 42

The output CSV contains:
  - One row per (ticker, indicator, period)
  - Columns: ticker, indicator, period, period_label, status, n_rows,
    mean, std, min, max, nan_count, nan_pct, runtime_ms, error
  - A header block prefixed with '#':
      Line 1: run metadata  (lib, branch, commit, timestamp …)
      Line 2: full config snapshot (tickers, periods, labels …)

Works on BOTH the pandas branch (master) and the polars branch (uv-polars).
Auto-detects which DataFrame library is in use.
"""

from __future__ import annotations

import importlib
import json
import os
import sys
import time
from pathlib import Path

# ── detect library ────────────────────────────────────────────
force_lib = None
if "--lib" in sys.argv:
    idx = sys.argv.index("--lib")
    force_lib = sys.argv[idx + 1].lower()

if force_lib == "pandas":
    import pandas as pd

    LIB, LIB_VERSION = "pandas", pd.__version__

    def load_csv(path):
        return pd.read_csv(path, index_col=0)

    def df_shape(df):
        return df.shape

    def df_clone(df):
        return df.copy()

    def df_take_rows(df, positions):
        return df.iloc[positions].copy()
elif force_lib == "polars":
    import polars as pl

    LIB, LIB_VERSION = "polars", pl.__version__

    def load_csv(path):
        return pl.read_csv(path)

    def df_shape(df):
        return df.shape

    def df_clone(df):
        return df.clone()

    def df_take_rows(df, positions):
        return df[positions]
else:
    try:
        import polars as pl

        LIB = "polars"
        LIB_VERSION = pl.__version__

        def load_csv(path):
            return pl.read_csv(path)

        def df_shape(df):
            return df.shape

        def df_clone(df):
            return df.clone()

        def df_take_rows(df, positions):
            return df[positions]
    except ImportError:
        import pandas as pd

        LIB = "pandas"
        LIB_VERSION = pd.__version__

        def load_csv(path):
            return pd.read_csv(path, index_col=0)

        def df_shape(df):
            return df.shape

        def df_clone(df):
            return df.copy()

        def df_take_rows(df, positions):
            return df.iloc[positions].copy()


# ── config ────────────────────────────────────────────────────
TEST_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(TEST_DIR)
for path in (PROJECT_ROOT, TEST_DIR):
    if path not in sys.path:
        sys.path.insert(0, path)

from config import (  # noqa: E402
    DATA_DIR,
    INDICATOR_CONFIG,
    PERIOD_LABELS,
    PERIODS,
    RESULTS_DIR,
    TICKERS,
    get_resample_row_positions,
    parse_resample_cli,
    snapshot,
)

from indicator_config import ensure_columns, unwrap_configured  # noqa: E402

FEATURE_DIRS = [
    "momentum_feature",
    "trend_feature",
    "volatility_feature",
    "volume_feature",
    "price_feature",
    "liquidity_feature",
    "composite_feature",
]


def discover_indicators():
    """Return sorted list of (module_path, module_name) for all indicators."""
    indicators = []
    for d in FEATURE_DIRS:
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if f.endswith(".py") and f != "__init__.py":
                mod_name = f"{d}.{f[:-3]}"
                indicators.append((os.path.join(d, f), mod_name))
    return indicators


def run_indicator(mod_name, df, n, factor_name):
    """Import and run a single indicator. Returns (result_df, runtime_ms) or raises."""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    mod = importlib.import_module(mod_name)
    t0 = time.perf_counter()
    df = ensure_columns(df, INDICATOR_CONFIG)
    result = mod.signal(df, n, factor_name, INDICATOR_CONFIG)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return unwrap_configured(result), elapsed_ms


def summarize_column(df, col_name):
    """Extract summary stats from a single result column."""
    if LIB == "polars":
        s = df[col_name]
        stats = {
            "mean": float(s.mean()) if s.mean() is not None else float("nan"),
            "std": float(s.std()) if s.std() is not None else float("nan"),
            "min": float(s.min()) if s.min() is not None else float("nan"),
            "max": float(s.max()) if s.max() is not None else float("nan"),
            "nan_count": int(s.null_count()),
            "nan_pct": round(s.null_count() / len(s) * 100, 2),
        }
    else:
        s = df[col_name]
        stats = {
            "mean": float(s.mean()),
            "std": float(s.std()),
            "min": float(s.min()),
            "max": float(s.max()),
            "nan_count": int(s.isna().sum()),
            "nan_pct": round(s.isna().sum() / len(s) * 100, 2),
        }
    return stats


def main():
    output_path = None
    args = sys.argv[1:]
    if "--output" in args:
        idx = args.index("--output")
        output_path = args[idx + 1]

    try:
        resample_config = parse_resample_cli(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    os.makedirs(RESULTS_DIR, exist_ok=True)

    indicators = discover_indicators()
    print(f"Library:  {LIB} {LIB_VERSION}")
    print(f"Tickers:  {TICKERS}")
    print(f"Periods:  {PERIODS}")
    print(f"Indicators: {len(indicators)}")
    print(f"Resample: {resample_config or 'disabled'}")
    print()

    try:
        import git

        repo = git.Repo(search_parent_directories=True)
        branch = repo.active_branch.name
        commit = repo.head.commit.hexsha[:8]
    except Exception:
        branch = "unknown"
        commit = "unknown"

    run_meta = {
        "lib": LIB,
        "lib_version": LIB_VERSION,
        "branch": branch,
        "commit": commit,
        "num_indicators": len(indicators),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "resample": resample_config,
    }

    results = []
    total = len(TICKERS) * len(indicators) * len(PERIODS)
    done = 0
    ok = 0
    fail = 0
    skip = 0

    for ticker in TICKERS:
        csv_path = os.path.join(DATA_DIR, f"{ticker}.csv")
        if not os.path.exists(csv_path):
            print(f"  {ticker}: no data file ({csv_path}), run download_data.py first")
            skip += len(indicators) * len(PERIODS)
            continue

        base_df = load_csv(csv_path)
        original_rows, cols = df_shape(base_df)
        positions = get_resample_row_positions(original_rows, ticker, resample_config)
        if positions is not None:
            base_df = df_take_rows(base_df, positions)
        rows, cols = df_shape(base_df)
        if positions is None:
            print(f"  {ticker}: {rows} rows × {cols} cols")
        else:
            print(f"  {ticker}: {rows}/{original_rows} sampled rows × {cols} cols")

        for file_path, mod_name in indicators:
            ind_name = Path(file_path).stem

            for n in PERIODS:
                done += 1
                label = PERIOD_LABELS.get(n, str(n))
                factor_name = f"test_{ind_name}_{n}"
                record = {
                    "ticker": ticker,
                    "indicator": ind_name,
                    "module": mod_name,
                    "period": n,
                    "period_label": label,
                    "factor_name": factor_name,
                }

                try:
                    df = df_clone(base_df)
                    result_df, runtime_ms = run_indicator(mod_name, df, n, factor_name)

                    stats = summarize_column(result_df, factor_name)
                    record["status"] = "ok"
                    record["n_rows"] = df_shape(result_df)[0]
                    record["runtime_ms"] = round(runtime_ms, 1)
                    record["mean"] = stats["mean"]
                    record["std"] = stats["std"]
                    record["min"] = stats["min"]
                    record["max"] = stats["max"]
                    record["nan_count"] = stats["nan_count"]
                    record["nan_pct"] = stats["nan_pct"]
                    record["error"] = ""
                    ok += 1
                except Exception as e:
                    record["status"] = "error"
                    record["n_rows"] = ""
                    record["runtime_ms"] = ""
                    record["mean"] = ""
                    record["std"] = ""
                    record["min"] = ""
                    record["max"] = ""
                    record["nan_count"] = ""
                    record["nan_pct"] = ""
                    record["error"] = str(e)[:200]
                    fail += 1

                results.append(record)

        pct = done / total * 100 if total else 0
        print(f"  [{done}/{total} {pct:.0f}%] ok={ok} fail={fail}")

    if output_path is None:
        output_path = os.path.join(RESULTS_DIR, f"results_{LIB}_{branch}_{time.strftime('%Y%m%d_%H%M%S')}.csv")

    with open(output_path, "w") as f:
        f.write(f"# @run {json.dumps(run_meta)}\n")
        f.write(f"# @config {json.dumps(snapshot(resample_config))}\n")

        if results:
            import csv as csv_mod

            writer = csv_mod.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    print()
    print(f"{'=' * 60}")
    print(f"  Done. {ok} ok, {fail} fail, {skip} skip  (total {total})")
    print(f"  Results → {output_path}")
    print(f"{'=' * 60}")

    return output_path


if __name__ == "__main__":
    main()

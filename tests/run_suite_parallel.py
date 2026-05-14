#!/usr/bin/env python3
"""
Run every indicator across all tickers and periods using process-level parallelism.

Usage:
    python tests/run_suite_parallel.py --impl polars
    python tests/run_suite_parallel.py --impl pandas
    python tests/run_suite_parallel.py --impl polars --output results/x.csv
    python tests/run_suite_parallel.py --impl pandas --workers 16
    python tests/run_suite_parallel.py --impl polars --resample-fraction 0.5 --resample-seed 42

Output CSV: one row per (ticker, indicator, period) with summary stats.
"""

from __future__ import annotations

import csv as csv_mod
import importlib
import json
import multiprocessing
import os
import sys
import time

# ── CLI args ──────────────────────────────────────────────────
output_path = None
max_workers = min(32, os.cpu_count() or 1)

args = sys.argv[1:]
if "--output" in args:
    idx = args.index("--output")
    output_path = args[idx + 1]
if "--workers" in args:
    idx = args.index("--workers")
    max_workers = int(args[idx + 1])

# --impl is mandatory: selects which implementation directory to test
if "--impl" not in args:
    print("error: --impl is required (polars or pandas)", file=sys.stderr)
    raise SystemExit(1)
_impl_idx = args.index("--impl")
_impl_val = args[_impl_idx + 1].strip().lower()
if _impl_val not in ("polars", "pandas"):
    print(f"error: --impl must be polars or pandas, got {_impl_val!r}", file=sys.stderr)
    raise SystemExit(1)
_impl_name = f"impl_{_impl_val}"

# ── paths ─────────────────────────────────────────────────────
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
for p in (PROJECT_ROOT, TEST_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# ── config imports ────────────────────────────────────────────
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

try:
    RESAMPLE_CONFIG = parse_resample_cli(args)
except ValueError as exc:
    print(f"error: {exc}", file=sys.stderr)
    raise SystemExit(2) from exc

# ── library detection (driven by --impl) ──────────────────────
if _impl_val == "pandas":
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

    def get_stats(df, col):
        s = df[col]
        return {
            "mean": float(s.mean()),
            "std": float(s.std()),
            "min": float(s.min()),
            "max": float(s.max()),
            "nan_count": int(s.isna().sum()),
            "nan_pct": round(s.isna().sum() / len(s) * 100, 2),
        }

else:
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

    def get_stats(df, col):
        s = df[col]
        s_clean = s.drop_nans().drop_nulls()
        return {
            "mean": float(s_clean.mean()) if len(s_clean) > 0 else float("nan"),
            "std": float(s_clean.std()) if len(s_clean) > 1 else float("nan"),
            "min": float(s_clean.min()) if len(s_clean) > 0 else float("nan"),
            "max": float(s_clean.max()) if len(s_clean) > 0 else float("nan"),
            "nan_count": int(s.null_count() + s.is_nan().sum()),
            "nan_pct": round((s.null_count() + s.is_nan().sum()) / len(s) * 100, 2),
        }


# ── indicator discovery ───────────────────────────────────────
FEATURE_SUBDIRS = [
    "momentum_feature",
    "trend_feature",
    "volatility_feature",
    "volume_feature",
    "price_feature",
    "liquidity_feature",
    "composite_feature",
]

FEATURE_DIRS = [f"{_impl_name}.{sub}" for sub in FEATURE_SUBDIRS]


def discover_indicators():
    """Return sorted list of module names for all indicators."""
    indicators = []
    for d in FEATURE_DIRS:
        fs_path = d.replace(".", os.sep)
        abs_path = os.path.join(PROJECT_ROOT, fs_path)
        if not os.path.isdir(abs_path):
            continue
        for f in sorted(os.listdir(abs_path)):
            if f.endswith(".py") and f != "__init__.py":
                indicators.append(f"{d}.{f[:-3]}")
    return indicators


# ── worker ────────────────────────────────────────────────────
def _make_error_record(ticker, ind_name, mod_name, n, error_msg):
    """Build a standard error result row."""
    return {
        "ticker": ticker,
        "indicator": ind_name,
        "module": mod_name,
        "period": n,
        "period_label": PERIOD_LABELS.get(n, str(n)),
        "factor_name": f"test_{ind_name}_{n}",
        "status": "error",
        "n_rows": "",
        "runtime_ms": "",
        "mean": "",
        "std": "",
        "min": "",
        "max": "",
        "nan_count": "",
        "nan_pct": "",
        "error": error_msg[:200],
    }


def run_one(task: dict) -> dict:
    """Run a single (ticker, indicator, period) combination."""
    ticker = task["ticker"]
    mod_name = task["mod_name"]
    n = task["n"]
    ind_name = task["ind_name"]
    factor_name = f"test_{ind_name}_{n}"

    csv_path = os.path.join(DATA_DIR, f"{ticker}.csv")
    if not os.path.exists(csv_path):
        return _make_error_record(ticker, ind_name, mod_name, n, f"no data file: {csv_path}")

    try:
        base_df = load_csv(csv_path)
        n_rows, _ = df_shape(base_df)
        positions = get_resample_row_positions(n_rows, ticker, RESAMPLE_CONFIG)
        if positions is not None:
            base_df = df_take_rows(base_df, positions)
        df = df_clone(base_df)

        df = ensure_columns(df, INDICATOR_CONFIG)

        mod = importlib.import_module(mod_name)
        t0 = time.perf_counter()
        result = mod.signal(df, n, factor_name, INDICATOR_CONFIG)
        result = unwrap_configured(result)
        runtime_ms = (time.perf_counter() - t0) * 1000

        if factor_name not in result.columns:
            return _make_error_record(ticker, ind_name, mod_name, n, f"column '{factor_name}' not in result")

        stats = get_stats(result, factor_name)
        return {
            "ticker": ticker,
            "indicator": ind_name,
            "module": mod_name,
            "period": n,
            "period_label": PERIOD_LABELS.get(n, str(n)),
            "factor_name": factor_name,
            "status": "ok",
            "n_rows": df_shape(result)[0],
            "runtime_ms": round(runtime_ms, 1),
            **stats,
            "error": "",
        }
    except Exception as e:
        return _make_error_record(ticker, ind_name, mod_name, n, str(e))


# ── main ──────────────────────────────────────────────────────
def main():
    global output_path
    os.makedirs(RESULTS_DIR, exist_ok=True)

    indicators = discover_indicators()
    print(f"Impl:     {_impl_name}")
    print(f"Library:  {LIB} {LIB_VERSION}")
    print(f"Tickers:  {TICKERS}")
    print(f"Periods:  {PERIODS}")
    print(f"Indicators: {len(indicators)}")
    print(f"Workers:  {max_workers}")
    print(f"Resample: {RESAMPLE_CONFIG or 'disabled'}")
    print()

    tasks = []
    for ticker in TICKERS:
        for mod_name in indicators:
            ind_name = mod_name.split(".")[-1]
            for n in PERIODS:
                tasks.append({"ticker": ticker, "mod_name": mod_name, "n": n, "ind_name": ind_name})

    total = len(tasks)
    print(f"Total tasks: {total}")

    t_start = time.perf_counter()
    results = []
    ok = 0
    fail = 0

    with multiprocessing.Pool(processes=max_workers) as pool:
        for i, record in enumerate(pool.imap_unordered(run_one, tasks, chunksize=50)):
            results.append(record)
            if record["status"] == "ok":
                ok += 1
            else:
                fail += 1
            if (i + 1) % 500 == 0 or (i + 1) == total:
                elapsed = time.perf_counter() - t_start
                rate = (i + 1) / elapsed
                eta = (total - i - 1) / rate if rate > 0 else 0
                print(
                    f"  [{i + 1}/{total} {100 * (i + 1) / total:.0f}%] ok={ok} fail={fail}  "
                    f"{rate:.0f}/s  ETA {eta:.0f}s"
                )

    elapsed = time.perf_counter() - t_start
    print(f"\n  Wall time: {elapsed:.1f}s ({total / elapsed:.0f} tasks/s)")

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
        "impl": _impl_name,
        "branch": branch,
        "commit": commit,
        "num_indicators": len(indicators),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "wall_time_s": round(elapsed, 1),
        "workers": max_workers,
        "resample": RESAMPLE_CONFIG,
    }

    if not output_path:
        tag = f"{LIB}_{branch}"
        output_path = os.path.join(RESULTS_DIR, f"{tag}_{time.strftime('%Y%m%d_%H%M%S')}.csv")

    results.sort(key=lambda r: (r.get("ticker", ""), r.get("indicator", ""), int(r.get("period", 0) or 0)))

    with open(output_path, "w") as f:
        f.write(f"# @run {json.dumps(run_meta)}\n")
        f.write(f"# @config {json.dumps(snapshot(RESAMPLE_CONFIG))}\n")
        if results:
            writer = csv_mod.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    print(f"\n{'=' * 60}")
    print(f"  Done. {ok} ok, {fail} fail  (total {total})")
    print(f"  Results → {output_path}")
    print(f"{'=' * 60}")

    return output_path


if __name__ == "__main__":
    main()

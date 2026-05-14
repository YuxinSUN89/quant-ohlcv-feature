#!/usr/bin/env python3
"""
Run every indicator across all tickers and periods using process-level parallelism.

Usage:
    python tests/run_suite_parallel.py
    python tests/run_suite_parallel.py --lib pandas
    python tests/run_suite_parallel.py --output results/x.csv
    python tests/run_suite_parallel.py --workers 16
    python tests/run_suite_parallel.py --resample-size 500 --resample-seed 42
    python tests/run_suite_parallel.py --resample-fraction 0.5 --resample-seed 42

Auto-detects whether this is the master branch (signal(*args)) or
whether indicator_config.py exists in the project root.

Output CSV: one row per (ticker, indicator, period) with summary stats.
"""

from __future__ import annotations

import csv as csv_mod
import hashlib
import importlib
import json
import multiprocessing
import os
import random
import sys
import time
from typing import Any

# ── CLI args ──────────────────────────────────────────────────
force_lib = None
output_path = None
max_workers = min(32, os.cpu_count() or 1)

args = sys.argv[1:]
if "--lib" in args:
    idx = args.index("--lib")
    force_lib = args[idx + 1].lower()
if "--output" in args:
    idx = args.index("--output")
    output_path = args[idx + 1]
if "--workers" in args:
    idx = args.index("--workers")
    max_workers = int(args[idx + 1])

# ── paths ─────────────────────────────────────────────────────
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
for p in (PROJECT_ROOT, TEST_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# ── detect branch type ────────────────────────────────────────
HAS_CONFIG = os.path.exists(os.path.join(PROJECT_ROOT, "indicator_config.py"))
DEFAULT_RESAMPLE_METHOD = "subset_no_replacement_sorted"
DEFAULT_RESAMPLE_SEED = 42


def parse_resample_cli(argv: list[str]) -> dict[str, Any] | None:
    """Parse deterministic resampling flags from CLI args."""
    wants_resample = any(
        flag in argv for flag in ("--resample", "--resample-size", "--resample-fraction", "--resample-seed")
    )
    if not wants_resample:
        return None

    method = DEFAULT_RESAMPLE_METHOD
    if "--resample" in argv:
        idx = argv.index("--resample")
        method = argv[idx + 1].strip().lower()

    if method != DEFAULT_RESAMPLE_METHOD:
        raise ValueError(f"Unsupported --resample value: {method!r}. Supported: {DEFAULT_RESAMPLE_METHOD!r}.")

    sample_size = None
    if "--resample-size" in argv:
        idx = argv.index("--resample-size")
        sample_size = int(argv[idx + 1])

    sample_fraction = None
    if "--resample-fraction" in argv:
        idx = argv.index("--resample-fraction")
        sample_fraction = float(argv[idx + 1])

    if sample_size is not None and sample_fraction is not None:
        raise ValueError("Use either --resample-size or --resample-fraction, not both.")
    if sample_size is None and sample_fraction is None:
        raise ValueError("Resampling requires --resample-size or --resample-fraction.")
    if sample_size is not None and sample_size <= 0:
        raise ValueError("--resample-size must be a positive integer.")
    if sample_fraction is not None and not (0 < sample_fraction <= 1):
        raise ValueError("--resample-fraction must be in the interval (0, 1].")

    seed = DEFAULT_RESAMPLE_SEED
    if "--resample-seed" in argv:
        idx = argv.index("--resample-seed")
        seed = int(argv[idx + 1])

    return {
        "enabled": True,
        "method": method,
        "sample_size": sample_size,
        "sample_fraction": sample_fraction,
        "seed": seed,
    }


def resolve_resample_size(n_rows: int, resample_config: dict[str, Any]) -> int:
    sample_size = resample_config.get("sample_size")
    if sample_size is not None:
        k = int(sample_size)
    else:
        sample_fraction = float(resample_config["sample_fraction"])
        k = max(1, round(n_rows * sample_fraction))
    if k > n_rows:
        raise ValueError(f"Requested resample size {k} exceeds available rows {n_rows}.")
    return k


def get_resample_row_positions(n_rows: int, ticker: str, resample_config: dict[str, Any] | None) -> list[int] | None:
    if not resample_config:
        return None
    k = resolve_resample_size(n_rows, resample_config)
    payload = (
        f"{resample_config['seed']}|{resample_config['method']}|{ticker}|{n_rows}|"
        f"{resample_config['sample_size']}|{resample_config['sample_fraction']}"
    )
    derived_seed = int.from_bytes(hashlib.sha256(payload.encode("utf-8")).digest()[:8], "big")
    rng = random.Random(derived_seed)
    return sorted(rng.sample(range(n_rows), k))


try:
    RESAMPLE_CONFIG = parse_resample_cli(args)
except ValueError as exc:
    print(f"error: {exc}", file=sys.stderr)
    raise SystemExit(2) from exc

if HAS_CONFIG:
    from config import (  # type: ignore[no-redef]
        DATA_DIR,
        INDICATOR_CONFIG,
        PERIOD_LABELS,
        PERIODS,
        RESULTS_DIR,
        TICKERS,
        snapshot,
    )

    from indicator_config import ensure_columns, unwrap_configured
else:
    DATA_DIR = "tests/data"
    RESULTS_DIR = "tests/results"
    TICKERS = ["AAPL", "MSFT", "GOOGL"]
    PERIODS = [3, 5, 7, 10, 14, 20, 30, 45, 60, 120]
    PERIOD_LABELS = {
        3: "3d-micro",
        5: "5d-week",
        7: "7d-week+",
        10: "10d-fortnight",
        14: "14d-halfmonth",
        20: "20d-month",
        30: "30d-month+",
        45: "45d-midquarter",
        60: "60d-quarter",
        120: "120d-halfyear",
    }

    def snapshot(resample_config=None):
        return {"tickers": TICKERS, "periods": PERIODS, "resample": resample_config}


# ── detect library ────────────────────────────────────────────
if force_lib == "pandas":
    import pandas as _pd

    LIB, LIB_VERSION = "pandas", _pd.__version__
elif force_lib == "polars":
    import polars as _pl

    LIB, LIB_VERSION = "polars", _pl.__version__
else:
    try:
        import polars as _pl

        LIB, LIB_VERSION = "polars", _pl.__version__
    except ImportError:
        import pandas as _pd

        LIB, LIB_VERSION = "pandas", _pd.__version__

if LIB == "polars":
    import polars as pl

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
else:
    import pandas as pd

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
    """Return sorted list of module names for all indicators."""
    indicators = []
    for d in FEATURE_DIRS:
        if not os.path.isdir(os.path.join(PROJECT_ROOT, d)):
            continue
        for f in sorted(os.listdir(os.path.join(PROJECT_ROOT, d))):
            if f.endswith(".py") and f != "__init__.py":
                indicators.append(f"{d}.{f[:-3]}")
    return indicators


def run_one(task: dict) -> dict:
    """Run a single (ticker, indicator, period) combination."""
    ticker = task["ticker"]
    mod_name = task["mod_name"]
    n = task["n"]
    ind_name = task["ind_name"]
    factor_name = f"test_{ind_name}_{n}"

    csv_path = os.path.join(DATA_DIR, f"{ticker}.csv")
    if not os.path.exists(csv_path):
        return {
            "ticker": ticker,
            "indicator": ind_name,
            "module": mod_name,
            "period": n,
            "period_label": PERIOD_LABELS.get(n, str(n)),
            "factor_name": factor_name,
            "status": "error",
            "n_rows": "",
            "runtime_ms": "",
            "mean": "",
            "std": "",
            "min": "",
            "max": "",
            "nan_count": "",
            "nan_pct": "",
            "error": f"no data file: {csv_path}",
        }

    try:
        base_df = load_csv(csv_path)
        n_rows, _ = df_shape(base_df)
        positions = get_resample_row_positions(n_rows, ticker, RESAMPLE_CONFIG)
        if positions is not None:
            base_df = df_take_rows(base_df, positions)
        df = df_clone(base_df)

        if HAS_CONFIG:
            df = ensure_columns(df, INDICATOR_CONFIG)

        mod = importlib.import_module(mod_name)
        t0 = time.perf_counter()

        if HAS_CONFIG:
            result = mod.signal(df, n, factor_name, INDICATOR_CONFIG)
            result = unwrap_configured(result)
        else:
            result = mod.signal(df, n, factor_name)

        runtime_ms = (time.perf_counter() - t0) * 1000

        if factor_name not in result.columns:
            return {
                "ticker": ticker,
                "indicator": ind_name,
                "module": mod_name,
                "period": n,
                "period_label": PERIOD_LABELS.get(n, str(n)),
                "factor_name": factor_name,
                "status": "error",
                "n_rows": "",
                "runtime_ms": "",
                "mean": "",
                "std": "",
                "min": "",
                "max": "",
                "nan_count": "",
                "nan_pct": "",
                "error": f"column '{factor_name}' not in result",
            }

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
        return {
            "ticker": ticker,
            "indicator": ind_name,
            "module": mod_name,
            "period": n,
            "period_label": PERIOD_LABELS.get(n, str(n)),
            "factor_name": factor_name,
            "status": "error",
            "n_rows": "",
            "runtime_ms": "",
            "mean": "",
            "std": "",
            "min": "",
            "max": "",
            "nan_count": "",
            "nan_pct": "",
            "error": str(e)[:200],
        }


def main():
    global output_path
    os.makedirs(RESULTS_DIR, exist_ok=True)

    indicators = discover_indicators()
    print(f"Library:  {LIB} {LIB_VERSION}")
    print(f"Branch:   {'config' if HAS_CONFIG else 'master'}")
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

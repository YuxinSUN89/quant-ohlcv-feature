"""
Shared configuration for the test suite.

Edit TICKERS to change which symbols are tested.
All other scripts read config from here.
"""

from __future__ import annotations

import hashlib
import random
import sys
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from indicator_config import IndicatorConfig  # noqa: E402

# ── indicator numerical defaults ─────────────────────────────
INDICATOR_CONFIG = IndicatorConfig(min_periods=1, ddof=0, ewm_adjust=True)

# ── configurable ──────────────────────────────────────────────
TICKERS = [
    "AAPL",
    "ABBV",
    "AMGN",
    "AMT",
    "AMZN",
    "APD",
    "AXP",
    "BA",
    "BAC",
    "BLK",
    "BTC-USD",
    "CAT",
    "COP",
    "COST",
    "CVX",
    "DE",
    "DUK",
    "GE",
    "GLD",
    "GOOGL",
    "GS",
    "HD",
    "HON",
    "JNJ",
    "JPM",
    "KO",
    "LIN",
    "LLY",
    "MCD",
    "META",
    "MRK",
    "MS",
    "MSFT",
    "NEE",
    "NEM",
    "NFLX",
    "NKE",
    "NVDA",
    "OXY",
    "PEP",
    "PFE",
    "PG",
    "PLD",
    "SBUX",
    "SCHW",
    "SHW",
    "SLB",
    "T",
    "TGT",
    "TLT",
    "TSLA",
    "UNH",
    "UNP",
    "VZ",
    "WMT",
    "XOM",
]

# 10 years of daily data
PERIOD = "10y"
INTERVAL = "1d"

# 10 lookback periods: short-term → long-term
PERIODS = [3, 5, 7, 10, 14, 20, 30, 45, 60, 120]

# Labels for readability in reports
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

DATA_DIR = "tests/data"
RESULTS_DIR = "tests/results"

DEFAULT_RESAMPLE_METHOD = "subset_no_replacement_sorted"
DEFAULT_RESAMPLE_SEED = 42


def parse_resample_cli(args: Sequence[str]) -> dict[str, Any] | None:
    """Parse optional deterministic resampling flags from CLI args.

    Supported flags:
      --resample <method>
      --resample-size <int>
      --resample-fraction <float>
      --resample-seed <int>

    Resampling is disabled by default. When enabled, rows are sampled without
    replacement and then restored to chronological order so time-series logic
    still sees ascending timestamps.
    """
    wants_resample = any(
        flag in args for flag in ("--resample", "--resample-size", "--resample-fraction", "--resample-seed")
    )
    if not wants_resample:
        return None

    method = DEFAULT_RESAMPLE_METHOD
    if "--resample" in args:
        idx = args.index("--resample")
        method = args[idx + 1].strip().lower()

    if method != DEFAULT_RESAMPLE_METHOD:
        raise ValueError(f"Unsupported --resample value: {method!r}. Supported: {DEFAULT_RESAMPLE_METHOD!r}.")

    sample_size = None
    if "--resample-size" in args:
        idx = args.index("--resample-size")
        sample_size = int(args[idx + 1])

    sample_fraction = None
    if "--resample-fraction" in args:
        idx = args.index("--resample-fraction")
        sample_fraction = float(args[idx + 1])

    if sample_size is not None and sample_fraction is not None:
        raise ValueError("Use either --resample-size or --resample-fraction, not both.")
    if sample_size is None and sample_fraction is None:
        raise ValueError("Resampling requires --resample-size or --resample-fraction.")
    if sample_size is not None and sample_size <= 0:
        raise ValueError("--resample-size must be a positive integer.")
    if sample_fraction is not None and not (0 < sample_fraction <= 1):
        raise ValueError("--resample-fraction must be in the interval (0, 1].")

    seed = DEFAULT_RESAMPLE_SEED
    if "--resample-seed" in args:
        idx = args.index("--resample-seed")
        seed = int(args[idx + 1])

    return {
        "enabled": True,
        "method": method,
        "sample_size": sample_size,
        "sample_fraction": sample_fraction,
        "seed": seed,
    }


def resolve_resample_size(n_rows: int, resample_config: dict[str, Any]) -> int:
    """Resolve the requested sample size for a dataset with n_rows rows."""
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
    """Return deterministic row positions for seeded resampling.

    The same seed, ticker, row count, and sampling spec produce the same row
    positions across branches and libraries.
    """
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


def snapshot(resample_config: dict[str, Any] | None = None):
    """Return a JSON-serializable dict of the full config for reproducibility."""
    return {
        "tickers": TICKERS,
        "period": PERIOD,
        "interval": INTERVAL,
        "periods": PERIODS,
        "period_labels": PERIOD_LABELS,
        "data_dir": DATA_DIR,
        "results_dir": RESULTS_DIR,
        "num_param_sets": len(PERIODS),
        "indicator_config": INDICATOR_CONFIG.snapshot(),
        "resample": resample_config,
    }

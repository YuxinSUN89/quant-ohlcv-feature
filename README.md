# quant-ohlcv-features

A modular library of **335+ technical indicator implementations** for quantitative feature engineering on OHLCV (Open, High, Low, Close, Volume) financial data. Designed for use in machine learning pipelines for cryptocurrency and equity markets.

---

## Overview

Each feature is implemented as a standalone Python function with a uniform `signal(df, n, factor_name, config)` signature. The library provides two parallel implementations — **polars** and **pandas** — housed in `impl_polars/` and `impl_pandas/` respectively. A shared `IndicatorConfig` controls numerical defaults (epsilon, min_periods, ddof, etc.) across both.

Seven categories of technical signals are covered in each implementation:

| Category | Files | Description |
|---|---|---|
| `momentum_feature/` | 121 | Rate of change, oscillators, divergence signals |
| `trend_feature/` | 67 | Moving averages, directional indicators, regression trends |
| `volatility_feature/` | 72 | Bands, channels, range-based uncertainty metrics |
| `volume_feature/` | 51 | Accumulation, flow, buying/selling pressure |
| `price_feature/` | 9 | VWAP, typical price, weighted close |
| `liquidity_feature/` | 4 | Market microstructure and illiquidity proxies |
| `composite_feature/` | 11 | Multi-factor combinations across categories |

---

## Input Data Format

All indicators expect a polars or pandas DataFrame (matching the chosen implementation) with the following columns:

| Column | Type | Description |
|---|---|---|
| `open` | float | Bar open price |
| `high` | float | Bar high price |
| `low` | float | Bar low price |
| `close` | float | Bar close price |
| `volume` | float | Base asset volume |
| `quote_volume` | float | Quote asset volume (used in some indicators) |
| `taker_buy_quote_asset_volume` | float | Taker buy volume (used in composite features) |

A sample dataset is provided at [`data/btcusd_data.csv`](data/btcusd_data.csv) (Bitcoin/USD historical OHLCV, ~6.5 MB).

---

## Usage

Every feature file exports a `signal(df, n, factor_name, config)` function with a consistent signature:

| Argument | Description |
|---|---|
| `df` | Input DataFrame with OHLCV columns (polars or pandas) |
| `n` | Lookback period (integer) |
| `factor_name` | Name of the output column to write into `df` |
| `config` | `IndicatorConfig` instance controlling numerical defaults |

**Example (polars):**

```python
import polars as pl
from impl_polars.momentum_feature.Rsi import signal as rsi
from indicator_config import IndicatorConfig

config = IndicatorConfig(min_periods=1, ddof=0, ewm_adjust=True)
df = pl.read_csv("data/btcusd_data.csv")
df = rsi(df, n=14, factor_name="rsi_14", config=config)

print(df.select("close", "rsi_14").tail())
```

**Example (pandas):**

```python
import pandas as pd
from impl_pandas.momentum_feature.Rsi import signal as rsi
from indicator_config import IndicatorConfig

config = IndicatorConfig(min_periods=1, ddof=0, ewm_adjust=True)
df = pd.read_csv("data/btcusd_data.csv", index_col=0)
df = rsi(df, n=14, factor_name="rsi_14", config=config)

print(df[["close", "rsi_14"]].tail())
```

Intermediate calculation columns are cleaned up before returning — only `factor_name` is added to the DataFrame.

---

## Test Suite

Run the parallel test suite with `--impl` selecting the implementation:

```bash
# Test polars indicators
python tests/run_suite_parallel.py --impl polars

# Test pandas indicators
python tests/run_suite_parallel.py --impl pandas

# With resampling (deterministic subset)
python tests/run_suite_parallel.py --impl polars --resample-fraction 0.6 --resample-seed 42

# Compare results
python tests/compare.py tests/results/polars.csv tests/results/pandas.csv
```

### CLI Options

| Flag | Description |
|---|---|
| `--impl polars\|pandas` | **(required)** Which implementation to test |
| `--output PATH` | Output CSV path (auto-generated if omitted) |
| `--workers N` | Max parallel workers (default: min(32, cpu_count)) |
| `--resample-fraction F` | Resample input data to fraction F ∈ (0, 1] |
| `--resample-size N` | Resample to exactly N rows |
| `--resample-seed S` | Seed for deterministic resampling (default: 42) |

---

## IndicatorConfig

Shared numerical defaults live in `indicator_config.py`:

```python
@dataclass(frozen=True)
class IndicatorConfig:
    min_periods: Optional[int] = None   # rolling window min_periods
    ddof: int = 1                        # delta degrees of freedom for std
    ewm_adjust: bool = True              # ewm adjust parameter
    eps: float = 1e-8                    # division-by-zero floor
    normalize_eps: float = config.normalized_eps          # normalization epsilon
```

---

## Feature Categories

### Momentum (`momentum_feature/`)

Measures the rate and strength of price change. Useful for identifying overbought/oversold conditions and mean-reversion opportunities.

Key indicators:
- **RSI variants** (`Rsi.py`, `Rsimean.py`, `Rsih.py`, `Rsiv.py`) — Relative Strength Index with smoothing and variant logic
- **MACD variants** (`Macd.py`, `Macd_v2.py`, `MacdVol.py`, `Zlmacd.py`) — Trend-momentum crossover signals
- **Stochastic** (`Skdj.py`, `KdjK.py`, `KdjD.py`, `KdjJ.py`) — Stochastic oscillator components
- **Bias** (`Bias.py`, `BiasVol.py`, `Rbias.py`, `TmaBias.py`) — Price deviation from moving average
- **CCI** (`Cci.py`, `CciMagic.py`, `MagicCci.py`) — Commodity Channel Index variants
- **ROC / PPO** (`Roc.py`, `RocVol.py`, `Sroc.py`, `Ppo.py`) — Rate of change and percentage oscillators
- **MTM** (`Mtm.py`, `MtmMax.py`, `MtmMean.py`, `MtmBull.py`, `MtmBear.py`) — Momentum aggregates

---

### Trend (`trend_feature/`)

Identifies directional bias and trend persistence. Includes adaptive averages that self-adjust to market conditions.

Key indicators:
- **Moving averages** (`Ma.py`, `Dema.py`, `Tema.py`, `Tma.py`, `Hma.py`, `T3.py`)
- **Adaptive MAs** (`Kama.py`, `Vidya.py`) — Kaufman AMA and variable-index dynamic average
- **ADX system** (`Adx.py`, `AdxDi+.py`, `AdxDi-.py`, `Adxr.py`)
- **Regression trends** (`Reg.py`, `RegEma.py`, `RegTema.py`, `Mreg.py`)

---

### Volatility (`volatility_feature/`)

Measures price uncertainty and range expansion. Used for position sizing, breakout detection, and regime identification.

Key indicators:
- **Bollinger Bands** (`Bolling.py`, `BollingWidth.py`, `Bolling_fancy.py`)
- **ATR** (`Atr.py`, `AtrPct.py`, `AtrUpper.py`, `AtrLower.py`)
- **Keltner Channel** (`KcUpper.py`, `KcLower.py`, `KcSignal.py`)
- **Donchian Channel** (`Dc.py`, `DcSignal.py`)
- **Fibonacci Bands** (`FbUpper.py`, `FbLower.py`)

---

### Volume (`volume_feature/`)

Tracks accumulation, distribution, and the balance between buying and selling pressure.

Key indicators:
- **OBV / AD** (`Obv.py`, `Adosc.py`)
- **CMF / MFI** (`Cmf.py`, `Mfi.py`)
- **Force / EMV** (`Fi.py`, `Emv.py`)
- **PVT** (`Pvt.py`, `Pvt_v2.py`, `Pvt_v3.py`)
- **Taker ratios** (`TakerByRatio.py`, `TakerByRatioPerTrade.py`)

---

### Price (`price_feature/`)

Derived from raw OHLC prices, providing normalized reference levels.

| File | Description |
|---|---|
| `Vwap.py` | Volume-Weighted Average Price (CLV-adjusted) |
| `VwapSignal.py` | VWAP signal line |
| `Typ.py` | Typical price: `(HIGH + LOW + CLOSE) / 3` |
| `Wc.py` | Weighted close: `(HIGH + 2×CLOSE + LOW) / 4` |

---

### Liquidity (`liquidity_feature/`)

Microstructure features capturing trade execution efficiency and market depth.

| File | Description |
|---|---|
| `Amihud.py` | Amihud illiquidity ratio |
| `Liquidity_v3.py` | General liquidity proxy v3 |
| `MarketPl.py` | Market placement metric |
| `MarketPl_v2.py` | Market placement metric v2 |

---

### Composite (`composite_feature/`)

Multi-factor signals combining signals across categories for stronger predictive features.

| File | Description |
|---|---|
| `Damaov10.py` | Momentum × Volatility × ATR composite |
| `Msbt.py` | Momentum × Std-Momentum × BBW × Taker-Buy |
| `Adx+mtm.py` | ADX + Momentum combination (bullish) |
| `Adx-mtm.py` | ADX + Momentum combination (bearish) |
| `FearGreed_Yidai_v1.py` | Sentiment-style composite |
| `PriceVolumeResist.py` | Price-volume resistance level |

---

## Setup

Install dependencies with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

> **Note:** TA-Lib requires the underlying C library before `pip install` will work:
> - macOS: `brew install ta-lib`
> - Ubuntu/Debian: `apt-get install libta-lib-dev`
> - Windows: use the pre-built wheel from [ta-lib-python releases](https://github.com/TA-Lib/ta-lib-python/releases)

---

## Design Principles

- **Self-contained**: Each indicator file is an independent module with no cross-file imports (except shared helpers).
- **Uniform interface**: All indicators share the `signal(df, n, factor_name, config)` signature.
- **Dual implementation**: Polars-native and pandas-native versions live side-by-side, sharing a single `IndicatorConfig`.
- **Config-driven defaults**: Epsilon, min_periods, ddof, and ewm_adjust flow from `IndicatorConfig` — no hardcoded numeric defaults.
- **Side-effect-free cleanup**: Intermediate columns created during calculation are deleted before returning `df`.
- **Division-by-zero safety**: A small epsilon (`config.eps`) is applied wherever denominators may be zero.
- **Relative outputs**: Most indicators produce normalized or ratio-based outputs to avoid scale mismatch in downstream models.

---

## Repository Structure

```
quant-ohlcv-features/
├── indicator_config.py          # Shared config (IndicatorConfig dataclass)
├── impl_polars/                 # Polars-native implementation
│   ├── helpers.py
│   ├── momentum_feature/
│   ├── trend_feature/
│   ├── volatility_feature/
│   ├── volume_feature/
│   ├── price_feature/
│   ├── liquidity_feature/
│   └── composite_feature/
├── impl_pandas/                 # Pandas-native implementation
│   ├── helpers.py
│   ├── bug_docs/               # Pandas-specific bug fix reports
│   ├── momentum_feature/
│   ├── trend_feature/
│   ├── volatility_feature/
│   ├── volume_feature/
│   ├── price_feature/
│   ├── liquidity_feature/
│   └── composite_feature/
├── tests/
│   ├── config.py               # Test configuration (tickers, periods, resampling)
│   ├── run_suite_parallel.py   # Parallel test runner (--impl polars|pandas)
│   ├── compare.py              # Cross-result comparison tool
│   └── download_data.py        # Download OHLCV data via yfinance
└── data/
    └── btcusd_data.csv          # Sample BTC/USD OHLCV data
```

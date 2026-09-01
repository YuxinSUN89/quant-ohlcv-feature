# quant-ohlcv-features

A modular library of **540+ technical indicator implementations** for quantitative feature engineering on OHLCV (Open, High, Low, Close, Volume) financial data. Designed for use in machine learning pipelines for cryptocurrency and equity markets.

---

## Overview

Each feature is implemented as a standalone Python function that accepts a pandas DataFrame and returns it with the computed indicator appended as a new column. The library covers seven categories of technical signals:

| Category | Files | Description |
|---|---|---|
| `momentum_feature/` | 240 | Rate of change, oscillators, divergence signals |
| `trend_feature/` | 73 | Moving averages, directional indicators, regression trends |
| `volatility_feature/` | 107 | Bands, channels, range-based uncertainty metrics |
| `volume_feature/` | 82 | Accumulation, flow, buying/selling pressure |
| `price_feature/` | 19 | VWAP, typical price, weighted close |
| `liquidity_feature/` | 8 | Market microstructure and illiquidity proxies |
| `composite_feature/` | 11 | Multi-factor combinations across categories |

---

## Input Data Format

All indicators expect a pandas DataFrame with the following columns:

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

Every feature file exports a single `signal(*args)` function with a consistent signature:

```python
df = signal(df, n, factor_name)
```

| Argument | Description |
|---|---|
| `df` | Input DataFrame with OHLCV columns |
| `n` | Lookback period (integer) |
| `factor_name` | Name of the output column to write into `df` |

**Example:**

```python
import pandas as pd
from momentum_feature.Rsi import signal as rsi

df = pd.read_csv("data/btcusd_data.csv")
df = rsi(df, n=14, factor_name="rsi_14")

print(df[["close", "rsi_14"]].tail())
```

Intermediate calculation columns are cleaned up before returning — only `factor_name` is added to the DataFrame.

---

## Feature Categories

### Momentum (`momentum_feature/`)

Measures the rate and strength of price change. Useful for identifying overbought/oversold conditions and mean-reversion opportunities.

Key indicators:
- **RSI variants** (`Rsi.py`, `Rsimean.py`, `Rsih.py`, `Rsiv.py`, `Rsij.py`) — Relative Strength Index with smoothing and variant logic
- **MACD variants** (`Macd.py`, `Macd_v2.py`, `MacdVol.py`, `Zlmacd.py`) — Trend-momentum crossover signals
- **Stochastic** (`Skdj.py`, `KdjK.py`, `KdjD.py`, `KdjJ.py`) — Stochastic oscillator components
- **Bias** (`Bias.py`, `BiasVol.py`, `Rbias.py`, `TmaBias.py`) — Price deviation from moving average
- **CCI** (`Cci.py`, `CciMagic.py`, `MagicCci.py`) — Commodity Channel Index variants
- **ROC / PPO** (`Roc.py`, `RocVol.py`, `Sroc.py`, `Ppo.py`) — Rate of change and percentage oscillators
- **MTM** (`Mtm.py`, `MtmMax.py`, `MtmMean.py`, `MtmBull.py`, `MtmBear.py`) — Momentum aggregates
- **DBCD** (`Dbcd.py`, `Dbcd_v2.py`, `Dbcd_taker.py`) — Divergence-based momentum
- **Other** — CMO, Fisher Transform, KST, DPO, Coppock Curve
- **Recently added** — MA-deviation oscillators (`G31.py`, `G34.py`, `G65.py`, `G66.py`, `G71.py`), anchored-reversal factors (`AncRet.py`, `AncReverse.py`), win-rate / Sharpe-style return stats (`WinRate.py`, `Sharpe.py`), and ~100 more numbered alpha-style oscillators (`G*.py`, `H*.py`) ported from a broader factor reference and restricted to pure OHLCV formulas

---

### Trend (`trend_feature/`)

Identifies directional bias and trend persistence. Includes adaptive averages that self-adjust to market conditions.

Key indicators:
- **Moving averages** (`Ma.py`, `Dema.py`, `Tema.py`, `Tma.py`, `Hma.py`, `T3.py`) — Simple, double, triple, hull, and T3 MAs
- **Adaptive MAs** (`Kama.py`, `Vidya.py`) — Kaufman AMA and variable-index dynamic average
- **ADX system** (`Adx.py`, `AdxDi+.py`, `AdxDi-.py`, `Adxr.py`) — Average Directional Index components
- **Regression trends** (`Reg.py`, `RegEma.py`, `RegTema.py`, `Mreg.py`) — Linear regression-based trend lines
- **Ichimoku** (`Ic.py`, `Ic_v2.py`, `Ic_v3.py`, `Ic_v4.py`) — Cloud indicator components
- **Signals** (`MaSignal.py`, `HmaSignal.py`) — Trend confirmation signals
- **Other** — Aroon, BBI, MAC, Gapped trend, CSE
- **Recently added** — DI-ratio directional-movement factors (`G172.py`, `G173.py`), regression-slope of a smoothed MA (`G21.py`), bottom-fractal pattern (`BottomFractal.py`), control-dominance factor (`StableControlPower.py`)

---

### Volatility (`volatility_feature/`)

Measures price uncertainty and range expansion. Used for position sizing, breakout detection, and regime identification.

Key indicators:
- **Bollinger Bands** (`Bolling.py`, `BollingWidth.py`, `Bolling_fancy.py`) — Standard deviation channels
- **ATR** (`Atr.py`, `AtrPct.py`, `AtrUpper.py`, `AtrLower.py`) — Average True Range and derived bands
- **Keltner Channel** (`KcUpper.py`, `KcLower.py`, `KcSignal.py`) — ATR-based envelope
- **Donchian Channel** (`Dc.py`, `DcSignal.py`) — High/low breakout bands
- **Fibonacci Bands** (`FbUpper.py`, `FbLower.py`) — Golden ratio volatility levels
- **APZ** (`Apz.py`, `ApzUpper.py`, `ApzLower.py`) — Adaptive Price Zone
- **PAC** (`Pac.py`, `PacUpper.py`, `PacLower.py`) — Price Acceleration Channel
- **Envelope** (`EnvUpper.py`, `EnvLower.py`, `EnvSignal.py`) — Percentage-based envelope
- **Other** — VIX-inspired bandwidth, PFE, MSSI, historical volatility, volume/change standard deviation
- **Recently added** — amplitude family (`Amplitude.py`, `AmplitudeBear.py`, `AmplitudeBull.py`, `AmplitudeStd.py`), candle-shadow ratios (`UpperShadow.py`, `LowerShadow.py`), gap standard deviation (`GapStdN.py`), plus ~20 more true-range / rolling-std alpha factors (`G*.py`, `H101.py`)

---

### Volume (`volume_feature/`)

Tracks accumulation, distribution, and the balance between buying and selling pressure.

Key indicators:
- **OBV / AD** (`Obv.py`, `Adosc.py`) — On-Balance Volume and A/D oscillator
- **CMF / MFI** (`Cmf.py`, `Mfi.py`) — Chaikin Money Flow and Money Flow Index
- **Force / EMV** (`Fi.py`, `Emv.py`) — Force Index and Ease of Movement
- **PVT** (`Pvt.py`, `Pvt_v2.py`, `Pvt_v3.py`) — Price-Volume Trend
- **Taker ratios** (`TakerByRatio.py`, `TakerByRatioPerTrade.py`) — Aggressive buyer/seller ratio
- **Volume rate of change** (`Pvo.py`) — Volume momentum
- **WAD / WVAD** (`Wad.py`, `Wvad.py`) — Williams Accumulation/Distribution
- **V1 variants** (`V1.py`, `V1Up.py`, `V1Dn.py`) — Directional volume components
- **Fancy features** (`BuyVolRatio_fancy.py`, `NetVol_fancy.py`, `UpNum_fancy.py`, `VolPerTrade_fancy.py`)
- **Recently added** — volume-ratio family (`VolRatio.py`, `UpVolRatio.py`, `DownVolRatio.py`, `VolumeAvgRatio.py`), volume-weighted price MAs (`Amv01.py`, `CostPriceMa.py`), turnover-shrink factors (`VolumeShrink.py`, `AmountShrinkVol.py`), price-volume correlation (`Corr.py`), plus ~20 more volume-driven alpha factors (`G*.py`, `H21.py`, `VBoll.py`)

---

### Price (`price_feature/`)

Derived from raw OHLC prices, providing normalized reference levels.

| File | Description |
|---|---|
| `Vwap.py` | Volume-Weighted Average Price (CLV-adjusted) |
| `VwapSignal.py` | VWAP signal line |
| `Vwapbias.py` | Price deviation from VWAP |
| `AvgPrice.py` | Volume-weighted average price normalization |
| `Typ.py` | Typical price: `(HIGH + LOW + CLOSE) / 3` |
| `Wc.py` | Weighted close: `(HIGH + 2×CLOSE + LOW) / 4` |
| `AvgPriceToHigh.py` | Price position relative to session high |
| `AvgPriceToLow.py` | Price position relative to session low |
| `LowPrice.py` | Low price derived metric |
| `MaHigh.py` / `MaLow.py` | Moving average of the session high / low |
| `PctFromNDayHigh.py` | Distance from the highest price of the prior N days |
| `BreakNDayHigh.py` | Whether price broke the prior N-day high |
| `MaxDrawdown.py` | Current close relative to its N-day rolling peak (drawdown) |
| `PricePercentile.py` | Rolling percentile rank of the current price |
| *(+5 more)* | See `price_feature/` for the full list |

---

### Liquidity (`liquidity_feature/`)

Microstructure features capturing trade execution efficiency and market depth.

| File | Description |
|---|---|
| `Amihud.py` | Amihud illiquidity ratio — quote volume per unit of intraday price path |
| `Liquidity_v3.py` | General liquidity proxy v3 |
| `MarketPl.py` | Market placement metric |
| `MarketPl_v2.py` | Market placement metric v2 |
| `Illiquidity.py` | Illiquidity ratio — quote volume per unit of intraday price path (alternate formulation) |
| `LiquidityPctChgMean.py` / `LiquidityPctChgStd.py` | Quote volume per unit of price change — mean / std over N days |

**Amihud formula:**

```
ROUTE1 = 2*(HIGH - LOW) + (OPEN - CLOSE)
ROUTE2 = 2*(HIGH - LOW) + (CLOSE - OPEN)
SHORTEST_PATH = MIN(ROUTE1, ROUTE2)
NORM_PATH = SHORTEST_PATH / OPEN
LIQUIDITY_PREMIUM = QUOTE_VOLUME / NORM_PATH
result = MA(LIQUIDITY_PREMIUM, N)
```

Higher values indicate greater liquidity (more volume per unit of price movement).

---

### Composite (`composite_feature/`)

Multi-factor signals combining signals across categories for stronger predictive features.

| File | Description |
|---|---|
| `Damaov10.py` | Momentum × Volatility × ATR composite |
| `Msbt.py` | Momentum × Std-Momentum × BBW × Taker-Buy |
| `Adx+mtm.py` | ADX + Momentum combination (bullish) |
| `Adx-mtm.py` | ADX + Momentum combination (bearish) |
| `CoppAtrBull.py` | Coppock Curve × ATR momentum-volatility |
| `Fbnq_pct_v5.py` | Fibonacci-based composite |
| `FearGreed_Yidai_v1.py` | Sentiment-style composite |
| `PriceVolumeResist.py` | Price-volume resistance level |
| `Pmarp_Yidai_v1.py` | Proprietary multi-factor signal |
| `Cbr_v1.py` | Custom multi-factor signal |
| `Cvr_v0.py` | Volatility-ratio composite |

---

## Dependencies

Install all dependencies with:

```bash
pip install -r requirements.txt
```

> **Note:** TA-Lib requires the underlying C library before `pip install` will work:
> - macOS: `brew install ta-lib`
> - Ubuntu/Debian: `apt-get install libta-lib-dev`
> - Windows: use the pre-built wheel from [ta-lib-python releases](https://github.com/TA-Lib/ta-lib-python/releases)

Each indicator file is self-contained with no cross-file imports.

---

## Design Principles

- **Self-contained**: Each file is an independent module with no dependencies on other feature files.
- **Uniform interface**: All indicators share the same `signal(df, n, factor_name)` signature, making them easy to iterate over in a pipeline.
- **Side-effect-free cleanup**: Intermediate columns created during calculation are deleted before returning `df`.
- **Division-by-zero safety**: A small epsilon (`eps = 1e-8`) is applied wherever denominators may be zero.
- **Relative outputs**: Most indicators produce normalized or ratio-based outputs to avoid scale mismatch in downstream models.

---

## Repository Structure

```
quant-ohlcv-features/
├── data/
│   └── btcusd_data.csv          # Sample BTC/USD OHLCV data
├── momentum_feature/            # 240 momentum indicators
├── trend_feature/               # 73 trend indicators
├── volatility_feature/          # 107 volatility indicators
├── volume_feature/              # 82 volume indicators
├── price_feature/               # 19 price-derived indicators
├── liquidity_feature/           # 8 liquidity/microstructure indicators
└── composite_feature/           # 11 multi-factor composite signals
```

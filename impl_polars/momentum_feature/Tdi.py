import numpy as np
import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # ******************** TDI ********************
    # RSI_PriceLine=EMA(RSI,N2)
    # RSI_SignalLine=EMA(RSI,N3)
    # RSI_MarketLine=EMA(RSI,N4)
    # TDI is a technical indicator derived from RSI, including RSI price line, trade signal line, market baseline, etc.
    # Buy/sell signals are generated when the RSI price line simultaneously crosses above/below the trade signal line and market baseline.

    rtn = df["close"].diff()
    up = np.where(rtn > 0, rtn, 0)
    up = pl.Series(up).fill_nan(None)
    dn = np.where(rtn < 0, rtn.abs(), 0)
    dn = pl.Series(dn).fill_nan(None)
    a = pl.Series(up).rolling_sum(n, min_samples=config.min_periods)
    b = pl.Series(dn).rolling_sum(n, min_samples=config.min_periods)
    a *= 1e3
    b *= 1e3
    rsi = a / (config.normalize_eps + a + b)
    rsi_price_line = pl.Series(rsi).ewm_mean(span=n, adjust=config.ewm_adjust)
    rsi_signal_line = pl.Series(rsi).ewm_mean(span=int(2 * n), adjust=config.ewm_adjust)

    s = rsi_price_line - rsi_signal_line
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df

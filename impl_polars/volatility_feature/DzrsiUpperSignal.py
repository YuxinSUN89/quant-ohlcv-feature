import numpy as np
import polars as pl

from impl_polars.helpers import scale_01


def signal(df, n, factor_name, config):
    # DzrsiUpperSignal indicator (RSI half-period MA - RSI Bollinger Upper band, 0-1 normalized)
    # Formula: RSI = A / (A + B) where A=SUM(up_diff,N), B=SUM(down_diff,N)
    #          RSI_UPPER = MA(RSI,N) + 2*STD(RSI,N); RSI_MA = MA(RSI, N/2)
    #          result = scale_01(RSI_MA - RSI_UPPER, N, config.normalize_eps)
    # Measures how far the RSI half-period MA is below the RSI upper Bollinger band.
    # Low values indicate RSI is at or above the upper band (overbought conditions).
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

    rsi_middle = rsi.rolling_mean(n, min_samples=config.min_periods)
    rsi_upper = rsi_middle + 2 * rsi.rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)
    # rsi_lower = rsi_middle - 2 * rsi.rolling_std(n, min_samples=config.min_periods, ddof=config.ddof)
    rsi_ma = rsi.rolling_mean(int(n / 2), min_samples=config.min_periods)

    s = rsi_ma - rsi_upper
    df = df.with_columns(pl.Series(factor_name, scale_01(s, n, config.normalize_eps, config=config)))

    return df

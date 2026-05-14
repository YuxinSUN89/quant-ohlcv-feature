import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Rsis indicator (RSI normalized to its rolling min/max range)
    # Formula: RSI = 100 * EMA(up_diff, 4N) / EMA(|diff|, 4N) (smoothed via EWM)
    #          RSIS = 100 * (RSI - MIN(RSI, 4N)) / (MAX(RSI, 4N) - MIN(RSI, 4N))
    # Normalizes RSI to its historical [0, 100] range over 4N periods, improving cross-asset comparability.
    # Values near 100 indicate RSI is near its highest recent level; near 0 near its lowest.
    eps = config.eps
    close_diff_pos = np.where(df["close"] > df["close"].shift(1), df["close"] - df["close"].shift(1), 0)
    close_diff_pos = pl.Series(close_diff_pos).fill_nan(None)
    rsi_a = pl.Series(close_diff_pos).ewm_mean(alpha=1 / (4 * n), adjust=config.ewm_adjust)
    rsi_b = (df["close"] - df["close"].shift(1)).abs().ewm_mean(alpha=1 / (4 * n), adjust=config.ewm_adjust)
    rsi = 100 * rsi_a / (eps + rsi_b)
    rsi_min = pl.Series(rsi).rolling_min(int(4 * n), min_samples=config.min_periods)
    rsi_max = pl.Series(rsi).rolling_max(int(4 * n), min_samples=config.min_periods)
    rsis = 100 * (rsi - rsi_min) / (eps + rsi_max - rsi_min)
    df = df.with_columns(pl.Series(factor_name, rsis))

    return df

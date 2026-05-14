import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    # Rsi_v2 indicator (RSI using rolling sum instead of EWM)
    # Formula: A = SUM(MAX(DIFF,0), N); B = SUM(MAX(-DIFF,0), N)
    #          result = A / (A + B)
    # Standard RSI computed using rolling sum (Wilder-style but without EWM).
    # Range [0, 1]. Values above 0.7 indicate overbought; below 0.3 indicate oversold.
    eps = config.eps
    close_dif = df["close"].diff()
    df = df.with_columns(pl.Series("up", np.where(close_dif > 0, close_dif, 0)).fill_nan(None))
    df = df.with_columns(pl.Series("down", np.where(close_dif < 0, abs(close_dif), 0)).fill_nan(None))
    a = df["up"].rolling_sum(n, min_samples=config.min_periods)
    b = df["down"].rolling_sum(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series(factor_name, a / (a + b + eps)))

    # remove redundant columns
    df = df.drop(["up", "down"])

    return df

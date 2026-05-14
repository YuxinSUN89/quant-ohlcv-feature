import numpy as np
import polars as pl


def signal(df, n, factor_name, config):
    eps = config.eps
    # Rsimean indicator (Rolling mean of RSI)
    # Formula: RSI = A/(A+B) where A=SUM(up_diff,N), B=SUM(down_diff,N); result = MA(RSI, N)
    # Smooths RSI with a rolling mean to reduce whipsaws. Useful as a trend-following version of RSI.
    # Values above 0.5 indicate sustained buying pressure; below 0.5 indicate selling pressure.
    close_dif = df["close"].diff()
    df = df.with_columns(pl.Series("up", np.where(close_dif > 0, close_dif, 0)).fill_nan(None))
    df = df.with_columns(pl.Series("down", np.where(close_dif < 0, abs(close_dif), 0)).fill_nan(None))
    a = df["up"].rolling_sum(n, min_samples=config.min_periods)
    b = df["down"].rolling_sum(n, min_samples=config.min_periods)
    df = df.with_columns(pl.Series("rsi", a / (a + b + eps)))
    df = df.with_columns(pl.Series(factor_name, df["rsi"].rolling_mean(n, min_samples=config.min_periods)))

    # remove redundant columns
    df = df.drop(["up", "down", "rsi"])

    return df
